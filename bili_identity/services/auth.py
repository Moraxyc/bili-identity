import logging
from datetime import datetime, timezone

from bili_identity.db import AsyncSessionLocal, get_verifiction_code

from .user import mark_user_as_verified, register_user

logger = logging.getLogger(__name__)


async def send_code(uid: int):
    from bili_identity.core.bilibili import send_verification_code

    await register_user(uid, anyway=True)

    await send_verification_code(uid)


async def verify_code(uid: int, code: str) -> bool:
    async with AsyncSessionLocal() as session:
        record = await get_verifiction_code(uid, session)
        if not record:
            logger.warning(f"未找到验证码记录 uid={uid}")
            return False

        expires_at = record.expires_at
        current_at = datetime.now(timezone.utc)
        logger.debug(f"验证码过期时间: {expires_at}")

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < current_at:
            logger.debug(f"验证码已过期, 当前{current_at}")
            return False

        logger.debug(f"验证码: {record.code}")
        if record.code != code:
            logger.debug(f"验证码不符合: {code}")
            return False

        logger.debug(f"验证通过")

        await mark_user_as_verified(uid)
        return True
