from enum import verify
from threading import Lock

from cachetools import TTLCache

from bili_identity.config import get_config
from bili_identity.utils import generate_session_id, session

config = get_config()

temp_auth_map = TTLCache(maxsize=10000, ttl=config.security.code_ttl)
reverse_map = TTLCache(maxsize=10000, ttl=config.security.code_ttl)

verified_session = TTLCache(maxsize=10000, ttl=config.security.code_ttl)

lock = Lock()


def store_mapping(session_id: str, uid: int):
    with lock:
        temp_auth_map[session_id] = uid
        reverse_map[uid] = session_id


def get_uid_by_session_id(session_id: str) -> str | None:
    with lock:
        return temp_auth_map.get(session_id)


def get_session_id_by_uid(uid: int) -> str | None:
    with lock:
        return reverse_map.get(uid)


def mark_verified_to_session_id(uid: int) -> None:
    session_id = get_session_id_by_uid(uid)
    with lock:
        verified_session[session_id] = True


def is_session_id_exist(session_id: str) -> bool:
    return session_id in temp_auth_map


def get_status_by_session_id(session_id: str) -> bool:
    return session_id in verified_session


def save_new_or_update_mapping(uid: int) -> str:
    session_id = generate_session_id()
    store_mapping(session_id, uid)
    return session_id


def clear_all_mappings_by_uid(uid: int) -> None:
    session_id = get_session_id_by_uid(uid)
    with lock:
        temp_auth_map.pop(session_id, None)
        reverse_map.pop(uid, None)
        verified_session.pop(session_id, None)
