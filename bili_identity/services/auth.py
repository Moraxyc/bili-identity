import logging
from datetime import datetime, timezone
from typing import Literal

from bili_identity.config import get_config
from bili_identity.db import (
    AsyncSessionLocal,
    get_verification_code,
    mark_verified_to_session_id,
    save_verification_code,
)
from bili_identity.db.verifyction_code import clear_codes
from bili_identity.utils import generate_secret

from .user import register_user

logger = logging.getLogger(__name__)

config = get_config()


async def send_code(uid: int) -> None:
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


async def gen_passive_code(uid: int) -> str:
    # 确保用户一定存在
    await register_user(uid, anyway=True)

    code = generate_secret(length=32)
    async with AsyncSessionLocal() as db_session:
        await save_verification_code(
            uid, db_session, code=code, mode="passive"
        )
    return code


async def verify_code(
    uid: int, code: str, mode: Literal["active", "passive"]
) -> bool:
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
        record = await get_verification_code(uid, session, mode=mode)
        if not record:
            logger.warning(f"未找到验证码记录 uid={uid}")
            return False

        expires_at = record.expires_at
        current_at = datetime.now(timezone.utc)
        logger.debug(f"验证码过期时间: {expires_at}")

        # 判断验证码是否已过期
        if record.is_expired():
            logger.debug(f"验证码已过期, 当前{current_at}")
            return False

        # 验证输入的验证码是否匹配
        logger.debug(f"验证码: {record.code}")
        if not record.is_match(code):
            logger.debug(f"验证码不符合: {code}")
            return False

        logger.debug("验证通过")

        mark_verified_to_session_id(uid)

        return True


async def clear_all_codes_by_uid(uid: int) -> None:
    async with AsyncSessionLocal() as session:
        await clear_codes(session, uid)
    logger.debug(f"已清除所有uid为{uid}的验证码")
