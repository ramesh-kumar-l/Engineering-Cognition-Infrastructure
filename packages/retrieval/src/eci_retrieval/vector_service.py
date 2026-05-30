"""VectorService — pgvector cosine similarity search over chunk_embeddings."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from eci_retrieval.dto import ChunkHit
from eci_retrieval.embedding_service import EmbeddingService


class VectorService:
    """Approximate nearest-neighbor search using pgvector HNSW cosine index."""

    def __init__(self, session: Session, embedding_service: EmbeddingService) -> None:
        self._session = session
        self._embedding_service = embedding_service

    def search(self, query: str, top_k: int = 10) -> list[ChunkHit]:
        """Embed *query* and return up to *top_k* most similar chunks."""
        if not query.strip():
            return []

        query_vec = self._embedding_service.embed_text(query)
        vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

        stmt = text("""
            SELECT
                document_id,
                note_id,
                chunk_index,
                content,
                1 - (embedding <=> cast(:vec AS vector)) AS score
            FROM chunk_embeddings
            ORDER BY embedding <=> cast(:vec AS vector)
            LIMIT :top_k
        """)

        rows = self._session.execute(stmt, {"vec": vec_str, "top_k": top_k}).fetchall()
        return [
            ChunkHit(
                source_type="document" if row.document_id is not None else "note",
                source_id=uuid.UUID(str(row.document_id or row.note_id)),
                chunk_index=row.chunk_index,
                content=row.content,
                score=max(0.0, float(row.score)),
            )
            for row in rows
        ]
