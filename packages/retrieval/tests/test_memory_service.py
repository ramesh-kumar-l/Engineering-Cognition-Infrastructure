"""Integration tests for MemoryService — requires real Postgres."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_retrieval.dto import MemoryEntryInput
from eci_retrieval.errors import SourceNotFoundError
from eci_retrieval.memory_service import MemoryService


@pytest.mark.integration
def test_create_and_get_entry(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = MemoryService(db_session, stub_embedding_provider)
    inp = MemoryEntryInput(title="Lesson Learned", body="Always write integration tests.")
    created = svc.create_entry(inp)
    assert created.id is not None
    assert created.title == "Lesson Learned"
    assert created.is_current is True

    fetched = svc.get_entry(created.id)
    assert fetched.id == created.id
    assert fetched.body == created.body


@pytest.mark.integration
def test_list_entries(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = MemoryService(db_session, stub_embedding_provider)
    svc.create_entry(MemoryEntryInput(title="Entry A", body="Content A."))
    svc.create_entry(MemoryEntryInput(title="Entry B", body="Content B."))
    entries = svc.list_entries()
    assert len(entries) >= 2


@pytest.mark.integration
def test_list_entries_filtered_by_source(
    db_session: Session,
    sample_document_id: uuid.UUID,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = MemoryService(db_session, stub_embedding_provider)
    svc.create_entry(
        MemoryEntryInput(
            title="Linked Entry",
            body="This entry traces back to a document.",
            source_type="document",
            source_id=sample_document_id,
        )
    )
    svc.create_entry(MemoryEntryInput(title="Unlinked", body="No source."))
    linked = svc.list_entries(source_id=sample_document_id)
    assert len(linked) >= 1
    assert all(e.source_id == sample_document_id for e in linked)


@pytest.mark.integration
def test_search_entries_returns_results(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = MemoryService(db_session, stub_embedding_provider)
    svc.create_entry(MemoryEntryInput(title="Retrieval Pattern", body="Hybrid search works."))
    results = svc.search_entries("hybrid search", top_k=5)
    assert len(results) >= 1


@pytest.mark.integration
def test_get_missing_entry_raises(
    db_session: Session,
    stub_embedding_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = MemoryService(db_session, stub_embedding_provider)
    with pytest.raises(SourceNotFoundError):
        svc.get_entry(uuid.uuid4())
