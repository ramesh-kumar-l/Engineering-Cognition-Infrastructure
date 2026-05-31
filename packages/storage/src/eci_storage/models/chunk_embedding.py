"""ChunkEmbedding — per-chunk vector embedding linked to a Document or Note."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk

try:
    from pgvector.sqlalchemy import Vector  # type: ignore[import-not-found]

    _VECTOR_TYPE = Vector(768)
except ImportError:  # pragma: no cover
    from sqlalchemy import Text as _VectorFallback  # type: ignore[assignment]

    _VECTOR_TYPE = _VectorFallback()  # type: ignore[assignment]


class ChunkEmbedding(Base, TimestampMixin):
    __tablename__ = "chunk_embeddings"
    __table_args__ = (
        CheckConstraint(
            "(document_id IS NOT NULL) OR (note_id IS NOT NULL)",
            name="ck_chunk_embeddings_source_not_null",
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
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    embedding: Mapped[Any] = mapped_column(_VECTOR_TYPE, nullable=False)
    model_used: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False, default=768)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<ChunkEmbedding {self.id} chunk_index={self.chunk_index}>"
