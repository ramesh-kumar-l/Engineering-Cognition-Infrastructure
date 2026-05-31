"""FTSService — Postgres full-text search over chunk_embeddings.content."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from eci_retrieval.dto import ChunkHit


class FTSService:
    """BM25-style retrieval using Postgres tsvector + ts_rank_cd."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def search(
        self,
        query: str,
        top_k: int = 10,
        tenant_id: uuid.UUID | None = None,
    ) -> list[ChunkHit]:
        """Return up to *top_k* chunks matching *query* by full-text rank."""
        if not query.strip():
            return []

        tenant_clause = "AND tenant_id = :tenant_id" if tenant_id is not None else ""
        stmt = text(f"""
            SELECT
                document_id,
                note_id,
                chunk_index,
                content,
                ts_rank_cd(
                    to_tsvector('english', content),
                    websearch_to_tsquery('english', :query)
                ) AS score
            FROM chunk_embeddings
            WHERE to_tsvector('english', content) @@ websearch_to_tsquery('english', :query)
            {tenant_clause}
            ORDER BY score DESC
            LIMIT :top_k
        """)

        params: dict[str, object] = {"query": query, "top_k": top_k}
        if tenant_id is not None:
            params["tenant_id"] = str(tenant_id)
        rows = self._session.execute(stmt, params).fetchall()
        return [
            ChunkHit(
                source_type="document" if row.document_id is not None else "note",
                source_id=uuid.UUID(str(row.document_id or row.note_id)),
                chunk_index=row.chunk_index,
                content=row.content,
                score=float(row.score),
            )
            for row in rows
        ]
