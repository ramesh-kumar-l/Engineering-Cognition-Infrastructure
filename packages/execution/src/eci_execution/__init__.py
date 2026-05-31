"""eci_execution — Phase 5 execution intelligence.

Public surface:
- GoalService, TaskService, RoadmapService
- DTOs: GoalInput, GoalOut, TaskInput, TaskOut, RoadmapInput, RoadmapOut,
        CitationInput, CitationOut, StatusUpdate
- Errors: GoalNotFoundError, TaskNotFoundError, RoadmapNotFoundError,
          InvalidStatusError, DependencyCycleError
"""

from eci_execution.dto import (
    CitationInput,
    CitationOut,
    GoalInput,
    GoalOut,
    RoadmapInput,
    RoadmapOut,
    StatusUpdate,
    TaskInput,
    TaskOut,
)
from eci_execution.errors import (
    DependencyCycleError,
    ExecutionError,
    GoalNotFoundError,
    InvalidStatusError,
    RoadmapNotFoundError,
    TaskNotFoundError,
)
from eci_execution.goal_service import GoalService
from eci_execution.roadmap_service import RoadmapService
from eci_execution.task_service import TaskService

__all__ = [
    "CitationInput",
    "CitationOut",
    "DependencyCycleError",
    "ExecutionError",
    "GoalInput",
    "GoalNotFoundError",
    "GoalOut",
    "GoalService",
    "InvalidStatusError",
    "RoadmapInput",
    "RoadmapNotFoundError",
    "RoadmapOut",
    "RoadmapService",
    "StatusUpdate",
    "TaskInput",
    "TaskNotFoundError",
    "TaskOut",
    "TaskService",
]
