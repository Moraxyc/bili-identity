import base64
import json
from datetime import datetime, timezone
from logging import getLogger
from typing import Optional, Tuple

from jwcrypto import jwt
from jwcrypto.common import JWException

from bili_identity.config import get_config
from bili_identity.db import (
    AsyncSessionLocal,
    get_first_active_jwk,
    get_jwk,
    get_revoked_token,
    revoke_jwt,
)
from bili_identity.utils import generate_token

config = get_config()
logger = getLogger(__name__)


async def issue_tokens(
    uid: int, refresh_token: bool = True, access_token: bool = True
) -> Tuple[Optional[str], Optional[str]]:
    async with AsyncSessionLocal() as session:
        key = await get_first_active_jwk(session)

    token1 = (
        generate_token(
            str(uid), "refresh", config.security.refresh_token_ttl, key
        )
        if refresh_token
        else None
    )
    token2 = (
        generate_token(
            str(uid), "access", config.security.access_token_ttl, key
        )
        if access_token
        else None
    )

    return token1, token2


async def get_token(token: str) -> Optional[dict]:
    header_b64 = token.split(".")[0]
    padded = header_b64 + "=" * (-len(header_b64) % 4)
    header = json.loads(base64.urlsafe_b64decode(padded).decode())
    kid = header.get("kid")
    async with AsyncSessionLocal() as session:
        jwk_obj = await get_jwk(session, kid)
        if not jwk_obj:
            return

    key = jwk_obj.jwk

    try:
        verified_token = jwt.JWT(jwt=token, key=key)
        result = json.loads(verified_token.claims)
        return result
    except JWException as e:
        logger.debug(f"Invalid token: {e}")
        return None


async def revoke_token(jti: str) -> None:
    async with AsyncSessionLocal() as session:
        await revoke_jwt(session, jti)


async def is_token_valid(token: str) -> bool:
    claims = await get_token(token)
    if not claims:
        return False

    jti = claims.get("jti")
    typ = claims.get("typ")
    exp = claims.get("exp")

    if not exp or datetime.now(timezone.utc).timestamp() > exp:
        logger.debug("Token expired")
        return False

    if typ == "refresh" and jti:
        async with AsyncSessionLocal() as session:
            result = await get_revoked_token(session, jti)
            if result:
                return False

    return True
