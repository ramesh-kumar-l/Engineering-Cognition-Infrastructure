"""ECI ingest — public surface."""

from eci_ingest.blob_store import BlobStore, LocalBlobStore, get_blob_store
from eci_ingest.config import IngestConfig, load_ingest_config
from eci_ingest.document_service import DocumentIngestService, ingest_document
from eci_ingest.dto import (
    DocumentIngestRequest,
    DocumentIngestResult,
    DocumentListItem,
    DocumentRead,
    NoteIngestRequest,
    NoteIngestResult,
    NoteRead,
)
from eci_ingest.errors import IngestError, ParseError, SourceTooLarge, UnsupportedSource
from eci_ingest.hashing import content_hash_bytes, content_hash_text
from eci_ingest.note_service import NoteIngestService, ingest_note
from eci_ingest.read_service import SourceReadService

__all__ = [
    "BlobStore",
    "DocumentIngestRequest",
    "DocumentIngestResult",
    "DocumentListItem",
    "DocumentRead",
    "DocumentIngestService",
    "IngestConfig",
    "IngestError",
    "LocalBlobStore",
    "NoteIngestRequest",
    "NoteIngestResult",
    "NoteRead",
    "NoteIngestService",
    "ParseError",
    "SourceReadService",
    "SourceTooLarge",
    "UnsupportedSource",
    "content_hash_bytes",
    "content_hash_text",
    "get_blob_store",
    "ingest_document",
    "ingest_note",
    "load_ingest_config",
]
