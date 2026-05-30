"""Summary — LLM-generated summary record linked to a Document or Note."""

from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Summary(Base, TimestampMixin):
    __tablename__ = "summaries"
    __table_args__ = (
        CheckConstraint(
            "(document_id IS NOT NULL) OR (note_id IS NOT NULL)",
            name="ck_summaries_source_not_null",
        ),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    note_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # short|medium|long
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    word_count: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    model_used: Mapped[str] = mapped_column(String(128), nullable=False, default="")

    def __repr__(self) -> str:
        return f"<Summary {self.id} level={self.level!r}>"
