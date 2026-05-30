"""FastAPI dependency providers — DB session, blob store, services."""

from __future__ import annotations

from typing import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from eci_ingest import (
    DocumentIngestService,
    NoteIngestService,
    get_blob_store,
)
from eci_storage import sessionmaker_for


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


def get_document_service(
    session: Session = Depends(get_db),
) -> DocumentIngestService:
    return DocumentIngestService(session, blob_store=get_blob_store())


def get_note_service(session: Session = Depends(get_db)) -> NoteIngestService:
    return NoteIngestService(session)
