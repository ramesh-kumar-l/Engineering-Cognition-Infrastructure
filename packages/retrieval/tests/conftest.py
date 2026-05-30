"""Shared fixtures for retrieval tests."""

from __future__ import annotations

import hashlib
import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from eci_llm.protocol import EmbeddingRequest, EmbeddingResponse

_ECI_TEST_DB_URL = os.getenv("ECI_TEST_DB_URL")


class StubEmbeddingProvider:
    """Returns deterministic hash-based embeddings — no Ollama required."""

    @property
    def model_name(self) -> str:
        return "stub-embed-0.1"

    @property
    def dimensions(self) -> int:
        return 768

    def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        embeddings = []
        for text in request.texts:
            raw = hashlib.md5(text.encode()).digest()  # 16 bytes
            vec = [float(b) / 255.0 for b in raw]
            vec += [0.0] * (768 - len(vec))
            embeddings.append(vec)
        return EmbeddingResponse(embeddings=embeddings, model="stub-embed-0.1")


@pytest.fixture
def stub_embedding_provider() -> StubEmbeddingProvider:
    return StubEmbeddingProvider()


@pytest.fixture(scope="session")
def db_engine():  # type: ignore[no-untyped-def]
    if not _ECI_TEST_DB_URL:
        pytest.skip("ECI_TEST_DB_URL not set — skipping integration tests")
    return create_engine(_ECI_TEST_DB_URL)


@pytest.fixture
def db_session(db_engine):  # type: ignore[no-untyped-def]
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
    from eci_storage.models import Document, RawBlob

    raw = b"Engineering memory is the foundation of systematic knowledge retrieval."
    h = hashlib.sha256(raw).hexdigest()
    blob = RawBlob(
        content_hash=h, size_bytes=len(raw), content_type="text/plain",
        storage_uri=f"file://test/{h}",
    )
    db_session.add(blob)
    db_session.flush()

    doc = Document(
        raw_blob_id=blob.id, kind="text",
        title="Test Retrieval Document",
        body=raw.decode(),
        source="test://retrieval-fixture",
        ingested_by="test",
    )
    db_session.add(doc)
    db_session.flush()
    return doc.id  # type: ignore[return-value]


@pytest.fixture
def sample_note_id(db_session: Session) -> uuid.UUID:
    from eci_storage.models import Note

    body = "Retrieval notes must carry citations to their source material."
    h = hashlib.sha256(body.encode()).hexdigest()
    note = Note(
        body=body, source="test://retrieval-fixture/note",
        content_hash=h, ingested_by="test",
    )
    db_session.add(note)
    db_session.flush()
    return note.id  # type: ignore[return-value]
