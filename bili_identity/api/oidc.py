import logging

from fastapi import APIRouter, Request

from bili_identity.config import get_config
from bili_identity.services import get_jwks, get_jwks_alg

oidc_router = APIRouter(prefix="/api/oidc")
oidc_well_known_router = APIRouter(prefix="/.well-known")

logger = logging.getLogger(__name__)

config = get_config()


@oidc_well_known_router.get("/openid-configuration")
async def openid_configuration(request: Request):
    base = str(request.base_url).rstrip("/")
    same_directory = f"{base}{str(request.url.path).rsplit('/', 1)[0]}"
    return {
        "issuer": config.oidc.issuer,
        "authorization_endpoint": f"{base}/api/oidc/auth",
        "token_endpoint": f"{base}/api/oidc/token",
        "userinfo_endpoint": f"{base}/api/oidc/userinfo",
        "jwks_uri": f"{same_directory}/openid-jwks",
        "response_types_supported": ["code"],
        "subject_types_supported": ["public"],
        "id_token_signing_alg_values_supported": await get_jwks_alg(),
    }


@oidc_well_known_router.get("/openid-jwks")
async def openid_jwks():
    return await get_jwks()
