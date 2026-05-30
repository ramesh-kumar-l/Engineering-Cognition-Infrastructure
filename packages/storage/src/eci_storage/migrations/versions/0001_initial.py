"""initial: raw_blobs, documents, notes, audit_events

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "raw_blobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("storage_uri", sa.String(1024), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_raw_blobs_content_hash", "raw_blobs", ["content_hash"])

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "raw_blob_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("raw_blobs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("title", sa.String(512), nullable=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("source", sa.String(512), nullable=False),
        sa.Column("author", sa.String(256), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_by", sa.String(128), nullable=False, server_default="system"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_raw_blob_id", "documents", ["raw_blob_id"])
    op.create_index("ix_documents_source", "documents", ["source"])

    op.create_table(
        "notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("source", sa.String(512), nullable=False),
        sa.Column("author", sa.String(256), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB, nullable=False, server_default="{}"),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_by", sa.String(128), nullable=False, server_default="system"),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notes_content_hash", "notes", ["content_hash"])

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor", sa.String(128), nullable=False),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("target_type", sa.String(64), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("prior_state", postgresql.JSONB, nullable=True),
        sa.Column("new_state", postgresql.JSONB, nullable=True),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_action", "audit_events", ["action"])
    op.create_index("ix_audit_events_target_id", "audit_events", ["target_id"])
    op.create_index("ix_audit_events_occurred_at", "audit_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("notes")
    op.drop_table("documents")
    op.drop_table("raw_blobs")
