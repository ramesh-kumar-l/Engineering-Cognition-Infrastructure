"""Helpers for storing and serializing lesson evidence."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from eci_reflection.dto import EvidenceInput, EvidenceOut
from eci_storage.models.lesson_evidence import LessonEvidence


def store_evidence(
    session: Session,
    lesson_id: uuid.UUID,
    items: list[EvidenceInput],
) -> None:
    for item in items:
        session.add(
            LessonEvidence(
                lesson_id=lesson_id,
                source_type=item.source_type,
                source_id=item.source_id,
                summary=item.summary,
            )
        )


def to_evidence_out(e: LessonEvidence) -> EvidenceOut:
    return EvidenceOut(
        id=e.id,
        lesson_id=e.lesson_id,
        source_type=e.source_type,
        source_id=e.source_id,
        summary=e.summary,
    )
