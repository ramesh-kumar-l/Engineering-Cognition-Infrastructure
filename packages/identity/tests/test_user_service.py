"""Integration tests for UserService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_identity.dto import UserInput
from eci_identity.errors import DuplicateEmailError, UserNotFoundError
from eci_identity.user_service import UserService


@pytest.mark.integration
def test_create_user(db_session: Session, tenant_a: uuid.UUID) -> None:
    svc = UserService(db_session)
    out = svc.create_user(UserInput(tenant_id=tenant_a, email="alice@test.io", role="member"))
    assert out.id is not None
    assert out.email == "alice@test.io"
    assert out.role == "member"
    assert out.tenant_id == tenant_a


@pytest.mark.integration
def test_create_admin_user(db_session: Session, tenant_a: uuid.UUID) -> None:
    svc = UserService(db_session)
    out = svc.create_user(UserInput(tenant_id=tenant_a, email="boss@test.io", role="admin"))
    assert out.role == "admin"


@pytest.mark.integration
def test_duplicate_email_raises(db_session: Session, tenant_a: uuid.UUID) -> None:
    svc = UserService(db_session)
    svc.create_user(UserInput(tenant_id=tenant_a, email="dup@test.io", role="member"))
    with pytest.raises(DuplicateEmailError):
        svc.create_user(UserInput(tenant_id=tenant_a, email="dup@test.io", role="viewer"))


@pytest.mark.integration
def test_get_user_not_found(db_session: Session) -> None:
    svc = UserService(db_session)
    with pytest.raises(UserNotFoundError):
        svc.get_user(uuid.uuid4())


@pytest.mark.integration
def test_get_by_email(db_session: Session, tenant_a: uuid.UUID) -> None:
    svc = UserService(db_session)
    svc.create_user(UserInput(tenant_id=tenant_a, email="lookup@test.io", role="member"))
    out = svc.get_by_email(tenant_a, "lookup@test.io")
    assert out.email == "lookup@test.io"


@pytest.mark.integration
def test_get_by_external_id_returns_none_if_missing(
    db_session: Session, tenant_a: uuid.UUID
) -> None:
    svc = UserService(db_session)
    assert svc.get_by_external_id(tenant_a, "nonexistent-oidc-sub") is None


@pytest.mark.integration
def test_update_role(db_session: Session, tenant_a: uuid.UUID) -> None:
    svc = UserService(db_session)
    user = svc.create_user(UserInput(tenant_id=tenant_a, email="role@test.io", role="viewer"))
    updated = svc.update_role(user.id, "admin")
    assert updated.role == "admin"


@pytest.mark.integration
def test_list_users_scoped_to_tenant(
    db_session: Session, tenant_a: uuid.UUID, tenant_b: uuid.UUID
) -> None:
    svc = UserService(db_session)
    svc.create_user(UserInput(tenant_id=tenant_a, email="u1@alpha.io", role="member"))
    svc.create_user(UserInput(tenant_id=tenant_b, email="u2@beta.io", role="member"))
    a_users = svc.list_users(tenant_a)
    emails = [u.email for u in a_users]
    assert "u1@alpha.io" in emails
    assert "u2@beta.io" not in emails
