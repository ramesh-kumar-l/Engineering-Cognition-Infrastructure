"""Integration tests for DocumentIngestService against real Postgres."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_ingest.blob_store import BlobStore
from eci_ingest.document_service import DocumentIngestService
from eci_ingest.dto import DocumentIngestRequest
from eci_ingest.errors import SourceTooLarge
from eci_storage.models import AuditEvent, Document, RawBlob


@pytest.mark.integration
def test_creates_document_and_blob(
    db_session: Session, blob_store: BlobStore
) -> None:
    svc = DocumentIngestService(db_session, blob_store=blob_store)
    req = DocumentIngestRequest(
        kind="markdown",
        source="unit-test",
        tags=["t1"],
    )
    result = svc.ingest(req, b"# Hello\n\nbody")
    assert result.deduplicated is False
    assert result.title == "Hello"

    docs = db_session.scalars(select(Document)).all()
    blobs = db_session.scalars(select(RawBlob)).all()
    assert len(docs) == 1
    assert len(blobs) == 1
    assert docs[0].raw_blob_id == blobs[0].id


@pytest.mark.integration
def test_idempotent_reingest_returns_same_document(
    db_session: Session, blob_store: BlobStore
) -> None:
    svc = DocumentIngestService(db_session, blob_store=blob_store)
    raw = b"# Same\n\nbody"
    req = DocumentIngestRequest(kind="markdown", source="unit-test")

    first = svc.ingest(req, raw)
    second = svc.ingest(req, raw)
    assert first.id == second.id
    assert second.deduplicated is True

    blobs = db_session.scalars(select(RawBlob)).all()
    docs = db_session.scalars(select(Document)).all()
    assert len(blobs) == 1
    assert len(docs) == 1


@pytest.mark.integration
def test_audit_records_create_and_dedup(
    db_session: Session, blob_store: BlobStore
) -> None:
    svc = DocumentIngestService(db_session, blob_store=blob_store)
    req = DocumentIngestRequest(kind="text", source="unit-test")
    svc.ingest(req, b"hello")
    svc.ingest(req, b"hello")

    actions = [
        e.action
        for e in db_session.scalars(
            select(AuditEvent).order_by(AuditEvent.occurred_at)
        ).all()
    ]
    assert "ingest.document.create" in actions
    assert "ingest.document.dedup" in actions


@pytest.mark.integration
def test_oversize_raises(
    db_session: Session, blob_store: BlobStore
) -> None:
    svc = DocumentIngestService(db_session, blob_store=blob_store)
    svc.config = svc.config.model_copy(update={"ingest_max_bytes": 4})
    req = DocumentIngestRequest(kind="text", source="unit-test")
    with pytest.raises(SourceTooLarge):
        svc.ingest(req, b"too long")
