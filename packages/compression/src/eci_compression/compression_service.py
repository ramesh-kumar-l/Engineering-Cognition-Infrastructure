"""Compression pipeline orchestrator.

Fetches a Document or Note from the DB, runs summarization + mental-model
extraction + playbook extraction, persists the results, and returns a
CompressionResult DTO. Each stage emits a trace span and is independently
re-runnable (re-running overwrites previous summaries and mental model for
the same source).
"""

from __future__ import annotations

import dataclasses
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_llm.protocol import LLMProvider
from eci_observability import get_logger, get_tracer
from eci_storage.models import Document, Note
from eci_storage.models.mental_model import MentalModel
from eci_storage.models.summary import Summary

from eci_compression.config import CompressionConfig, load_compression_config
from eci_compression.dto import (
    CompressionRequest,
    CompressionResult,
    MentalModelResult,
    PlaybookResult,
    SourceType,
    SummaryResult,
)
from eci_compression.errors import SourceNotFound
from eci_compression.mental_model import MentalModelService
from eci_compression.playbook import PlaybookService
from eci_compression.summarizer import SummarizationService

_log = get_logger("eci_compression.service")
_tracer = get_tracer("eci_compression")


class CompressionService:
    """Runs the full compression pipeline for a single Document or Note."""

    def __init__(
        self,
        session: Session,
        provider: LLMProvider,
        config: CompressionConfig | None = None,
    ) -> None:
        self.session = session
        self.config = config or load_compression_config()
        self._summarizer = SummarizationService(provider)
        self._mental_model = MentalModelService(provider)
        self._playbook = PlaybookService(provider)

    def compress(self, request: CompressionRequest) -> CompressionResult:
        with _tracer.start_as_current_span("compression.run") as span:
            span.set_attribute("compression.source_type", request.source_type.value)
            span.set_attribute("compression.source_id", str(request.source_id))

            content, source_hash = self._fetch_content(request)
            content = content[: self.config.max_content_chars]

            doc_id = request.source_id if request.source_type == SourceType.DOCUMENT else None
            note_id = request.source_id if request.source_type == SourceType.NOTE else None

            summaries = self._summarizer.summarize_all_levels(content)
            mental_model = self._mental_model.extract(content)
            playbook = (
                self._playbook.extract(content) if self.config.extract_playbooks else None
            )

            self._persist_summaries(doc_id, note_id, source_hash, summaries)
            self._persist_mental_model(doc_id, note_id, source_hash, mental_model, playbook)
            self.session.flush()

            _log.info(
                "compression.complete",
                source_type=request.source_type.value,
                source_id=str(request.source_id),
                summaries=len(summaries),
            )
            return CompressionResult(
                source_id=request.source_id,
                source_type=request.source_type,
                summaries=summaries,
                mental_model=mental_model,
                playbook=playbook,
                compressed_at=datetime.now(timezone.utc),
            )

    def _fetch_content(self, request: CompressionRequest) -> tuple[str, str]:
        if request.source_type == SourceType.DOCUMENT:
            doc = self.session.scalar(select(Document).where(Document.id == request.source_id))
            if doc is None:
                raise SourceNotFound(f"Document {request.source_id} not found")
            return doc.body, doc.raw_blob.content_hash
        note = self.session.scalar(select(Note).where(Note.id == request.source_id))
        if note is None:
            raise SourceNotFound(f"Note {request.source_id} not found")
        return note.body, note.content_hash

    def _persist_summaries(
        self,
        doc_id: uuid.UUID | None,
        note_id: uuid.UUID | None,
        source_hash: str,
        summaries: list[SummaryResult],
    ) -> None:
        for result in summaries:
            self.session.add(
                Summary(
                    document_id=doc_id,
                    note_id=note_id,
                    level=result.level.value,
                    content=result.content,
                    source_hash=source_hash,
                    word_count=result.word_count,
                    model_used=result.model_used,
                )
            )

    def _persist_mental_model(
        self,
        doc_id: uuid.UUID | None,
        note_id: uuid.UUID | None,
        source_hash: str,
        mental_model: MentalModelResult,
        playbook: PlaybookResult | None,
    ) -> None:
        playbook_data: dict[str, Any] | None = None
        if playbook and playbook.title:
            playbook_data = {
                "title": playbook.title,
                "applicable_when": playbook.applicable_when,
                "parameters": playbook.parameters,
                "steps": playbook.steps,
            }
        self.session.add(
            MentalModel(
                document_id=doc_id,
                note_id=note_id,
                claims=mental_model.claims,
                entities=[dataclasses.asdict(e) for e in mental_model.entities],
                relationships=[dataclasses.asdict(r) for r in mental_model.relationships],
                playbook=playbook_data,
                source_hash=source_hash,
                model_used=mental_model.model_used,
            )
        )
