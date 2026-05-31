"""Lesson ORM model — a typed insight produced by a retrospective run."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = uuid_pk()
    retrospective_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("retrospectives.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False, default="global")
    confidence: Mapped[str] = mapped_column(String(8), nullable=False, default="medium")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active", index=True)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
