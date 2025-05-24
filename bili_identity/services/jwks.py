from logging import getLogger
from typing import List

from bili_identity.db import AsyncSessionLocal, ensure_jwks, list_jwks

logger = getLogger(__name__)


async def get_jwks() -> dict:
    async with AsyncSessionLocal() as session:
        await ensure_jwks(session)
        jwks = await list_jwks(session)
        logger.debug(f"查询到 {len(jwks)} 个有效 JWK 条目")

    jwks_dict = {"keys": jwks}
    return jwks_dict


async def get_jwks_alg() -> List[str]:
    async with AsyncSessionLocal() as session:
        jwks_list = await list_jwks(session)
        algs = [jwk["alg"] for jwk in jwks_list if "alg" in jwk]
        # 去重
        return list(set(algs))
