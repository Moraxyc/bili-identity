import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bili_identity.models import VerificationCode

logger = logging.getLogger(__name__)


async def get_verification_code(
    uid: int, session: AsyncSession
) -> Optional[VerificationCode]:
    result = await session.execute(
        select(VerificationCode).where(VerificationCode.uid == uid)
    )
    return result.scalar_one_or_none()


async def save_verification_code(
    uid: int,
    session: AsyncSession,
    code: str,
    expires_at: Optional[datetime] = None,
    mode: str = "active",
) -> bool:
    expires_at = expires_at or datetime.now(timezone.utc) + timedelta(minutes=5)

    record = VerificationCode(
        uid=uid,
        code=code,
        expires_at=expires_at,
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
