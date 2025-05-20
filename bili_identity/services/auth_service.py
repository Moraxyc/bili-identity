from datetime import datetime, timezone

from db import AsyncSessionLocal
from models.user import User
from models.verification import VerificationCode
from sqlalchemy import select


async def send_code(uid: int):
    from core.bilibili import send_verification_code

    await send_verification_code(uid)


async def verify_code(uid: int, code: str) -> bool:
    async with AsyncSessionLocal() as session:
        # 查询验证码记录
        result = await session.execute(
            select(VerificationCode).where(VerificationCode.uid == uid)
        )
        record = result.scalar_one_or_none()

        if not record:
            return False
        if record.expires_at < datetime.now(timezone.utc):
            return False
        if record.code != code:
            return False

        # 更新用户验证状态
        user_result = await session.execute(select(User).where(User.uid == uid))
        user = user_result.scalar_one_or_none()
        if user:
            user.is_verified = True
            await session.commit()
            return True

    return False
