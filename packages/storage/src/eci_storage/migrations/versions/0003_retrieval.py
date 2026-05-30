"""retrieval: chunk_embeddings, memory_entries, FTS + vector indices

Revision ID: 0003_retrieval
Revises: 0002_compression
Create Date: 2026-05-30
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "0003_retrieval"
down_revision: Union[str, None] = "0002_compression"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute("""
        CREATE TABLE chunk_embeddings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
            note_id UUID REFERENCES notes(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            content_hash VARCHAR(64) NOT NULL,
            embedding vector(768) NOT NULL,
            model_used VARCHAR(128) NOT NULL DEFAULT '',
            dimensions INTEGER NOT NULL DEFAULT 768,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            CONSTRAINT ck_chunk_embeddings_source_not_null
                CHECK ((document_id IS NOT NULL) OR (note_id IS NOT NULL))
        )
    """)

    op.execute("""
        CREATE TABLE memory_entries (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(512) NOT NULL,
            body TEXT NOT NULL,
            tags TEXT[] NOT NULL DEFAULT '{}',
            source_type VARCHAR(32),
            source_id UUID,
            version INTEGER NOT NULL DEFAULT 1,
            is_current BOOLEAN NOT NULL DEFAULT TRUE,
            embedding vector(768),
            model_used VARCHAR(128),
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Regular indices
    op.execute("CREATE INDEX ix_chunk_embeddings_document_id ON chunk_embeddings(document_id)")
    op.execute("CREATE INDEX ix_chunk_embeddings_note_id ON chunk_embeddings(note_id)")
    op.execute("CREATE INDEX ix_chunk_embeddings_content_hash ON chunk_embeddings(content_hash)")
    op.execute("CREATE INDEX ix_memory_entries_source_id ON memory_entries(source_id)")

    # GIN index for full-text search on chunk content
    op.execute("""
        CREATE INDEX ix_chunk_embeddings_fts
        ON chunk_embeddings USING GIN (to_tsvector('english', content))
    """)

    # HNSW vector indices for approximate nearest-neighbor search (cosine distance)
    op.execute("""
        CREATE INDEX ix_chunk_embeddings_embedding_hnsw
        ON chunk_embeddings USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    op.execute("""
        CREATE INDEX ix_memory_entries_embedding_hnsw
        ON memory_entries USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS memory_entries")
    op.execute("DROP TABLE IF EXISTS chunk_embeddings")
