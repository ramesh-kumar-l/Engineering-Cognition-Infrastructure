"""User — member of a tenant with a specific role."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    # admin | member | viewer
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")
    # OIDC sub claim from the identity provider
    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    # active | suspended
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active", index=True)

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role}>"
