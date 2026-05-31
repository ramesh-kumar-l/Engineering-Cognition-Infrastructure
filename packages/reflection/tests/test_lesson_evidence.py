"""Integration tests for lesson evidence storage and retrieval."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_reflection.dto import EvidenceInput, LessonInput
from eci_reflection.lesson_service import LessonService
from eci_storage.models.lesson_evidence import LessonEvidence


@pytest.mark.integration
def test_evidence_stored_on_create(
    db_session: Session,
    sample_goal_id: uuid.UUID,
    sample_task_id: uuid.UUID,
) -> None:
    svc = LessonService(db_session)
    out = svc.create_lesson(
        LessonInput(
            claim="Multi-evidence lesson",
            evidence=[
                EvidenceInput(
                    source_type="goal",
                    source_id=sample_goal_id,
                    summary="Goal showed pattern A",
                ),
                EvidenceInput(
                    source_type="task",
                    source_id=sample_task_id,
                    summary="Task confirmed pattern A",
                ),
            ],
        )
    )
    rows = list(
        db_session.scalars(
            select(LessonEvidence).where(LessonEvidence.lesson_id == out.id)
        )
    )
    assert len(rows) == 2
    source_types = {r.source_type for r in rows}
    assert source_types == {"goal", "task"}


@pytest.mark.integration
def test_evidence_cascades_on_lesson_delete(db_session: Session) -> None:
    from eci_storage.models.lesson import Lesson

    svc = LessonService(db_session)
    out = svc.create_lesson(
        LessonInput(
            claim="Lesson to delete",
            evidence=[
                EvidenceInput(
                    source_type="goal",
                    source_id=uuid.uuid4(),
                    summary="Supporting evidence",
                )
            ],
        )
    )
    lesson_id = out.id
    lesson = db_session.get(Lesson, lesson_id)
    assert lesson is not None

    db_session.delete(lesson)
    db_session.flush()

    remaining = list(
        db_session.scalars(
            select(LessonEvidence).where(LessonEvidence.lesson_id == lesson_id)
        )
    )
    assert remaining == []


@pytest.mark.integration
def test_lesson_no_evidence_returns_empty_list(db_session: Session) -> None:
    svc = LessonService(db_session)
    out = svc.create_lesson(LessonInput(claim="No evidence provided"))
    assert out.evidence == []
