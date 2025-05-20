import logging

from bili_identity.db import AsyncSessionLocal, get_user
from bili_identity.db.user import create_user, update_user

logger = logging.getLogger(__name__)


async def register_user(uid: int, anyway: bool = False, **kwargs) -> bool:
    async with AsyncSessionLocal() as session:
        if await get_user(uid, session) and not anyway:
            logger.warning(f"用户 {uid} 已存在，无法注册")
            return False
        return await create_user(uid, session, **kwargs) is not None


async def mark_user_as_verified(uid: int) -> bool:
    async with AsyncSessionLocal() as session:
        result = await update_user(uid, session, is_verified=True)
        if result:
            return True
        logger.warning(f"无法更新用户 {uid} 状态为已验证")
        return False
