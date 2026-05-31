"""Integration tests for GoalService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_execution.dto import CitationInput, GoalInput, StatusUpdate
from eci_execution.errors import GoalNotFoundError, InvalidStatusError
from eci_execution.goal_service import GoalService


@pytest.mark.integration
def test_create_goal_minimal(db_session: Session) -> None:
    svc = GoalService(db_session)
    out = svc.create_goal(GoalInput(title="Improve test coverage"))
    assert out.id is not None
    assert out.title == "Improve test coverage"
    assert out.status == "pending"
    assert out.roadmap_id is None
    assert out.source_memory_id is None


@pytest.mark.integration
def test_create_goal_with_citations(db_session: Session, sample_memory_entry_id: uuid.UUID) -> None:
    svc = GoalService(db_session)
    citation = CitationInput(
        source_type="document",
        source_id=uuid.uuid4(),
        chunk_index=0,
        content="Engineering memory supports systematic knowledge retrieval.",
        score=0.87,
        title="Engineering Memory Doc",
        source_uri="file://test/doc.md",
    )
    out = svc.create_goal(
        GoalInput(
            title="Build retrieval pipeline",
            source_memory_id=sample_memory_entry_id,
            citations=[citation],
        )
    )
    assert out.source_memory_id == sample_memory_entry_id
    citations = svc.get_citations(out.id)
    assert len(citations) == 1
    assert citations[0].score == 0.87
    assert citations[0].source_type == "document"


@pytest.mark.integration
def test_get_goal_not_found(db_session: Session) -> None:
    svc = GoalService(db_session)
    with pytest.raises(GoalNotFoundError):
        svc.get_goal(uuid.uuid4())


@pytest.mark.integration
def test_list_goals_by_roadmap(db_session: Session) -> None:
    from eci_storage.models.roadmap import Roadmap

    roadmap = Roadmap(title="Q3 Roadmap")
    db_session.add(roadmap)
    db_session.flush()

    svc = GoalService(db_session)
    svc.create_goal(GoalInput(title="Goal A", roadmap_id=roadmap.id))
    svc.create_goal(GoalInput(title="Goal B", roadmap_id=roadmap.id))
    svc.create_goal(GoalInput(title="Goal C"))  # different roadmap

    results = svc.list_goals(roadmap_id=roadmap.id)
    titles = {r.title for r in results}
    assert titles == {"Goal A", "Goal B"}


@pytest.mark.integration
def test_update_status_records_audit(db_session: Session) -> None:
    from sqlalchemy import select

    from eci_storage.models.audit import AuditEvent

    svc = GoalService(db_session)
    out = svc.create_goal(GoalInput(title="Audited goal"))
    svc.update_status(out.id, StatusUpdate(status="in_progress", reason="Starting now"))

    events = list(
        db_session.scalars(
            select(AuditEvent).where(
                AuditEvent.target_id == out.id,
                AuditEvent.action == "goal.status_change",
            )
        )
    )
    assert len(events) == 1
    assert events[0].prior_state == {"status": "pending"}
    assert events[0].new_state == {"status": "in_progress"}
    assert events[0].reason == "Starting now"


@pytest.mark.integration
def test_update_status_invalid_raises(db_session: Session) -> None:
    svc = GoalService(db_session)
    out = svc.create_goal(GoalInput(title="Goal"))
    with pytest.raises(InvalidStatusError):
        svc.update_status(out.id, StatusUpdate(status="flying"))


@pytest.mark.integration
def test_get_citations_empty(db_session: Session) -> None:
    svc = GoalService(db_session)
    out = svc.create_goal(GoalInput(title="No citations goal"))
    assert svc.get_citations(out.id) == []
