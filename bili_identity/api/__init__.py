from .auth import auth_router
from .oidc import oidc_router, oidc_well_known_router

__all__ = ["auth_router", "oidc_well_known_router", "oidc_router"]
