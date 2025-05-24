from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bili_identity.models import RevokedToken


async def get_revoked_token(
    session: AsyncSession, jti: str
) -> Optional[RevokedToken]:
    result = await session.execute(
        select(RevokedToken).where(RevokedToken.jti == jti)
    )
    return result.scalar_one_or_none()


async def revoke_jwt(session: AsyncSession, jti: str) -> None:
    if await get_revoked_token(session, jti):
        return
    new_token = RevokedToken(jti=jti)
    session.add(new_token)
    await session.commit()
