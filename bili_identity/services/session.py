from bili_identity.db import get_session_id


async def is_session_verified(session_id: str) -> bool:
    session = await get_session_id(session_id)
    return session is not None and session.get("verified", False)
