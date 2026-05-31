"""Integration tests for RoadmapService."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy.orm import Session

from eci_execution.dto import GoalInput, RoadmapInput
from eci_execution.errors import RoadmapNotFoundError
from eci_execution.goal_service import GoalService
from eci_execution.roadmap_service import RoadmapService


@pytest.mark.integration
def test_create_and_get_roadmap(db_session: Session) -> None:
    svc = RoadmapService(db_session)
    out = svc.create_roadmap(RoadmapInput(title="Q3 Roadmap", description="Q3 engineering goals"))
    assert out.id is not None
    fetched = svc.get_roadmap(out.id)
    assert fetched.title == "Q3 Roadmap"
    assert fetched.description == "Q3 engineering goals"


@pytest.mark.integration
def test_get_roadmap_not_found(db_session: Session) -> None:
    svc = RoadmapService(db_session)
    with pytest.raises(RoadmapNotFoundError):
        svc.get_roadmap(uuid.uuid4())


@pytest.mark.integration
def test_list_roadmaps(db_session: Session) -> None:
    svc = RoadmapService(db_session)
    svc.create_roadmap(RoadmapInput(title="Roadmap Alpha"))
    svc.create_roadmap(RoadmapInput(title="Roadmap Beta"))
    results = svc.list_roadmaps()
    titles = {r.title for r in results}
    assert {"Roadmap Alpha", "Roadmap Beta"}.issubset(titles)


@pytest.mark.integration
def test_goals_linked_to_roadmap(db_session: Session) -> None:
    rm_svc = RoadmapService(db_session)
    goal_svc = GoalService(db_session)
    roadmap = rm_svc.create_roadmap(RoadmapInput(title="Linked Roadmap"))
    goal_svc.create_goal(GoalInput(title="Goal 1", roadmap_id=roadmap.id))
    goals = goal_svc.list_goals(roadmap_id=roadmap.id)
    assert len(goals) == 1
    assert goals[0].roadmap_id == roadmap.id
