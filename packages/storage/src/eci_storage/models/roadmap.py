"""Roadmap — ordered collection of goals."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class Roadmap(Base, TimestampMixin):
    """Top-level container grouping related goals."""

    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Roadmap {self.id} title={self.title!r}>"
