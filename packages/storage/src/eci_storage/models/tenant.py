"""Tenant — top-level workspace / organisation; the isolation boundary."""

from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    # active | suspended
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active", index=True)

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
