"""Read-only access to ingested sources (documents, notes).

Tenant isolation is enforced here: a row whose ``tenant_id`` differs from the
caller's is treated as absent (returns ``None``), never leaked.
"""

from __future__ import annotations

import uuid

from eci_storage.models import Document, Note
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_ingest.dto import DocumentListItem, DocumentRead, NoteRead


class SourceReadService:
    """Per-call instance; no per-instance state beyond the session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_documents(
        self, tenant_id: uuid.UUID | None, limit: int = 50, offset: int = 0
    ) -> list[DocumentListItem]:
        stmt = select(Document).order_by(Document.ingested_at.desc())
        if tenant_id is not None:
            stmt = stmt.where(Document.tenant_id == tenant_id)
        stmt = stmt.limit(limit).offset(offset)
        return [_doc_list_item(d) for d in self.session.scalars(stmt)]

    def get_document(
        self, document_id: uuid.UUID, tenant_id: uuid.UUID | None
    ) -> DocumentRead | None:
        doc = self.session.get(Document, document_id)
        if doc is None or (tenant_id is not None and doc.tenant_id != tenant_id):
            return None
        return DocumentRead(
            id=doc.id,
            kind=doc.kind,
            title=doc.title,
            source=doc.source,
            author=doc.author,
            tags=list(doc.tags),
            ingested_at=doc.ingested_at,
            body=doc.body,
            content_hash=doc.raw_blob.content_hash,
            metadata=dict(doc.meta),
            captured_at=doc.captured_at,
        )

    def get_note(self, note_id: uuid.UUID, tenant_id: uuid.UUID | None) -> NoteRead | None:
        note = self.session.get(Note, note_id)
        if note is None or (tenant_id is not None and note.tenant_id != tenant_id):
            return None
        return NoteRead(
            id=note.id,
            body=note.body,
            source=note.source,
            author=note.author,
            tags=list(note.tags),
            metadata=dict(note.meta),
            content_hash=note.content_hash,
            captured_at=note.captured_at,
            ingested_at=note.ingested_at,
        )


def _doc_list_item(doc: Document) -> DocumentListItem:
    return DocumentListItem(
        id=doc.id,
        kind=doc.kind,
        title=doc.title,
        source=doc.source,
        author=doc.author,
        tags=list(doc.tags),
        ingested_at=doc.ingested_at,
    )
