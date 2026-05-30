"""RawBlob — immutable, content-addressed origin bytes."""

from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class RawBlob(Base, TimestampMixin):
    __tablename__ = "raw_blobs"

    id: Mapped[uuid.UUID] = uuid_pk()
    content_hash: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    storage_uri: Mapped[str] = mapped_column(String(1024), nullable=False)

    def __repr__(self) -> str:
        return f"<RawBlob {self.content_hash[:12]}… {self.size_bytes}B>"
