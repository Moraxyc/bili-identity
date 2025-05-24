import json
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence, cast

from jwcrypto import jwk
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bili_identity.models import JWKKey
from bili_identity.utils import generate_new_rs256

logger = logging.getLogger(__name__)


async def get_first_active_jwk(session: AsyncSession) -> jwk.JWK:
    await ensure_jwks(session)
    stmt = select(JWKKey).where(JWKKey.active)
    result = await session.execute(stmt)
    obj = result.scalars().first()
    # Cause ensure_jwks()
    return cast(JWKKey, obj).jwk


async def get_jwk(session: AsyncSession, kid: str) -> Optional[JWKKey]:
    result = await session.execute(select(JWKKey).where(JWKKey.kid == kid))
    return result.scalar_one_or_none()


async def list_jwks(
    session: AsyncSession, private_key: bool = False, active: bool = True
) -> List[dict]:
    """
    列出 JWK 密钥对象。
    """
    stmt = select(JWKKey).where(JWKKey.active) if active else select(JWKKey)
    result = await session.execute(stmt)
    keys = result.scalars().all()

    jwks = []
    for key in keys:
        jwks.append(key.key if private_key else key.pubkey)

    return jwks


async def revoke_jwk(session: AsyncSession, kid: str):
    """
    吊销某个kid
    """
    jwk = await get_jwk(session, kid)
    if jwk:
        jwk.active = False
        await session.commit()


async def save_new_jwk(session: AsyncSession) -> Optional[JWKKey]:
    jwk_dict: dict = generate_new_rs256()
    if not jwk_dict:
        logger.error("生成 JWK 失败")
        return None

    jwk_obj = JWKKey(
        kid=jwk_dict["kid"],
        content=json.dumps(jwk_dict),
        # Almost half an year
        expires_at=datetime.now(timezone.utc) + timedelta(days=180),
    )
    session.add(jwk_obj)

    try:
        await session.commit()
        return jwk_obj
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"存储JWK {jwk_obj.kid} 失败: {e}")
        return None


async def ensure_jwks(session: AsyncSession) -> None:
    stmt = select(JWKKey).where(JWKKey.active)
    result = await session.execute(stmt)
    active_keys: Sequence[JWKKey] = result.scalars().all()

    all_expires_soon = all(
        key.expires_soon(threshold_days=7) for key in active_keys
    )

    if all_expires_soon:
        await save_new_jwk(session)

        for key in active_keys:
            if key.expires_soon(threshold_days=0):
                await revoke_jwk(session, kid=key.kid)
