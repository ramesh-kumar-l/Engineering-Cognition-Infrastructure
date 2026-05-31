"""TenantService — CRUD for Tenant records."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_identity.dto import TenantInput, TenantOut
from eci_identity.errors import TenantNotFoundError
from eci_storage.models.tenant import Tenant

_log = get_logger("eci_identity.tenant_service")


def _to_out(t: Tenant) -> TenantOut:
    return TenantOut(
        id=t.id,
        name=t.name,
        slug=t.slug,
        status=t.status,
        created_at=t.created_at,
    )


class TenantService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_tenant(self, inp: TenantInput) -> TenantOut:
        tenant = Tenant(name=inp.name, slug=inp.slug)
        self._session.add(tenant)
        self._session.flush()
        _log.info("tenant.created", tenant_id=str(tenant.id), slug=inp.slug)
        return _to_out(tenant)

    def get_tenant(self, tenant_id: uuid.UUID) -> TenantOut:
        t = self._session.get(Tenant, tenant_id)
        if t is None:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        return _to_out(t)

    def get_by_slug(self, slug: str) -> TenantOut:
        t = self._session.scalar(select(Tenant).where(Tenant.slug == slug))
        if t is None:
            raise TenantNotFoundError(f"Tenant slug={slug!r} not found")
        return _to_out(t)

    def list_tenants(self) -> list[TenantOut]:
        rows = self._session.scalars(select(Tenant).order_by(Tenant.created_at))
        return [_to_out(t) for t in rows]
