import secrets


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)
