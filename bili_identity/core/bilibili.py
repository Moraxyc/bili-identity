from bili_identity.config import config
from bili_identity.db import AsyncSessionLocal, save_verification_code
from bili_identity.utils.random import generate_code


async def send_verification_code(uid: int):
    code = generate_code()
    from bilibili_api import session

    await session.send_msg(
        config.credential,
        uid,
        session.EventType.TEXT,
        config.bili.captcha_msg_template.format(code=code),
    )

    async with AsyncSessionLocal() as db_session:
        await save_verification_code(uid, db_session, code=code)
