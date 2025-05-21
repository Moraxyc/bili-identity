import logging
from typing import cast

from bili_identity.db import AsyncSessionLocal, get_user
from bili_identity.db.user import create_user, update_user

logger = logging.getLogger(__name__)


async def register_user(uid: int, anyway: bool = False, **kwargs) -> bool:
    """
    注册用户。如果用户已存在且未设置 `anyway=True`，则不执行注册。

    :param uid: 用户的B站UID
    :type uid: int
    :param anyway: 是否无视已有用户强制注册，默认为 False
    :type anyway: bool
    :param kwargs: 创建用户时传入的其他关键字参数，将传递给 `create_user`
    :type kwargs: dict
    :return: 注册是否成功。成功返回 True，失败返回 False
    :rtype: bool
    """
    async with AsyncSessionLocal() as session:
        if await get_user(uid, session) and not anyway:
            logger.warning(f"用户 {uid} 已存在，无法注册")
            return False
        return await create_user(uid, session, **kwargs) is not None


async def mark_user_as_verified(uid: int) -> bool:
    """
    将指定用户标记为已验证状态。

    :param uid: 要标记为已验证的用户 UID
    :type uid: int
    :return: 若更新成功则返回 True，否则返回 False
    :rtype: bool
    """
    async with AsyncSessionLocal() as session:
        result = await update_user(uid, session, is_verified=True)
        if result:
            return True
        logger.warning(f"无法更新用户 {uid} 状态为已验证")
        return False


async def is_user_verified(uid: int) -> bool:
    """
    判断用户在数据库中是否已经过验证。

    :param uid: 要标记验证的用户 UID
    :type uid: int
    :return: 若已验证则返回 True，否则返回 False
    :rtype: bool
    """
    async with AsyncSessionLocal() as session:
        user = await get_user(uid, session)
    if not user:
        return False

    return cast(bool, user.is_verified)
