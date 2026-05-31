"""Tenants router — workspace CRUD (admin-only).

Endpoints:
  POST /tenants           → create tenant (admin)
  GET  /tenants           → list all tenants (admin)
  GET  /tenants/{id}      → get tenant by ID (admin)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from eci_api.auth import require_admin
from eci_api.dependencies import get_db
from eci_identity.dto import RequestContext, TenantInput
from eci_identity.errors import TenantNotFoundError
from eci_identity.tenant_service import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


class CreateTenantRequest(BaseModel):
    name: str = Field(min_length=1, max_length=256)
    slug: str = Field(min_length=1, max_length=64, pattern=r"^[a-z0-9-]+$")


class TenantResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    status: str


def _svc(session: Session) -> TenantService:
    return TenantService(session)


@router.post("", status_code=201, response_model=TenantResponse)
def create_tenant(
    body: CreateTenantRequest,
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(require_admin),
) -> TenantResponse:
    out = _svc(session).create_tenant(TenantInput(name=body.name, slug=body.slug))
    return TenantResponse(id=out.id, name=out.name, slug=out.slug, status=out.status)


@router.get("", response_model=list[TenantResponse])
def list_tenants(
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(require_admin),
) -> list[TenantResponse]:
    return [
        TenantResponse(id=t.id, name=t.name, slug=t.slug, status=t.status)
        for t in _svc(session).list_tenants()
    ]


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: uuid.UUID,
    session: Session = Depends(get_db),
    ctx: RequestContext = Depends(require_admin),
) -> TenantResponse:
    try:
        t = _svc(session).get_tenant(tenant_id)
        return TenantResponse(id=t.id, name=t.name, slug=t.slug, status=t.status)
    except TenantNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
