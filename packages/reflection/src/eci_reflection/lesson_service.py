"""LessonService — CRUD, supersession, and evidence retrieval for lessons."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_observability import get_logger
from eci_reflection.dto import (
    VALID_CONFIDENCES,
    VALID_SCOPES,
    EvidenceOut,
    LessonInput,
    LessonOut,
)
from eci_reflection.errors import (
    InvalidConfidenceError,
    LessonNotFoundError,
    SupersessionError,
)
from eci_reflection.evidence_helpers import store_evidence, to_evidence_out
from eci_storage.models.audit import AuditEvent
from eci_storage.models.base import utcnow
from eci_storage.models.lesson import Lesson
from eci_storage.models.lesson_evidence import LessonEvidence

_log = get_logger("eci_reflection.lesson_service")


def _load_evidence(session: Session, lesson_id: uuid.UUID) -> list[EvidenceOut]:
    rows = session.scalars(
        select(LessonEvidence).where(LessonEvidence.lesson_id == lesson_id)
    )
    return [to_evidence_out(r) for r in rows]


def _to_lesson_out(lesson: Lesson, session: Session) -> LessonOut:
    return LessonOut(
        id=lesson.id,
        retrospective_id=lesson.retrospective_id,
        claim=lesson.claim,
        scope=lesson.scope,
        confidence=lesson.confidence,
        status=lesson.status,
        supersedes_id=lesson.supersedes_id,
        evidence=_load_evidence(session, lesson.id),
        created_at=lesson.created_at,
        updated_at=lesson.updated_at,
    )


class LessonService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_lesson(self, inp: LessonInput) -> LessonOut:
        if inp.confidence not in VALID_CONFIDENCES:
            raise InvalidConfidenceError(f"Unknown confidence: {inp.confidence!r}")
        if inp.scope not in VALID_SCOPES:
            inp = LessonInput(
                claim=inp.claim,
                evidence=inp.evidence,
                scope="global",
                confidence=inp.confidence,
                retrospective_id=inp.retrospective_id,
                supersedes_id=inp.supersedes_id,
            )

        lesson = Lesson(
            retrospective_id=inp.retrospective_id,
            claim=inp.claim,
            scope=inp.scope,
            confidence=inp.confidence,
            status="active",
            supersedes_id=inp.supersedes_id,
        )
        self._session.add(lesson)
        self._session.flush()

        store_evidence(self._session, lesson.id, inp.evidence)
        self._session.flush()

        _log.info("lesson.created", lesson_id=str(lesson.id), confidence=inp.confidence)
        return _to_lesson_out(lesson, self._session)

    def get_lesson(self, lesson_id: uuid.UUID) -> LessonOut:
        lesson = self._session.get(Lesson, lesson_id)
        if lesson is None:
            raise LessonNotFoundError(f"Lesson {lesson_id} not found")
        return _to_lesson_out(lesson, self._session)

    def list_lessons(
        self,
        retrospective_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[LessonOut]:
        stmt = select(Lesson).order_by(Lesson.created_at)
        if retrospective_id is not None:
            stmt = stmt.where(Lesson.retrospective_id == retrospective_id)
        if status is not None:
            stmt = stmt.where(Lesson.status == status)
        return [_to_lesson_out(l, self._session) for l in self._session.scalars(stmt)]

    def supersede(
        self,
        old_lesson_id: uuid.UUID,
        new_inp: LessonInput,
        actor: str = "system",
    ) -> LessonOut:
        old = self._session.get(Lesson, old_lesson_id)
        if old is None:
            raise LessonNotFoundError(f"Lesson {old_lesson_id} not found")
        if old.status != "active":
            raise SupersessionError(f"Lesson {old_lesson_id} is already {old.status}")

        new_inp = LessonInput(
            claim=new_inp.claim,
            evidence=new_inp.evidence,
            scope=new_inp.scope,
            confidence=new_inp.confidence,
            retrospective_id=new_inp.retrospective_id,
            supersedes_id=old_lesson_id,
        )
        new_lesson_out = self.create_lesson(new_inp)

        old.status = "superseded"
        old.updated_at = utcnow()
        self._session.add(
            AuditEvent(
                actor=actor,
                action="lesson.superseded",
                target_type="lesson",
                target_id=old_lesson_id,
                prior_state={"status": "active"},
                new_state={"status": "superseded", "superseded_by": str(new_lesson_out.id)},
                reason=f"Superseded by lesson {new_lesson_out.id}",
            )
        )
        self._session.flush()
        _log.info("lesson.superseded", old_id=str(old_lesson_id), new_id=str(new_lesson_out.id))
        return new_lesson_out
