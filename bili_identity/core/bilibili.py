import logging

from bilibili_api.session import Event, EventType

from bili_identity.config import get_config
from bili_identity.db import AsyncSessionLocal, save_verification_code
from bili_identity.services import verify_code
from bili_identity.utils import extract_code_from_message, generate_code

logger = logging.getLogger(__name__)


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


config = get_config()


async def receive_verifiction_code(event: Event):
    logger.debug(f"接收到消息事件: {event}")
    if not isinstance(event.content, str):
        logger.debug("消息内容不是字符串，忽略处理。")
        return

    logger.debug(f"消息内容: {event.content}")
    code = extract_code_from_message(event.content, length=32)

    if not code:
        logger.debug("未提取到验证码。")
        await config.session.reply(
            event,
            "未识别到验证码，请发送包含验证码的内容，或切换到主动验证码模式",
        )
        return

    logger.debug(f"提取到的验证码: {code}")
    success = await verify_code(event.sender_uid, code, mode="passive")

    if success:
        logger.debug(f"用户 {event.uid} 验证成功。")
        await config.session.reply(event, "✅ 验证成功，您已完成身份验证。")
    else:
        logger.debug(f"用户 {event.uid} 验证失败")
        await config.session.reply(
            event, "❌ 验证失败，验证码错误或已过期。"
        )
