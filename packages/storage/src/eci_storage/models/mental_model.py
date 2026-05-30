"""MentalModel — structured knowledge extracted from a Document or Note.

Stores claims (list of strings), entities (list of dicts), relationships
(list of dicts), and optionally a playbook (dict) — all as JSONB columns.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from eci_storage.models.base import Base, TimestampMixin, uuid_pk


class MentalModel(Base, TimestampMixin):
    __tablename__ = "mental_models"
    __table_args__ = (
        CheckConstraint(
            "(document_id IS NOT NULL) OR (note_id IS NOT NULL)",
            name="ck_mental_models_source_not_null",
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
    claims: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    entities: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    relationships: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    playbook: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    source_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    model_used: Mapped[str] = mapped_column(String(128), nullable=False, default="")

    def __repr__(self) -> str:
        return f"<MentalModel {self.id} doc={self.document_id} note={self.note_id}>"
