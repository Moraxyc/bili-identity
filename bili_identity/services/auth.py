import logging
from datetime import datetime, timezone

from bili_identity.db import AsyncSessionLocal, get_verification_code

from .user import mark_user_as_verified, register_user

logger = logging.getLogger(__name__)


async def send_code(uid: int):
    """
    发送验证码给指定用户。

    :param uid: 用户的B站UID
    :type uid: int
    :return: 无返回值，操作完成后结束
    :rtype: None
    """
    from bili_identity.core.bilibili import send_verification_code

    # 确保用户一定存在
    await register_user(uid, anyway=True)

    await send_verification_code(uid)


async def verify_code(uid: int, code: str) -> bool:
    """
    验证用户提交的验证码是否有效，若验证成功则标记用户为已验证。

    :param uid: 用户的B站UID
    :type uid: int
    :param code: 用户提交的验证码
    :type code: str
    :return: 如果验证码存在、未过期且匹配，则返回 True，否则返回 False
    :rtype: bool
    """
    async with AsyncSessionLocal() as session:
        # 查询数据库中该用户的验证码记录
        record = await get_verification_code(uid, session)
        if not record:
            logger.warning(f"未找到验证码记录 uid={uid}")
            return False

        expires_at = record.expires_at
        current_at = datetime.now(timezone.utc)
        logger.debug(f"验证码过期时间: {expires_at}")

        # 确保过期时间是有时区信息的 datetime 对象
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        # 判断验证码是否已过期
        if expires_at < current_at:
            logger.debug(f"验证码已过期, 当前{current_at}")
            return False

        # 验证输入的验证码是否匹配
        logger.debug(f"验证码: {record.code}")
        if record.code != code:
            logger.debug(f"验证码不符合: {code}")
            return False

        logger.debug("验证通过")

        # 标记用户为已验证
        await mark_user_as_verified(uid)
        return True
