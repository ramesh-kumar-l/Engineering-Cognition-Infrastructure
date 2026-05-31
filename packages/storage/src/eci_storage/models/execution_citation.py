"""ExecutionCitation — persisted evidence linking a goal or task to a retrieval result."""

from __future__ import annotations

import uuid

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class ExecutionCitation(Base, TimestampMixin):
    """Snapshot of a retrieval citation stored at goal/task creation time.

    Uses a polymorphic (target_type, target_id) pattern — no FK on target_id —
    so a single table covers both goals and tasks (see ADR-007).
    """

    __tablename__ = "execution_citations"

    id: Mapped[uuid.UUID] = uuid_pk()

    # Polymorphic target: 'goal' | 'task'
    target_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)

    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    source_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    def __repr__(self) -> str:
        return f"<ExecutionCitation {self.target_type}:{self.target_id}>"
