"""compression: summaries, mental_models

Revision ID: 0002_compression
Revises: 0001_initial
Create Date: 2026-05-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_compression"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "note_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notes.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("level", sa.String(16), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("word_count", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("model_used", sa.String(128), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(document_id IS NOT NULL) OR (note_id IS NOT NULL)",
            name="ck_summaries_source_not_null",
        ),
    )
    op.create_index("ix_summaries_document_id", "summaries", ["document_id"])
    op.create_index("ix_summaries_note_id", "summaries", ["note_id"])
    op.create_index("ix_summaries_source_hash", "summaries", ["source_hash"])

    op.create_table(
        "mental_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "note_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("notes.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("claims", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("entities", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("relationships", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("playbook", postgresql.JSONB, nullable=True),
        sa.Column("source_hash", sa.String(64), nullable=False),
        sa.Column("model_used", sa.String(128), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(document_id IS NOT NULL) OR (note_id IS NOT NULL)",
            name="ck_mental_models_source_not_null",
        ),
    )
    op.create_index("ix_mental_models_document_id", "mental_models", ["document_id"])
    op.create_index("ix_mental_models_note_id", "mental_models", ["note_id"])
    op.create_index("ix_mental_models_source_hash", "mental_models", ["source_hash"])


def downgrade() -> None:
    op.drop_table("mental_models")
    op.drop_table("summaries")
