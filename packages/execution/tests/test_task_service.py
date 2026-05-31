"""Integration tests for TaskService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_execution.dto import CitationInput, GoalInput, StatusUpdate, TaskInput
from eci_execution.errors import DependencyCycleError, TaskNotFoundError
from eci_execution.goal_service import GoalService
from eci_execution.task_service import TaskService


@pytest.mark.integration
def test_create_task_standalone(db_session: Session) -> None:
    svc = TaskService(db_session)
    out = svc.create_task(TaskInput(title="Standalone task"))
    assert out.id is not None
    assert out.status == "pending"
    assert out.goal_id is None


@pytest.mark.integration
def test_create_task_linked_to_goal(db_session: Session) -> None:
    goal = GoalService(db_session).create_goal(GoalInput(title="Parent goal"))
    svc = TaskService(db_session)
    task = svc.create_task(TaskInput(title="Child task", goal_id=goal.id, position=1))
    assert task.goal_id == goal.id
    assert task.position == 1


@pytest.mark.integration
def test_create_task_with_citations(db_session: Session) -> None:
    svc = TaskService(db_session)
    citation = CitationInput(
        source_type="note",
        source_id=uuid.uuid4(),
        chunk_index=2,
        content="Setup CI pipeline documentation.",
        score=0.72,
        title="CI Note",
        source_uri=None,
    )
    task = svc.create_task(TaskInput(title="Setup CI", citations=[citation]))
    cits = svc.get_citations(task.id)
    assert len(cits) == 1
    assert cits[0].chunk_index == 2
    assert cits[0].target_type == "task"


@pytest.mark.integration
def test_get_task_not_found(db_session: Session) -> None:
    svc = TaskService(db_session)
    with pytest.raises(TaskNotFoundError):
        svc.get_task(uuid.uuid4())


@pytest.mark.integration
def test_list_tasks_by_goal(db_session: Session) -> None:
    goal = GoalService(db_session).create_goal(GoalInput(title="Goal"))
    svc = TaskService(db_session)
    svc.create_task(TaskInput(title="T1", goal_id=goal.id))
    svc.create_task(TaskInput(title="T2", goal_id=goal.id))
    svc.create_task(TaskInput(title="T3"))  # no goal

    tasks = svc.list_tasks(goal_id=goal.id)
    assert {t.title for t in tasks} == {"T1", "T2"}


@pytest.mark.integration
def test_dependency_added_successfully(db_session: Session) -> None:
    svc = TaskService(db_session)
    t_a = svc.create_task(TaskInput(title="A"))
    t_b = svc.create_task(TaskInput(title="B"))
    svc.add_dependency(upstream_id=t_a.id, downstream_id=t_b.id)
    # No exception = success


@pytest.mark.integration
def test_self_dependency_raises_cycle(db_session: Session) -> None:
    svc = TaskService(db_session)
    t = svc.create_task(TaskInput(title="Self-loop"))
    with pytest.raises(DependencyCycleError):
        svc.add_dependency(upstream_id=t.id, downstream_id=t.id)


@pytest.mark.integration
def test_transitive_cycle_detected(db_session: Session) -> None:
    svc = TaskService(db_session)
    a = svc.create_task(TaskInput(title="A"))
    b = svc.create_task(TaskInput(title="B"))
    c = svc.create_task(TaskInput(title="C"))
    svc.add_dependency(upstream_id=a.id, downstream_id=b.id)
    svc.add_dependency(upstream_id=b.id, downstream_id=c.id)
    with pytest.raises(DependencyCycleError):
        # c→a would close the cycle a→b→c→a
        svc.add_dependency(upstream_id=c.id, downstream_id=a.id)


@pytest.mark.integration
def test_update_task_status(db_session: Session) -> None:
    svc = TaskService(db_session)
    task = svc.create_task(TaskInput(title="Pending task"))
    updated = svc.update_status(task.id, StatusUpdate(status="completed"))
    assert updated.status == "completed"
