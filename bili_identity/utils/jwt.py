import uuid
from datetime import datetime, timedelta, timezone

from jwcrypto import jwk, jwt


def generate_token(
    sub: str, token_type: str, lifetime_seconds: int, jwk: jwk.JWK
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=lifetime_seconds)).timestamp()),
        "jti": str(uuid.uuid4()),
        "typ": token_type,
    }

    token = jwt.JWT(
        header={"alg": "RS256", "kid": jwk.key_id, "typ": "JWT"},
        claims=payload,
    )
    token.make_signed_token(jwk)
    return token.serialize()


def decode_token(token_str: str, jwk: jwk.JWK) -> dict:
    token = jwt.JWT(key=jwk, jwt=token_str)
    return token.claims
