"""Integration tests for TenantService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_identity.dto import TenantInput
from eci_identity.errors import TenantNotFoundError
from eci_identity.tenant_service import TenantService


@pytest.mark.integration
def test_create_tenant(db_session: Session) -> None:
    svc = TenantService(db_session)
    slug = f"acme-{uuid.uuid4().hex[:8]}"
    out = svc.create_tenant(TenantInput(name="Acme Corp", slug=slug))
    assert out.id is not None
    assert out.name == "Acme Corp"
    assert out.slug == slug
    assert out.status == "active"


@pytest.mark.integration
def test_get_tenant(db_session: Session) -> None:
    svc = TenantService(db_session)
    slug = f"widgets-{uuid.uuid4().hex[:8]}"
    created = svc.create_tenant(TenantInput(name="Widgets Inc", slug=slug))
    fetched = svc.get_tenant(created.id)
    assert fetched.id == created.id
    assert fetched.slug == slug


@pytest.mark.integration
def test_get_tenant_not_found(db_session: Session) -> None:
    svc = TenantService(db_session)
    with pytest.raises(TenantNotFoundError):
        svc.get_tenant(uuid.uuid4())


@pytest.mark.integration
def test_get_by_slug(db_session: Session) -> None:
    svc = TenantService(db_session)
    slug = f"slug-test-{uuid.uuid4().hex[:8]}"
    svc.create_tenant(TenantInput(name="Slug Test", slug=slug))
    out = svc.get_by_slug(slug)
    assert out.slug == slug


@pytest.mark.integration
def test_get_by_slug_not_found(db_session: Session) -> None:
    svc = TenantService(db_session)
    with pytest.raises(TenantNotFoundError):
        svc.get_by_slug("does-not-exist-xyz")


@pytest.mark.integration
def test_list_tenants(db_session: Session) -> None:
    svc = TenantService(db_session)
    before = len(svc.list_tenants())
    svc.create_tenant(TenantInput(name="T1", slug=f"t1-{uuid.uuid4().hex[:8]}"))
    svc.create_tenant(TenantInput(name="T2", slug=f"t2-{uuid.uuid4().hex[:8]}"))
    after = svc.list_tenants()
    assert len(after) == before + 2
