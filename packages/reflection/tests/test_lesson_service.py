"""Integration tests for LessonService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_reflection.dto import EvidenceInput, LessonInput
from eci_reflection.errors import (
    InvalidConfidenceError,
    LessonNotFoundError,
    SupersessionError,
)
from eci_reflection.lesson_service import LessonService


@pytest.mark.integration
def test_create_lesson_minimal(db_session: Session) -> None:
    svc = LessonService(db_session)
    out = svc.create_lesson(LessonInput(claim="Start with the hardest problem first"))
    assert out.id is not None
    assert out.claim == "Start with the hardest problem first"
    assert out.status == "active"
    assert out.confidence == "medium"
    assert out.scope == "global"
    assert out.evidence == []


@pytest.mark.integration
def test_create_lesson_with_evidence(db_session: Session, sample_goal_id: uuid.UUID) -> None:
    svc = LessonService(db_session)
    evidence = EvidenceInput(
        source_type="goal",
        source_id=sample_goal_id,
        summary="Goal completion showed the value of early automation.",
    )
    out = svc.create_lesson(
        LessonInput(
            claim="Automate before scaling",
            confidence="high",
            scope="project",
            evidence=[evidence],
        )
    )
    assert len(out.evidence) == 1
    assert out.evidence[0].source_type == "goal"
    assert out.evidence[0].source_id == sample_goal_id


@pytest.mark.integration
def test_get_lesson_not_found(db_session: Session) -> None:
    svc = LessonService(db_session)
    with pytest.raises(LessonNotFoundError):
        svc.get_lesson(uuid.uuid4())


@pytest.mark.integration
def test_invalid_confidence_raises(db_session: Session) -> None:
    svc = LessonService(db_session)
    with pytest.raises(InvalidConfidenceError):
        svc.create_lesson(LessonInput(claim="x", confidence="very_sure"))


@pytest.mark.integration
def test_list_lessons_filter_by_status(db_session: Session) -> None:
    svc = LessonService(db_session)
    svc.create_lesson(LessonInput(claim="Active lesson"))
    out_b = svc.create_lesson(LessonInput(claim="To be superseded"))
    svc.supersede(out_b.id, LessonInput(claim="Replacement lesson"))

    active = svc.list_lessons(status="active")
    assert any(l.claim == "Active lesson" for l in active)
    assert not any(l.claim == "To be superseded" for l in active)


@pytest.mark.integration
def test_supersede_creates_new_and_marks_old(db_session: Session) -> None:
    svc = LessonService(db_session)
    old = svc.create_lesson(LessonInput(claim="Old lesson"))
    new = svc.supersede(old.id, LessonInput(claim="Improved lesson", confidence="high"))

    assert new.supersedes_id == old.id
    assert new.status == "active"
    refreshed_old = svc.get_lesson(old.id)
    assert refreshed_old.status == "superseded"


@pytest.mark.integration
def test_supersede_already_superseded_raises(db_session: Session) -> None:
    svc = LessonService(db_session)
    old = svc.create_lesson(LessonInput(claim="Old"))
    svc.supersede(old.id, LessonInput(claim="First replacement"))
    with pytest.raises(SupersessionError):
        svc.supersede(old.id, LessonInput(claim="Second replacement — should fail"))


@pytest.mark.integration
def test_supersede_audit_recorded(db_session: Session) -> None:
    from sqlalchemy import select

    from eci_storage.models.audit import AuditEvent

    svc = LessonService(db_session)
    old = svc.create_lesson(LessonInput(claim="Will be superseded"))
    svc.supersede(old.id, LessonInput(claim="Successor"), actor="test_user")

    events = list(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.target_id == old.id,
                AuditEvent.action == "lesson.superseded",
            )
        )
    )
    assert len(events) == 1
    assert events[0].actor == "test_user"
    assert events[0].prior_state == {"status": "active"}
    assert events[0].new_state["status"] == "superseded"
