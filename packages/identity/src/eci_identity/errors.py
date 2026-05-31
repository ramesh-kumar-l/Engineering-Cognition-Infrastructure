"""Identity domain errors."""

from __future__ import annotations


class IdentityError(Exception):
    """Base for all identity domain errors."""


class AuthError(IdentityError):
    """Authentication failed."""


class InvalidTokenError(AuthError):
    """JWT is malformed or signature invalid."""


class ExpiredTokenError(AuthError):
    """JWT has expired."""


class PermissionDeniedError(IdentityError):
    """Caller's role is insufficient for the requested operation."""


class TenantNotFoundError(IdentityError):
    """Tenant does not exist."""


class UserNotFoundError(IdentityError):
    """User does not exist."""


class DuplicateEmailError(IdentityError):
    """Email already exists within this tenant."""


class OIDCError(IdentityError):
    """OIDC flow or token exchange error."""
