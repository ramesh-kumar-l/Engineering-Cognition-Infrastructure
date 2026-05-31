"""Goal — top-level execution intent, linked to source memory."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Goal(Base, TimestampMixin):
    """An outcome to achieve, optionally scoped to a Roadmap and motivated by a MemoryEntry."""

    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # pending | in_progress | completed | blocked | cancelled
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")

    roadmap_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_memory_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("memory_entries.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<Goal {self.id} status={self.status!r}>"
