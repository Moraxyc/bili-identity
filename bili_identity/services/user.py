import logging

from bili_identity.db import AsyncSessionLocal, create_user, get_user

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
        if await get_user(uid, session):
            if not anyway:
                logger.warning(f"用户 {uid} 已存在，无法注册")
            return False

        from bili_identity.core.bilibili import fetch_user_info

        user_info = await fetch_user_info(uid)
        nickname = user_info.get("name", None)
        avatar_url = user_info.get("face", None)

        return (
            await create_user(
                uid,
                session,
                nickname=nickname,
                avatar_url=avatar_url,
                **kwargs,
            )
            is not None
        )
