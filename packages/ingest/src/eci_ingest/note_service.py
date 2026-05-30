"""Note ingest service. Inline body, no raw blob."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_ingest.audit import record_audit
from eci_ingest.config import IngestConfig, load_ingest_config
from eci_ingest.dto import NoteIngestRequest, NoteIngestResult
from eci_ingest.errors import SourceTooLarge
from eci_ingest.hashing import content_hash_text
from eci_observability import (
    get_logger,
    get_tracer,
    ingest_counter,
)
from eci_storage.models import Note

_log = get_logger("eci_ingest.note")
_tracer = get_tracer("eci_ingest")


class NoteIngestService:
    def __init__(
        self,
        session: Session,
        config: IngestConfig | None = None,
    ) -> None:
        self.session = session
        self.config = config or load_ingest_config()

    def ingest(self, request: NoteIngestRequest) -> NoteIngestResult:
        with _tracer.start_as_current_span("ingest.note") as span:
            span.set_attribute("ingest.source", request.source)
            span.set_attribute("ingest.size_bytes", len(request.body.encode("utf-8")))

            if len(request.body.encode("utf-8")) > self.config.ingest_max_bytes:
                ingest_counter.labels(source_kind="note", outcome="too_large").inc()
                raise SourceTooLarge("note body too large")

            hash_hex = content_hash_text(
                request.body,
                request.source,
                request.author or "",
                request.captured_at.isoformat() if request.captured_at else "",
            )
            span.set_attribute("ingest.content_hash", hash_hex)

            existing = self.session.scalar(
                select(Note).where(Note.content_hash == hash_hex)
            )
            if existing is not None:
                record_audit(
                    self.session,
                    actor=request.ingested_by,
                    action="ingest.note.dedup",
                    target_type="note",
                    target_id=existing.id,
                    new_state={"content_hash": hash_hex},
                    reason="content_hash collision; returning existing record",
                )
                ingest_counter.labels(source_kind="note", outcome="dedup").inc()
                _log.info(
                    "ingest.note.dedup",
                    note_id=str(existing.id),
                    content_hash=hash_hex,
                )
                return NoteIngestResult(
                    id=existing.id,
                    content_hash=hash_hex,
                    source=existing.source,
                    deduplicated=True,
                    ingested_at=existing.ingested_at,
                )

            note = Note(
                body=request.body,
                source=request.source,
                author=request.author,
                tags=list(request.tags),
                meta=dict(request.metadata),
                captured_at=request.captured_at,
                ingested_by=request.ingested_by,
                content_hash=hash_hex,
            )
            self.session.add(note)
            self.session.flush()

            record_audit(
                self.session,
                actor=request.ingested_by,
                action="ingest.note.create",
                target_type="note",
                target_id=note.id,
                new_state={"source": note.source, "content_hash": hash_hex},
            )
            ingest_counter.labels(source_kind="note", outcome="created").inc()
            _log.info(
                "ingest.note.created",
                note_id=str(note.id),
                content_hash=hash_hex,
                source=request.source,
            )
            return NoteIngestResult(
                id=note.id,
                content_hash=hash_hex,
                source=note.source,
                deduplicated=False,
                ingested_at=note.ingested_at,
            )


def ingest_note(session: Session, request: NoteIngestRequest) -> NoteIngestResult:
    return NoteIngestService(session).ingest(request)
