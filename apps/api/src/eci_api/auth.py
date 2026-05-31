"""FastAPI auth dependencies — token extraction, context injection, RBAC guards."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from prometheus_client import Counter

from eci_identity.config import IdentityConfig, load_identity_config
from eci_identity.dto import RequestContext
from eci_identity.errors import AuthError, PermissionDeniedError
from eci_identity.rbac import require_role
from eci_identity.token_service import TokenService
from eci_observability import get_logger

_log = get_logger("eci_api.auth")
_auth_denied = Counter(
    "eci_auth_denied_total",
    "Auth deny events by reason",
    ["reason"],
)

_bearer = HTTPBearer(auto_error=False)
_config: IdentityConfig | None = None


def _cfg() -> IdentityConfig:
    global _config
    if _config is None:
        _config = load_identity_config()
    return _config


def get_request_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> RequestContext:
    """Extract and validate the Bearer JWT; return a RequestContext."""
    cfg = _cfg()
    if cfg.auth_disabled:
        return TokenService(cfg).dev_context()
    if credentials is None:
        _auth_denied.labels(reason="missing_token").inc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return TokenService(cfg).decode(credentials.credentials)
    except AuthError as exc:
        _auth_denied.labels(reason="invalid_token").inc()
        _log.warning("auth.token_rejected", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_write(
    ctx: RequestContext = Depends(get_request_context),
) -> RequestContext:
    """Require at least 'member' role; raise 403 otherwise."""
    try:
        require_role(ctx, "member")
    except PermissionDeniedError as exc:
        _auth_denied.labels(reason="insufficient_role").inc()
        _log.warning("auth.rbac_denied", actor=ctx.actor, role=ctx.role, required="member")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return ctx


def require_admin(
    ctx: RequestContext = Depends(get_request_context),
) -> RequestContext:
    """Require 'admin' role; raise 403 otherwise."""
    try:
        require_role(ctx, "admin")
    except PermissionDeniedError as exc:
        _auth_denied.labels(reason="insufficient_role").inc()
        _log.warning("auth.rbac_denied", actor=ctx.actor, role=ctx.role, required="admin")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    return ctx
