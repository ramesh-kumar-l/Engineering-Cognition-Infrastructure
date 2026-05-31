"""Retrospective ORM model — a single reflection run over execution history."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Retrospective(Base, TimestampMixin):
    __tablename__ = "retrospectives"

    id: Mapped[uuid.UUID] = uuid_pk()
    cadence: Mapped[str] = mapped_column(String(16), nullable=False)  # weekly|monthly|milestone
    scope_type: Mapped[str | None] = mapped_column(String(16), nullable=True)  # roadmap|goal|global
    scope_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="running")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    lesson_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
