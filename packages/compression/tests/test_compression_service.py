"""Integration tests for CompressionService — requires real Postgres.

Uses the json_stub_provider fixture — no Ollama or cloud API required.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_compression.compression_service import CompressionService
from eci_compression.dto import CompressionRequest, SourceType
from eci_compression.errors import SourceNotFound
from eci_storage.models.mental_model import MentalModel
from eci_storage.models.summary import Summary


@pytest.mark.integration
def test_compress_document_creates_three_summaries(
    db_session: Session,
    sample_document_id: uuid.UUID,
    json_stub_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = CompressionService(db_session, json_stub_provider)
    result = svc.compress(
        CompressionRequest(source_id=sample_document_id, source_type=SourceType.DOCUMENT)
    )

    assert len(result.summaries) == 3
    assert result.source_id == sample_document_id

    saved = db_session.scalars(
        select(Summary).where(Summary.document_id == sample_document_id)
    ).all()
    assert len(saved) == 3
    assert {s.level for s in saved} == {"short", "medium", "long"}


@pytest.mark.integration
def test_compress_document_creates_mental_model(
    db_session: Session,
    sample_document_id: uuid.UUID,
    json_stub_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = CompressionService(db_session, json_stub_provider)
    svc.compress(
        CompressionRequest(source_id=sample_document_id, source_type=SourceType.DOCUMENT)
    )

    mm = db_session.scalar(
        select(MentalModel).where(MentalModel.document_id == sample_document_id)
    )
    assert mm is not None
    assert "test claim" in mm.claims
    assert len(mm.entities) == 1
    assert mm.model_used == "stub-0.1"


@pytest.mark.integration
def test_compress_note(
    db_session: Session,
    sample_note_id: uuid.UUID,
    json_stub_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = CompressionService(db_session, json_stub_provider)
    result = svc.compress(
        CompressionRequest(source_id=sample_note_id, source_type=SourceType.NOTE)
    )

    assert len(result.summaries) == 3
    saved = db_session.scalars(
        select(Summary).where(Summary.note_id == sample_note_id)
    ).all()
    assert len(saved) == 3


@pytest.mark.integration
def test_missing_document_raises_source_not_found(
    db_session: Session,
    json_stub_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = CompressionService(db_session, json_stub_provider)
    with pytest.raises(SourceNotFound):
        svc.compress(
            CompressionRequest(source_id=uuid.uuid4(), source_type=SourceType.DOCUMENT)
        )
