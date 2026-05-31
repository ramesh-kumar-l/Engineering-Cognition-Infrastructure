"""Auth router — OIDC login redirect and callback token exchange.

Endpoints:
  GET  /auth/login      → return OIDC authorization URL
  POST /auth/callback   → exchange OIDC code for a local JWT
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from eci_api.dependencies import get_db
from eci_identity.config import load_identity_config
from eci_identity.errors import OIDCError
from eci_identity.oidc_service import OIDCService
from eci_observability import get_logger

_log = get_logger("eci_api.routers.auth")
router = APIRouter(prefix="/auth", tags=["auth"])


class LoginResponse(BaseModel):
    auth_url: str
    state: str


class CallbackBody(BaseModel):
    code: str
    tenant_id: uuid.UUID


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _oidc_service(session: Session) -> OIDCService:
    return OIDCService(load_identity_config(), session)


@router.get("/login", response_model=LoginResponse, summary="Get OIDC authorization URL")
def get_auth_login(session: Session = Depends(get_db)) -> LoginResponse:
    """Return the OIDC provider authorization URL. Redirect the user there to authenticate."""
    try:
        result = _oidc_service(session).build_auth_url()
        return LoginResponse(auth_url=result["auth_url"], state=result["state"])
    except OIDCError as exc:
        _log.warning("auth.login_failed", error=str(exc))
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/callback", response_model=TokenResponse, summary="Exchange OIDC code for JWT")
def post_auth_callback(
    body: CallbackBody,
    session: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange the OIDC authorization code for a local JWT. tenant_id identifies the workspace."""
    try:
        result = _oidc_service(session).exchange_code(body.code, body.tenant_id)
        return TokenResponse(access_token=result.access_token)
    except OIDCError as exc:
        _log.warning("auth.callback_failed", tenant_id=str(body.tenant_id), error=str(exc))
        raise HTTPException(status_code=502, detail=str(exc)) from exc
