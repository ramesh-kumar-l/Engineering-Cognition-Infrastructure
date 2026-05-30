"""CitationEngine — enriches raw ChunkHits with source metadata (title, URI)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from eci_retrieval.dto import ChunkHit, Citation
from eci_storage.models import Document, Note


class CitationEngine:
    """Resolves source metadata for each hit and produces Citation objects."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def build_citations(self, hits: list[ChunkHit]) -> list[Citation]:
        """Return a Citation for every ChunkHit, with title and URI resolved."""
        if not hits:
            return []

        doc_ids = {h.source_id for h in hits if h.source_type == "document"}
        note_ids = {h.source_id for h in hits if h.source_type == "note"}

        docs = self._fetch_docs(doc_ids)
        notes = self._fetch_notes(note_ids)

        return [
            Citation(
                source_type=hit.source_type,
                source_id=hit.source_id,
                chunk_index=hit.chunk_index,
                content=hit.content,
                score=hit.score,
                title=self._title(hit, docs, notes),
                source_uri=self._uri(hit, docs, notes),
            )
            for hit in hits
        ]

    def _fetch_docs(self, ids: set[uuid.UUID]) -> dict[uuid.UUID, Document]:
        if not ids:
            return {}
        rows = self._session.query(Document).filter(Document.id.in_(ids)).all()
        return {r.id: r for r in rows}

    def _fetch_notes(self, ids: set[uuid.UUID]) -> dict[uuid.UUID, Note]:
        if not ids:
            return {}
        rows = self._session.query(Note).filter(Note.id.in_(ids)).all()
        return {r.id: r for r in rows}

    @staticmethod
    def _title(
        hit: ChunkHit,
        docs: dict[uuid.UUID, Document],
        notes: dict[uuid.UUID, Note],
    ) -> str | None:
        if hit.source_type == "document":
            doc = docs.get(hit.source_id)
            return doc.title if doc else None
        if hit.source_type == "note":
            note = notes.get(hit.source_id)
            if note is None:
                return None
            return note.body[:80] + "…" if len(note.body) > 80 else note.body
        return None

    @staticmethod
    def _uri(
        hit: ChunkHit,
        docs: dict[uuid.UUID, Document],
        notes: dict[uuid.UUID, Note],
    ) -> str | None:
        if hit.source_type == "document":
            doc = docs.get(hit.source_id)
            return doc.source if doc else None
        if hit.source_type == "note":
            note = notes.get(hit.source_id)
            return note.source if note else None
        return None
