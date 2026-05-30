"""Integration tests for EmbeddingService — requires real Postgres."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_retrieval.embedding_service import EmbeddingService
from eci_retrieval.errors import SourceNotFoundError
from eci_storage.models import ChunkEmbedding


@pytest.mark.integration
def test_embed_document_creates_chunks(
    db_session: Session,
    sample_document_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = EmbeddingService(db_session, stub_embedding_provider)
    count = svc.embed_document(sample_document_id)

    assert count >= 1
    rows = db_session.scalars(
        select(ChunkEmbedding).where(ChunkEmbedding.document_id == sample_document_id)
    ).all()
    assert len(rows) == count
    assert all(r.embedding is not None for r in rows)
    assert all(r.model_used == "stub-embed-0.1" for r in rows)


@pytest.mark.integration
def test_embed_document_is_idempotent(
    db_session: Session,
    sample_document_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = EmbeddingService(db_session, stub_embedding_provider)
    first = svc.embed_document(sample_document_id)
    second = svc.embed_document(sample_document_id)
    assert first >= 1
    assert second == 0  # all chunks already cached


@pytest.mark.integration
def test_embed_note_creates_chunks(
    db_session: Session,
    sample_note_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = EmbeddingService(db_session, stub_embedding_provider)
    count = svc.embed_note(sample_note_id)
    assert count >= 1
    rows = db_session.scalars(
        select(ChunkEmbedding).where(ChunkEmbedding.note_id == sample_note_id)
    ).all()
    assert len(rows) == count


@pytest.mark.integration
def test_embed_missing_document_raises(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = EmbeddingService(db_session, stub_embedding_provider)
    with pytest.raises(SourceNotFoundError):
        svc.embed_document(uuid.uuid4())
