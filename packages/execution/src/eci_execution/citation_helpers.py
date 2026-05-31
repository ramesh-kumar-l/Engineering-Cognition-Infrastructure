"""Shared helpers for storing and converting ExecutionCitation records."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from eci_execution.dto import CitationInput, CitationOut
from eci_storage.models.execution_citation import ExecutionCitation


def store_citations(
    session: Session,
    target_type: str,
    target_id: uuid.UUID,
    citations: list[CitationInput],
) -> None:
    for c in citations:
        session.add(
            ExecutionCitation(
                target_type=target_type,
                target_id=target_id,
                source_type=c.source_type,
                source_id=c.source_id,
                chunk_index=c.chunk_index,
                content=c.content,
                score=c.score,
                title=c.title,
                source_uri=c.source_uri,
            )
        )


def to_citation_out(c: ExecutionCitation) -> CitationOut:
    return CitationOut(
        target_type=c.target_type,
        target_id=c.target_id,
        source_type=c.source_type,
        source_id=c.source_id,
        chunk_index=c.chunk_index,
        content=c.content,
        score=c.score,
        title=c.title,
        source_uri=c.source_uri,
    )
