"""Domain errors for the execution package."""

from __future__ import annotations


class ExecutionError(Exception):
    """Base class for all execution-domain errors."""


class GoalNotFoundError(ExecutionError):
    """Raised when a goal ID resolves to no row."""


class TaskNotFoundError(ExecutionError):
    """Raised when a task ID resolves to no row."""


class RoadmapNotFoundError(ExecutionError):
    """Raised when a roadmap ID resolves to no row."""


class InvalidStatusError(ExecutionError):
    """Raised when a status transition uses an unknown status value."""


class DependencyCycleError(ExecutionError):
    """Raised when adding a task dependency would create a cycle."""
