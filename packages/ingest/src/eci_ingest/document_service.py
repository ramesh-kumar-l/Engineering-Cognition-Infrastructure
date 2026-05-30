"""Document ingest service.

End-to-end:
1. Size check.
2. Compute content_hash.
3. Idempotency: if a RawBlob with this hash exists, return its Document.
4. Otherwise: write blob, parse, insert RawBlob + Document, audit.

Trace + Prometheus metrics emitted around the whole op.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_ingest.audit import record_audit
from eci_ingest.blob_store import BlobStore, get_blob_store
from eci_ingest.config import IngestConfig, load_ingest_config
from eci_ingest.dto import DocumentIngestRequest, DocumentIngestResult
from eci_ingest.errors import SourceTooLarge
from eci_ingest.hashing import content_hash_bytes
from eci_ingest.parsers import parse
from eci_observability import (
    get_logger,
    get_tracer,
    ingest_bytes,
    ingest_counter,
)
from eci_storage.models import Document, RawBlob

_log = get_logger("eci_ingest.document")
_tracer = get_tracer("eci_ingest")


class DocumentIngestService:
    """Per-call instance is fine; no per-instance state."""

    def __init__(
        self,
        session: Session,
        blob_store: BlobStore | None = None,
        config: IngestConfig | None = None,
    ) -> None:
        self.session = session
        self.config = config or load_ingest_config()
        self.blob_store = blob_store or get_blob_store(self.config)

    def ingest(
        self, request: DocumentIngestRequest, raw: bytes
    ) -> DocumentIngestResult:
        with _tracer.start_as_current_span("ingest.document") as span:
            span.set_attribute("ingest.kind", request.kind)
            span.set_attribute("ingest.source", request.source)
            span.set_attribute("ingest.size_bytes", len(raw))

            if len(raw) > self.config.ingest_max_bytes:
                ingest_counter.labels(source_kind="document", outcome="too_large").inc()
                raise SourceTooLarge(
                    f"{len(raw)} > {self.config.ingest_max_bytes}"
                )

            hash_hex = content_hash_bytes(raw)
            span.set_attribute("ingest.content_hash", hash_hex)

            existing_blob = self.session.scalar(
                select(RawBlob).where(RawBlob.content_hash == hash_hex)
            )
            if existing_blob is not None:
                existing_doc = self.session.scalar(
                    select(Document).where(Document.raw_blob_id == existing_blob.id)
                )
                if existing_doc is not None:
                    return self._dedup_result(existing_doc, hash_hex)

            content_type = _content_type_for(request.kind)
            storage_uri = self.blob_store.put(hash_hex, raw)
            blob = existing_blob or RawBlob(
                content_hash=hash_hex,
                size_bytes=len(raw),
                content_type=content_type,
                storage_uri=storage_uri,
            )
            if existing_blob is None:
                self.session.add(blob)
                self.session.flush()

            parsed = parse(request.kind, raw)
            doc = Document(
                raw_blob_id=blob.id,
                kind=request.kind,
                title=request.title or parsed.title,
                body=parsed.body,
                source=request.source,
                author=request.author,
                tags=list(request.tags),
                meta={**parsed.metadata, **request.metadata},
                captured_at=request.captured_at,
                ingested_by=request.ingested_by,
            )
            self.session.add(doc)
            self.session.flush()

            record_audit(
                self.session,
                actor=request.ingested_by,
                action="ingest.document.create",
                target_type="document",
                target_id=doc.id,
                new_state={
                    "kind": doc.kind,
                    "source": doc.source,
                    "content_hash": hash_hex,
                },
                reason=None,
            )

            ingest_counter.labels(source_kind="document", outcome="created").inc()
            ingest_bytes.labels(source_kind="document").inc(len(raw))
            _log.info(
                "ingest.document.created",
                doc_id=str(doc.id),
                content_hash=hash_hex,
                source=request.source,
            )
            return DocumentIngestResult(
                id=doc.id,
                content_hash=hash_hex,
                kind=request.kind,
                title=doc.title,
                source=doc.source,
                deduplicated=False,
                ingested_at=doc.ingested_at,
            )

    def _dedup_result(
        self, existing: Document, hash_hex: str
    ) -> DocumentIngestResult:
        record_audit(
            self.session,
            actor=existing.ingested_by,
            action="ingest.document.dedup",
            target_type="document",
            target_id=existing.id,
            new_state={"content_hash": hash_hex},
            reason="content_hash collision; returning existing record",
        )
        ingest_counter.labels(source_kind="document", outcome="dedup").inc()
        _log.info(
            "ingest.document.dedup",
            doc_id=str(existing.id),
            content_hash=hash_hex,
        )
        # Cast kind to the literal type the DTO expects.
        from typing import cast

        from eci_ingest.dto import DocumentKind

        return DocumentIngestResult(
            id=existing.id,
            content_hash=hash_hex,
            kind=cast(DocumentKind, existing.kind),
            title=existing.title,
            source=existing.source,
            deduplicated=True,
            ingested_at=existing.ingested_at,
        )


def ingest_document(
    session: Session, request: DocumentIngestRequest, raw: bytes
) -> DocumentIngestResult:
    """Convenience: build a service and run one ingest."""
    return DocumentIngestService(session).ingest(request, raw)


def _content_type_for(kind: str) -> str:
    return {
        "markdown": "text/markdown",
        "text": "text/plain",
        "pdf": "application/pdf",
    }.get(kind, "application/octet-stream")
