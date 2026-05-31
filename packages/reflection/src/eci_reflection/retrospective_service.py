"""RetrospectiveService — create and run retrospective reflection cycles."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from eci_llm.protocol import LLMProvider
from eci_observability import get_logger
from eci_reflection.dto import (
    VALID_CADENCES,
    LessonInput,
    RetrospectiveInput,
    RetrospectiveOut,
)
from eci_reflection.errors import InvalidCadenceError, RetrospectiveNotFoundError
from eci_reflection.lesson_service import LessonService
from eci_reflection.pattern_extractor import PatternExtractor
from eci_storage.models.base import utcnow
from eci_storage.models.goal import Goal
from eci_storage.models.retrospective import Retrospective
from eci_storage.models.task import Task

_log = get_logger("eci_reflection.retrospective_service")


def _to_retro_out(r: Retrospective) -> RetrospectiveOut:
    return RetrospectiveOut(
        id=r.id,
        cadence=r.cadence,
        scope_type=r.scope_type,
        scope_id=r.scope_id,
        status=r.status,
        started_at=r.started_at,
        completed_at=r.completed_at,
        notes=r.notes,
        lesson_count=r.lesson_count,
        created_at=r.created_at,
        updated_at=r.updated_at,
    )


def _collect_items(
    session: Session,
    scope_type: str | None,
    scope_id: uuid.UUID | None,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    goal_stmt = select(Goal).where(Goal.status == "completed")
    if scope_type == "roadmap" and scope_id is not None:
        goal_stmt = goal_stmt.where(Goal.roadmap_id == scope_id)
    elif scope_type == "goal" and scope_id is not None:
        goal_stmt = goal_stmt.where(Goal.id == scope_id)

    for g in session.scalars(goal_stmt):
        items.append({
            "type": "goal",
            "id": str(g.id),
            "title": g.title,
            "description": g.description or "",
        })

    task_stmt = select(Task).where(Task.status == "completed")
    if scope_type == "goal" and scope_id is not None:
        task_stmt = task_stmt.where(Task.goal_id == scope_id)
    elif scope_type == "roadmap" and scope_id is not None:
        goal_ids = [g["id"] for g in items if g["type"] == "goal"]
        if goal_ids:
            task_stmt = task_stmt.where(
                Task.goal_id.in_([uuid.UUID(gid) for gid in goal_ids])
            )

    for t in session.scalars(task_stmt):
        items.append({
            "type": "task",
            "id": str(t.id),
            "title": t.title,
            "description": t.description or "",
        })

    return items


class RetrospectiveService:
    def __init__(self, session: Session, provider: LLMProvider) -> None:
        self._session = session
        self._provider = provider

    def create_and_run(self, inp: RetrospectiveInput) -> RetrospectiveOut:
        if inp.cadence not in VALID_CADENCES:
            raise InvalidCadenceError(f"Unknown cadence: {inp.cadence!r}")

        retro = Retrospective(
            cadence=inp.cadence,
            scope_type=inp.scope_type,
            scope_id=inp.scope_id,
            status="running",
            started_at=utcnow(),
            notes=inp.notes,
        )
        self._session.add(retro)
        self._session.flush()

        _log.info("retrospective.started", retro_id=str(retro.id), cadence=inp.cadence)

        try:
            items = _collect_items(self._session, inp.scope_type, inp.scope_id)
            extractor = PatternExtractor(self._provider)
            lesson_inputs: list[LessonInput] = extractor.extract(items)

            lesson_svc = LessonService(self._session)
            count = 0
            for li in lesson_inputs:
                li = LessonInput(
                    claim=li.claim,
                    evidence=li.evidence,
                    scope=li.scope,
                    confidence=li.confidence,
                    retrospective_id=retro.id,
                )
                lesson_svc.create_lesson(li)
                count += 1

            retro.status = "completed"
            retro.completed_at = utcnow()
            retro.lesson_count = count
            retro.updated_at = utcnow()
        except Exception as exc:
            retro.status = "failed"
            retro.updated_at = utcnow()
            _log.error("retrospective.failed", retro_id=str(retro.id), error=str(exc))
            self._session.flush()
            raise

        self._session.flush()
        _log.info("retrospective.completed", retro_id=str(retro.id), lessons=count)
        return _to_retro_out(retro)

    def get_retrospective(self, retro_id: uuid.UUID) -> RetrospectiveOut:
        retro = self._session.get(Retrospective, retro_id)
        if retro is None:
            raise RetrospectiveNotFoundError(f"Retrospective {retro_id} not found")
        return _to_retro_out(retro)

    def list_retrospectives(self) -> list[RetrospectiveOut]:
        stmt = select(Retrospective).order_by(Retrospective.started_at.desc())
        return [_to_retro_out(r) for r in self._session.scalars(stmt)]
