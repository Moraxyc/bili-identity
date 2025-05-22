import json
import logging
from datetime import datetime, timezone
from typing import Optional

from bili_identity.config import get_config
from bili_identity.db import get_kv_session
from bili_identity.utils import generate_session_id

logger = logging.getLogger(__name__)

config = get_config()
DEFAULT_TTL = config.security.session_ttl


async def create_session_id(
    uid: int, ttl: int, is_verified: bool = False
) -> str:
    session_id = generate_session_id()

    session_data = {
        "session_id": session_id,
        "uid": uid,
        "verified": is_verified,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    key = f"session:{session_id}"
    uid_key = f"uid_to_session_id:{uid}"

    logger.debug(f"Creating session: {session_data}")
    kv_session = get_kv_session()
    await kv_session.set(key, json.dumps(session_data), ttl)
    await kv_session.set(uid_key, session_id, ttl)
    logger.debug(f"Session stored in Redis with TTL={ttl}")
    return session_id


async def get_session_id(session_id: str) -> Optional[dict]:
    kv_session = get_kv_session()
    key = f"session:{session_id}"
    raw_data = await kv_session.get(key)
    if not raw_data:
        return
    data = json.loads(raw_data)
    data["created_at"] = datetime.fromisoformat(data["created_at"])

    logger.debug(f"Retrieved raw session data for {session_id}: {raw_data}")
    return data


async def get_session_id_by_uid(uid: int) -> Optional[str]:
    kv_session = get_kv_session()
    key = f"uid_to_session_id:{uid}"
    return await kv_session.get(key)


async def update_session_id(
    session_id: str, updates: dict, ttl: Optional[int] = None
) -> Optional[dict]:
    kv_session = get_kv_session()
    key = f"session:{session_id}"
    raw_data = await kv_session.get(key)
    logger.debug(f"Raw session data before update: {raw_data}")
    if not raw_data:
        return
    data = json.loads(raw_data)
    data.update(updates)
    await kv_session.set(key, json.dumps(data), ttl or DEFAULT_TTL)

    if "uid" in data:
        uid_key = f"uid_to_session_id:{data['uid']}"
        uid_value = await kv_session.get(uid_key)
        if isinstance(uid_value, str):
            await kv_session.set(uid_key, uid_value, ttl or DEFAULT_TTL)

    logger.debug(
        f"Updated session {session_id} with: {updates}, TTL={ttl or DEFAULT_TTL}"
    )
    return data


async def destroy_session_id(session_id: str) -> bool:
    kv_session = get_kv_session()
    key = f"session:{session_id}"
    result = await kv_session.delete(key)
    logger.debug(f"Destroy session {session_id}, result: {result}")
    return result == 1


async def destroy_uid_to_session_id(uid: int) -> bool:
    kv_session = get_kv_session()
    key = f"uid_to_session_id:{uid}"
    result = await kv_session.delete(key)
    logger.debug(
        f"Destroy uid_to_session_id for uid {uid}, result: {result}"
    )
    return result == 1
