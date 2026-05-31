"""Pure data transfer objects for the identity domain."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

VALID_ROLES: frozenset[str] = frozenset({"admin", "member", "viewer"})

# Role hierarchy used by rbac.py — higher index = more privilege.
ROLE_ORDER: list[str] = ["viewer", "member", "admin"]


@dataclass
class TenantInput:
    name: str
    slug: str


@dataclass
class TenantOut:
    id: uuid.UUID
    name: str
    slug: str
    status: str
    created_at: datetime


@dataclass
class UserInput:
    tenant_id: uuid.UUID
    email: str
    role: str = "member"
    display_name: str | None = None
    external_id: str | None = None


@dataclass
class UserOut:
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    display_name: str | None
    role: str
    status: str
    created_at: datetime


@dataclass
class RequestContext:
    """Injected into every request after authentication.

    Carries the resolved identity (user_id, tenant_id, role) so downstream
    services can scope queries and write actor identity to audit events.
    """

    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: str
    actor: str  # email address or "dev@localhost" in dev mode


@dataclass
class TokenClaims:
    """Parsed claims from a decoded JWT."""

    sub: str
    email: str
    tenant_id: str | None = None
    iss: str | None = None


@dataclass
class AuthResponse:
    access_token: str
    token_type: str = "bearer"
    user: UserOut | None = None
