"""Shared fixtures for compression tests.

Stub providers are returned by fixtures. Test files that need to subclass
them should define their own minimal stub classes directly.
"""

from __future__ import annotations

import hashlib
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from eci_llm.protocol import LLMRequest, LLMResponse

_ECI_TEST_DB_URL = os.getenv("ECI_TEST_DB_URL")


# ---------------------------------------------------------------------------
# Stub LLM providers — module-level so tests can subclass if needed.
# ---------------------------------------------------------------------------


class StubLLMProvider:
    """Returns a fixed text response for any request."""

    def __init__(self, response_content: str = "stub summary") -> None:
        self._response = response_content

    @property
    def model_name(self) -> str:
        return "stub-0.1"

    def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=self._response, model="stub-0.1", prompt_tokens=10, completion_tokens=5
        )


class JsonStubLLMProvider(StubLLMProvider):
    """Returns valid mental-model JSON for any request."""

    def complete(self, request: LLMRequest) -> LLMResponse:
        content = (
            '{"claims": ["test claim"], '
            '"entities": [{"name": "TestEntity", "type": "concept", '
            '"description": "a test entity"}], '
            '"relationships": [{"subject": "TestEntity", "predicate": "is", '
            '"object": "test"}]}'
        )
        return LLMResponse(content=content, model="stub-0.1")


@pytest.fixture
def stub_provider() -> StubLLMProvider:
    return StubLLMProvider()


@pytest.fixture
def json_stub_provider() -> JsonStubLLMProvider:
    return JsonStubLLMProvider()


# ---------------------------------------------------------------------------
# Real-Postgres fixtures — skipped when ECI_TEST_DB_URL is unset.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def db_engine():  # type: ignore[no-untyped-def]
    if not _ECI_TEST_DB_URL:
        pytest.skip("ECI_TEST_DB_URL not set — skipping integration tests")
    return create_engine(_ECI_TEST_DB_URL)


@pytest.fixture
def db_session(db_engine):  # type: ignore[no-untyped-def]
    """Per-test transactional session — rolls back after each test."""
    conn = db_engine.connect()
    txn = conn.begin()
    factory = sessionmaker(bind=conn)
    session: Session = factory()
    yield session
    session.close()
    txn.rollback()
    conn.close()


@pytest.fixture
def sample_document_id(db_session: Session) -> uuid.UUID:
    """Insert a minimal Document into the DB without using the ingest service."""
    from eci_storage.models import Document, RawBlob

    raw = b"This is a test document about knowledge management and engineering systems."
    h = hashlib.sha256(raw).hexdigest()
    blob = RawBlob(
        content_hash=h,
        size_bytes=len(raw),
        content_type="text/plain",
        storage_uri=f"file://test/{h}",
    )
    db_session.add(blob)
    db_session.flush()

    doc = Document(
        raw_blob_id=blob.id,
        kind="text",
        title="Test Document",
        body=raw.decode(),
        source="test://fixture",
        ingested_by="test",
    )
    db_session.add(doc)
    db_session.flush()
    return doc.id  # type: ignore[return-value]


@pytest.fixture
def sample_note_id(db_session: Session) -> uuid.UUID:
    """Insert a minimal Note into the DB."""
    from eci_storage.models import Note

    body = "This is a short engineering note about debugging production issues."
    h = hashlib.sha256(body.encode()).hexdigest()
    note = Note(
        body=body,
        source="test://fixture/note",
        content_hash=h,
        ingested_by="test",
    )
    db_session.add(note)
    db_session.flush()
    return note.id  # type: ignore[return-value]
