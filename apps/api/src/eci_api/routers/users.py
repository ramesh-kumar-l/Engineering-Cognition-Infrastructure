"""Users router — user management within a tenant.

Endpoints:
  POST   /users              → create user (admin)
  GET    /users              → list users in caller's tenant (member+)
  GET    /users/{id}         → get user (member+, own tenant only)
  PATCH  /users/{id}/role    → update role (admin)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from eci_api.auth import get_request_context, require_admin
from eci_api.dependencies import get_db
from eci_identity.dto import RequestContext, UserInput
from eci_identity.errors import DuplicateEmailError, UserNotFoundError
from eci_identity.user_service import UserService
from eci_observability import get_logger

_log = get_logger("eci_api.routers.users")
router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=1, max_length=256)
    display_name: str | None = None
    role: str = "member"


class UpdateRoleRequest(BaseModel):
    role: str


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    display_name: str | None
    role: str
    status: str


def _svc(session: Session) -> UserService:
    return UserService(session)


@router.post("", status_code=201, response_model=UserResponse)
def create_user(
    body: CreateUserRequest,
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(require_admin),
) -> UserResponse:
    try:
        out = _svc(session).create_user(
            UserInput(
                tenant_id=ctx.tenant_id,
                email=body.email,
                role=body.role,
                display_name=body.display_name,
            )
        )
        return UserResponse(
            id=out.id, tenant_id=out.tenant_id, email=out.email,
            display_name=out.display_name, role=out.role, status=out.status,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("", response_model=list[UserResponse])
def list_users(
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
) -> list[UserResponse]:
    return [
        UserResponse(
            id=u.id, tenant_id=u.tenant_id, email=u.email,
            display_name=u.display_name, role=u.role, status=u.status,
        )
        for u in _svc(session).list_users(ctx.tenant_id)
    ]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
) -> UserResponse:
    try:
        u = _svc(session).get_user(user_id)
        if u.tenant_id != ctx.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied: cross-tenant read")
        return UserResponse(
            id=u.id, tenant_id=u.tenant_id, email=u.email,
            display_name=u.display_name, role=u.role, status=u.status,
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: uuid.UUID,
    body: UpdateRoleRequest,
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(require_admin),
) -> UserResponse:
    svc = _svc(session)
    try:
        u = svc.get_user(user_id)
        if u.tenant_id != ctx.tenant_id:
            raise HTTPException(status_code=403, detail="Access denied: cross-tenant write")
        updated = svc.update_role(user_id, body.role)
        return UserResponse(
            id=updated.id, tenant_id=updated.tenant_id, email=updated.email,
            display_name=updated.display_name, role=updated.role, status=updated.status,
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
