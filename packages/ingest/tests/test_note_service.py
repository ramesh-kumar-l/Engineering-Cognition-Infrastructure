"""Integration tests for NoteIngestService."""

from __future__ import annotations

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_ingest.dto import NoteIngestRequest
from eci_ingest.note_service import NoteIngestService
from eci_storage.models import AuditEvent, Note


@pytest.mark.integration
def test_creates_note(db_session: Session) -> None:
    svc = NoteIngestService(db_session)
    res = svc.ingest(
        NoteIngestRequest(body="a thought", source="manual", tags=["t"])
    )
    assert res.deduplicated is False
    assert db_session.scalars(select(Note)).first() is not None


@pytest.mark.integration
def test_dedup_on_identical_payload(db_session: Session) -> None:
    svc = NoteIngestService(db_session)
    req = NoteIngestRequest(body="same", source="manual", author="me")
    a = svc.ingest(req)
    b = svc.ingest(req)
    assert a.id == b.id
    assert b.deduplicated is True
    assert len(db_session.scalars(select(Note)).all()) == 1


@pytest.mark.integration
def test_audit_recorded(db_session: Session) -> None:
    svc = NoteIngestService(db_session)
    svc.ingest(NoteIngestRequest(body="hi", source="m"))
    svc.ingest(NoteIngestRequest(body="hi", source="m"))
    actions = [
        e.action
        for e in db_session.scalars(
            select(AuditEvent).order_by(AuditEvent.occurred_at)
        ).all()
    ]
    assert "ingest.note.create" in actions
    assert "ingest.note.dedup" in actions
