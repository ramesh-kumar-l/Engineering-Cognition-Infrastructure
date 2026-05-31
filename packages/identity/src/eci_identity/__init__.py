"""ECI Identity — tenants, users, RBAC, OIDC, JWT.

Public surface:
  - config: IdentityConfig, load_identity_config
  - dto: RequestContext, TenantInput/Out, UserInput/Out, AuthResponse, VALID_ROLES
  - errors: IdentityError hierarchy
  - rbac: require_role, can_write, can_admin, validate_role
  - token_service: TokenService
  - tenant_service: TenantService
  - user_service: UserService
  - oidc_service: OIDCService
"""

from eci_identity.config import IdentityConfig, load_identity_config
from eci_identity.dto import (
    AuthResponse,
    RequestContext,
    TenantInput,
    TenantOut,
    TokenClaims,
    UserInput,
    UserOut,
    VALID_ROLES,
)
from eci_identity.errors import (
    AuthError,
    DuplicateEmailError,
    ExpiredTokenError,
    IdentityError,
    InvalidTokenError,
    OIDCError,
    PermissionDeniedError,
    TenantNotFoundError,
    UserNotFoundError,
)
from eci_identity.oidc_service import OIDCService
from eci_identity.rbac import can_admin, can_write, require_role, validate_role
from eci_identity.tenant_service import TenantService
from eci_identity.token_service import TokenService
from eci_identity.user_service import UserService

__all__ = [
    "AuthError",
    "AuthResponse",
    "DuplicateEmailError",
    "ExpiredTokenError",
    "IdentityConfig",
    "IdentityError",
    "InvalidTokenError",
    "OIDCError",
    "OIDCService",
    "PermissionDeniedError",
    "RequestContext",
    "TenantInput",
    "TenantNotFoundError",
    "TenantOut",
    "TenantService",
    "TokenClaims",
    "TokenService",
    "UserInput",
    "UserNotFoundError",
    "UserOut",
    "UserService",
    "VALID_ROLES",
    "can_admin",
    "can_write",
    "load_identity_config",
    "require_role",
    "validate_role",
]
