"""FastAPI dependency providers — DB session, blob store, services."""

from __future__ import annotations

from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from eci_compression.compression_service import CompressionService
from eci_ingest import (
    DocumentIngestService,
    NoteIngestService,
    get_blob_store,
)
from eci_llm import LLMProvider, create_llm_provider
from eci_storage import sessionmaker_for

# Process-level LLM provider singleton (created on first request).
_llm_provider: LLMProvider | None = None


def get_db() -> Iterator[Session]:
    """Yield a Session, commit on success, rollback on error."""
    factory = sessionmaker_for()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_llm_provider() -> LLMProvider:
    """Return the process-level LLM provider. Created once on first call."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = create_llm_provider()
    return _llm_provider


def get_document_service(
    session: Session = Depends(get_db),
) -> DocumentIngestService:
    return DocumentIngestService(session, blob_store=get_blob_store())


def get_note_service(session: Session = Depends(get_db)) -> NoteIngestService:
    return NoteIngestService(session)


def get_compression_service(
    session: Session = Depends(get_db),
    provider: LLMProvider = Depends(get_llm_provider),
) -> CompressionService:
    return CompressionService(session, provider)
