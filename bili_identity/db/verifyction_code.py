import logging
from typing import Literal, Optional

from pydantic import NonNegativeFloat
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from bili_identity.config import get_config
from bili_identity.models import VerificationCode

logger = logging.getLogger(__name__)

config = get_config()


async def get_verification_code(
    uid: int,
    session: AsyncSession,
    mode: Literal["active", "passive"] = "active",
) -> Optional[VerificationCode]:
    result = await session.execute(
        select(VerificationCode).where(
            VerificationCode.uid == uid, VerificationCode.mode == mode
        )
    )
    return result.scalar_one_or_none()


async def save_verification_code(
    uid: int,
    session: AsyncSession,
    code: str,
    expire_ttl: int = config.security.code_ttl,
    mode: Literal["active", "passive"] = "passive",
) -> bool:
    record = VerificationCode.create(
        uid=uid,
        code=code,
        expire_ttl=expire_ttl,
        mode=mode,
    )

    try:
        await session.merge(record)
        await session.commit()
        logger.debug(f"验证码保存成功 uid={uid}, code={code}")
        return True
    except Exception as e:
        await session.rollback()
        logger.error(f"保存验证码失败 uid={uid}: {e}")
        return False


async def clear_codes(session: AsyncSession, uid: int) -> None:
    stmt = delete(VerificationCode).where(VerificationCode.uid == uid)
    await session.execute(stmt)
    await session.commit()
