import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bili_identity.models import User

logger = logging.getLogger(__name__)


async def get_user(uid: int, session: AsyncSession) -> Optional[User]:
    result = await session.execute(select(User).where(User.uid == uid))
    return result.scalar_one_or_none()


async def create_user(
    uid: int, session: AsyncSession, **kwargs
) -> Optional[User]:
    new_user = User(uid=uid, **kwargs)
    session.add(new_user)

    try:
        await session.commit()
        return new_user
    except IntegrityError as e:
        await session.rollback()
        logger.error(f"创建用户 {uid} 失败: {e}")
        return None


async def update_user(
    uid: int, session: AsyncSession, **kwargs
) -> Optional[User]:
    user = await get_user(uid, session)

    if not user:
        logger.warning(f"用户 {uid} 不存在，无法更新")
        return None

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        await session.commit()
        return user
    except Exception as e:
        await session.rollback()
        logger.error(f"更新用户 {uid} 失败: {e}")
        return None
