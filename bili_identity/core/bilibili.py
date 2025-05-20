from datetime import datetime, timedelta, timezone

from config import config
from db import AsyncSessionLocal
from models.verification import VerificationCode
from utils.random import generate_code


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
        record = VerificationCode(
            uid=uid,
            code=code,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            mode="active",
        )
        await db_session.merge(record)
        await db_session.commit()
