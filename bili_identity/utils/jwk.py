import logging
import uuid

from jwcrypto import jwk

logger = logging.getLogger(__name__)


def generate_new_rs256() -> dict:
    kid = str(uuid.uuid4())

    key = jwk.JWK.generate(kty="RSA", size=2048)
    jwk_dict = key.export(private_key=True, as_dict=True)
    jwk_dict.update({"alg": "RS256", "use": "sig", "kid": kid})
    logger.debug(f"生成kid为{kid}的RS256 JWK")

    return jwk_dict
