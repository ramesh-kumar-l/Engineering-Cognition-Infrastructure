"""Note — inline, short-form captured content (no raw blob)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, utcnow, uuid_pk


class Note(Base, TimestampMixin):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = uuid_pk()
    body: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str | None] = mapped_column(String(256), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    meta: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
    captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    ingested_by: Mapped[str] = mapped_column(String(128), default="system", nullable=False)
    content_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Note {self.id} source={self.source!r}>"
