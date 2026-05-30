"""MemoryService — CRUD + vector search over long-term memory entries."""

from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.orm import Session

from eci_llm.protocol import EmbeddingProvider, EmbeddingRequest
from eci_observability import get_logger
from eci_retrieval.dto import MemoryEntryInput, MemoryEntryOut
from eci_retrieval.errors import EmbeddingError, SourceNotFoundError
from eci_storage.models import MemoryEntry

_log = get_logger("eci_retrieval.memory_service")


class MemoryService:
    def __init__(self, session: Session, embedding_provider: EmbeddingProvider) -> None:
        self._session = session
        self._provider = embedding_provider

    def create_entry(self, inp: MemoryEntryInput) -> MemoryEntryOut:
        """Persist a new MemoryEntry and embed its body for vector search."""
        embedding = self._embed(inp.body)
        entry = MemoryEntry(
            title=inp.title,
            body=inp.body,
            tags=inp.tags,
            source_type=inp.source_type,
            source_id=inp.source_id,
            version=1,
            is_current=True,
            embedding=embedding,
            model_used=self._provider.model_name,
        )
        self._session.add(entry)
        self._session.flush()
        _log.info("memory.created", entry_id=str(entry.id), title=inp.title)
        return self._to_dto(entry)

    def get_entry(self, entry_id: uuid.UUID) -> MemoryEntryOut:
        entry = self._session.get(MemoryEntry, entry_id)
        if entry is None:
            raise SourceNotFoundError(f"MemoryEntry {entry_id} not found")
        return self._to_dto(entry)

    def list_entries(
        self,
        source_id: uuid.UUID | None = None,
        current_only: bool = True,
    ) -> list[MemoryEntryOut]:
        q = self._session.query(MemoryEntry)
        if current_only:
            q = q.filter(MemoryEntry.is_current.is_(True))
        if source_id is not None:
            q = q.filter(MemoryEntry.source_id == source_id)
        return [self._to_dto(e) for e in q.order_by(MemoryEntry.created_at.desc()).all()]

    def search_entries(self, query: str, top_k: int = 10) -> list[MemoryEntryOut]:
        """Vector similarity search over current memory entries."""
        query_vec = self._embed(query)
        vec_str = "[" + ",".join(str(v) for v in query_vec) + "]"

        stmt = text("""
            SELECT id FROM memory_entries
            WHERE is_current = TRUE AND embedding IS NOT NULL
            ORDER BY embedding <=> cast(:vec AS vector)
            LIMIT :top_k
        """)
        rows = self._session.execute(stmt, {"vec": vec_str, "top_k": top_k}).fetchall()
        ids = [uuid.UUID(str(row.id)) for row in rows]
        entries = self._session.query(MemoryEntry).filter(MemoryEntry.id.in_(ids)).all()
        by_id = {e.id: e for e in entries}
        return [self._to_dto(by_id[i]) for i in ids if i in by_id]

    def _embed(self, text_: str) -> list[float]:
        try:
            resp = self._provider.embed(EmbeddingRequest(texts=[text_]))
            return resp.embeddings[0]
        except Exception as exc:
            raise EmbeddingError(f"Failed to embed memory entry: {exc}") from exc

    @staticmethod
    def _to_dto(entry: MemoryEntry) -> MemoryEntryOut:
        return MemoryEntryOut(
            id=entry.id,
            title=entry.title,
            body=entry.body,
            tags=entry.tags or [],
            source_type=entry.source_type,
            source_id=entry.source_id,
            version=entry.version,
            is_current=entry.is_current,
            created_at=entry.created_at,
        )
