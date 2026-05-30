"""Smoke tests for the storage models against a real Postgres."""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from eci_storage.models import AuditEvent, Document, Note, RawBlob


@pytest.mark.integration
def test_raw_blob_round_trip(db_session: Session) -> None:
    blob = RawBlob(
        content_hash="a" * 64,
        size_bytes=10,
        content_type="text/markdown",
        storage_uri="file:///tmp/a",
    )
    db_session.add(blob)
    db_session.flush()
    fetched = db_session.get(RawBlob, blob.id)
    assert fetched is not None
    assert fetched.content_hash == "a" * 64


@pytest.mark.integration
def test_document_links_to_blob(db_session: Session) -> None:
    blob = RawBlob(
        content_hash="b" * 64,
        size_bytes=20,
        content_type="text/markdown",
        storage_uri="file:///tmp/b",
    )
    db_session.add(blob)
    db_session.flush()
    doc = Document(
        raw_blob_id=blob.id,
        kind="markdown",
        title="hello",
        body="hi",
        source="test",
        tags=["t1"],
        meta={"k": "v"},
    )
    db_session.add(doc)
    db_session.flush()
    assert doc.raw_blob.content_hash == "b" * 64


@pytest.mark.integration
def test_note_unique_content_hash(db_session: Session) -> None:
    n1 = Note(body="x", source="s", content_hash="c" * 64, tags=[], meta={})
    db_session.add(n1)
    db_session.flush()
    n2 = Note(body="x", source="s", content_hash="c" * 64, tags=[], meta={})
    db_session.add(n2)
    with pytest.raises(Exception):  # noqa: B017,PT011 — integrity error
        db_session.flush()


@pytest.mark.integration
def test_audit_event_persists(db_session: Session) -> None:
    ev = AuditEvent(
        actor="system",
        action="ingest.document.create",
        target_type="document",
        target_id=None,
        prior_state=None,
        new_state={"id": "x"},
        reason=None,
    )
    db_session.add(ev)
    db_session.flush()
    assert ev.id is not None
