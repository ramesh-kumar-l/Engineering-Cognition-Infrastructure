"""MemoryEntry — curated long-term memory record, versioned and embedding-indexed."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk

try:
    from pgvector.sqlalchemy import Vector  # type: ignore[import-not-found]

    _VECTOR_TYPE = Vector(768)
except ImportError:  # pragma: no cover
    from sqlalchemy import Text as _VectorFallback  # type: ignore[assignment]

    _VECTOR_TYPE = _VectorFallback()  # type: ignore[assignment]


class MemoryEntry(Base, TimestampMixin):
    """Curated knowledge record — distinct from raw ingest. Versioned + vector-indexed."""

    __tablename__ = "memory_entries"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    # Optional back-reference to the source document or note that motivated this entry.
    source_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # "document" | "note" | None
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    embedding: Mapped[Any | None] = mapped_column(_VECTOR_TYPE, nullable=True)
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    def __repr__(self) -> str:
        return f"<MemoryEntry {self.id} title={self.title!r} v{self.version}>"
