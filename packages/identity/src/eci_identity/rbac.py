"""RBAC helpers — role hierarchy and permission guards."""

from __future__ import annotations

from eci_identity.dto import ROLE_ORDER, VALID_ROLES, RequestContext
from eci_identity.errors import PermissionDeniedError


def role_rank(role: str) -> int:
    """Return the numeric rank of a role (higher = more privilege). -1 if unknown."""
    try:
        return ROLE_ORDER.index(role)
    except ValueError:
        return -1


def require_role(ctx: RequestContext, minimum_role: str) -> None:
    """Raise PermissionDeniedError if ctx.role is below minimum_role."""
    if role_rank(ctx.role) < role_rank(minimum_role):
        raise PermissionDeniedError(
            f"Role '{ctx.role}' is insufficient; '{minimum_role}' or above required"
        )


def can_write(ctx: RequestContext) -> bool:
    """True if the caller can create or modify resources (member or admin)."""
    return role_rank(ctx.role) >= role_rank("member")


def can_admin(ctx: RequestContext) -> bool:
    """True if the caller holds the admin role."""
    return role_rank(ctx.role) >= role_rank("admin")


def validate_role(role: str) -> str:
    """Return role unchanged if valid; raise ValueError otherwise."""
    if role not in VALID_ROLES:
        raise ValueError(f"Invalid role {role!r}; must be one of {sorted(VALID_ROLES)}")
    return role
