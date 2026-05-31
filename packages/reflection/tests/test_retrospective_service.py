"""Integration tests for RetrospectiveService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_reflection.dto import RetrospectiveInput
from eci_reflection.errors import InvalidCadenceError, RetrospectiveNotFoundError
from eci_reflection.lesson_service import LessonService
from eci_reflection.retrospective_service import RetrospectiveService


@pytest.mark.integration
def test_create_and_run_produces_lessons(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
    sample_goal_id: uuid.UUID,
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    out = svc.create_and_run(RetrospectiveInput(cadence="weekly"))

    assert out.status == "completed"
    assert out.lesson_count == 1
    assert out.cadence == "weekly"


@pytest.mark.integration
def test_run_with_empty_provider_completes_zero_lessons(
    db_session: Session,
    empty_llm_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = RetrospectiveService(db_session, empty_llm_provider)
    out = svc.create_and_run(RetrospectiveInput(cadence="monthly"))

    assert out.status == "completed"
    assert out.lesson_count == 0


@pytest.mark.integration
def test_lessons_cite_retrospective(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
    sample_goal_id: uuid.UUID,
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    retro = svc.create_and_run(RetrospectiveInput(cadence="milestone"))

    lesson_svc = LessonService(db_session)
    lessons = lesson_svc.list_lessons(retrospective_id=retro.id)
    assert len(lessons) == 1
    assert lessons[0].retrospective_id == retro.id


@pytest.mark.integration
def test_get_retrospective_not_found(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    with pytest.raises(RetrospectiveNotFoundError):
        svc.get_retrospective(uuid.uuid4())


@pytest.mark.integration
def test_invalid_cadence_raises(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    with pytest.raises(InvalidCadenceError):
        svc.create_and_run(RetrospectiveInput(cadence="quarterly"))


@pytest.mark.integration
def test_scoped_retrospective_goal(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
    sample_goal_id: uuid.UUID,
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    out = svc.create_and_run(
        RetrospectiveInput(cadence="milestone", scope_type="goal", scope_id=sample_goal_id)
    )
    assert out.status == "completed"
    assert out.scope_type == "goal"
    assert out.scope_id == sample_goal_id


@pytest.mark.integration
def test_list_retrospectives(
    db_session: Session,
    stub_llm_provider,  # type: ignore[no-untyped-def]
) -> None:
    svc = RetrospectiveService(db_session, stub_llm_provider)
    svc.create_and_run(RetrospectiveInput(cadence="weekly"))
    svc.create_and_run(RetrospectiveInput(cadence="monthly"))
    all_retros = svc.list_retrospectives()
    assert len(all_retros) >= 2
