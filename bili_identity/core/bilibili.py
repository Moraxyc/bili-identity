from bili_identity.config import get_config
from bili_identity.db import AsyncSessionLocal, save_verification_code
from bili_identity.utils.random import generate_code


async def send_verification_code(uid: int):
    """
    向指定 UID 用户发送验证码，并将验证码保存到数据库中
    """
    code = generate_code()  # 生成随机6位验证码
    from bilibili_api import session

    # 使用 B 站 API 发送验证码消息
    config = get_config()
    await session.send_msg(
        config.credential,
        uid,
        session.EventType.TEXT,
        config.bili.captcha_msg_template.format(code=code),
    )

    async with AsyncSessionLocal() as db_session:
        await save_verification_code(uid, db_session, code=code)
