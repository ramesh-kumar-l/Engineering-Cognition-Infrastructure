"""UserService — CRUD and role management for User records."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_identity.dto import UserInput, UserOut
from eci_identity.errors import DuplicateEmailError, UserNotFoundError
from eci_identity.rbac import validate_role
from eci_storage.models.user import User

_log = get_logger("eci_identity.user_service")


def _to_out(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        tenant_id=u.tenant_id,
        email=u.email,
        display_name=u.display_name,
        role=u.role,
        status=u.status,
        created_at=u.created_at,
    )


class UserService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_user(self, inp: UserInput) -> UserOut:
        validate_role(inp.role)
        existing = self._session.scalar(
            select(User).where(User.tenant_id == inp.tenant_id, User.email == inp.email)
        )
        if existing is not None:
            raise DuplicateEmailError(f"Email {inp.email!r} already exists in this tenant")
        user = User(
            tenant_id=inp.tenant_id,
            email=inp.email,
            display_name=inp.display_name,
            role=inp.role,
            external_id=inp.external_id,
        )
        self._session.add(user)
        self._session.flush()
        _log.info("user.created", user_id=str(user.id), tenant_id=str(inp.tenant_id))
        return _to_out(user)

    def get_user(self, user_id: uuid.UUID) -> UserOut:
        u = self._session.get(User, user_id)
        if u is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return _to_out(u)

    def get_by_email(self, tenant_id: uuid.UUID, email: str) -> UserOut:
        u = self._session.scalar(
            select(User).where(User.tenant_id == tenant_id, User.email == email)
        )
        if u is None:
            raise UserNotFoundError(f"User {email!r} not found in tenant")
        return _to_out(u)

    def get_by_external_id(self, tenant_id: uuid.UUID, external_id: str) -> UserOut | None:
        u = self._session.scalar(
            select(User).where(
                User.tenant_id == tenant_id, User.external_id == external_id
            )
        )
        return _to_out(u) if u is not None else None

    def list_users(self, tenant_id: uuid.UUID) -> list[UserOut]:
        rows = self._session.scalars(
            select(User).where(User.tenant_id == tenant_id).order_by(User.created_at)
        )
        return [_to_out(u) for u in rows]

    def update_role(self, user_id: uuid.UUID, role: str) -> UserOut:
        validate_role(role)
        u = self._session.get(User, user_id)
        if u is None:
            raise UserNotFoundError(f"User {user_id} not found")
        u.role = role
        self._session.flush()
        _log.info("user.role_updated", user_id=str(user_id), role=role)
        return _to_out(u)
