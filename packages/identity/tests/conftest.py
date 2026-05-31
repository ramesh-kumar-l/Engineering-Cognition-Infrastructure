"""Shared fixtures for identity integration tests."""

from __future__ import annotations

import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from eci_identity.dto import TenantInput, UserInput
from eci_identity.tenant_service import TenantService
from eci_identity.user_service import UserService
from eci_storage.models import Base

_DB_URL = os.environ.get("ECI_TEST_DB_URL", "")


@pytest.fixture(scope="session")
def db_engine():
    if not _DB_URL:
        pytest.skip("ECI_TEST_DB_URL not set")
    engine = create_engine(_DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Function-scoped session with automatic rollback — tests are fully isolated."""
    connection = db_engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection)
    session = factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def tenant_a(db_session: Session) -> uuid.UUID:
    svc = TenantService(db_session)
    slug = f"tenant-a-{uuid.uuid4().hex[:8]}"
    out = svc.create_tenant(TenantInput(name="Team Alpha", slug=slug))
    return out.id


@pytest.fixture()
def tenant_b(db_session: Session) -> uuid.UUID:
    svc = TenantService(db_session)
    slug = f"tenant-b-{uuid.uuid4().hex[:8]}"
    out = svc.create_tenant(TenantInput(name="Team Beta", slug=slug))
    return out.id


@pytest.fixture()
def admin_user(db_session: Session, tenant_a: uuid.UUID) -> uuid.UUID:
    svc = UserService(db_session)
    out = svc.create_user(UserInput(
        tenant_id=tenant_a,
        email="admin@alpha.test",
        role="admin",
    ))
    return out.id


@pytest.fixture()
def member_user(db_session: Session, tenant_a: uuid.UUID) -> uuid.UUID:
    svc = UserService(db_session)
    out = svc.create_user(UserInput(
        tenant_id=tenant_a,
        email="member@alpha.test",
        role="member",
    ))
    return out.id
