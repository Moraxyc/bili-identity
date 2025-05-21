import logging
from typing import Literal, Optional

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
    expire_minutes: int = 5,
    mode: Literal["active", "passive"] = "passive",
) -> bool:
    record = VerificationCode.create(
        uid=uid,
        code=code,
        expire_minutes=expire_minutes,
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
