"""LessonEvidence ORM model — execution events that support a lesson claim."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class LessonEvidence(Base, TimestampMixin):
    __tablename__ = "lesson_evidence"

    id: Mapped[uuid.UUID] = uuid_pk()
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)  # goal|task|memory_entry
    source_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
