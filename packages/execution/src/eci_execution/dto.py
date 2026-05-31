"""Data-transfer objects for the execution package."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

VALID_STATUSES = frozenset(
    {"pending", "in_progress", "completed", "blocked", "cancelled"}
)


@dataclass
class CitationInput:
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None = None
    source_uri: str | None = None


@dataclass
class CitationOut:
    target_type: str
    target_id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None
    source_uri: str | None


@dataclass
class RoadmapInput:
    title: str
    description: str | None = None


@dataclass
class RoadmapOut:
    id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class GoalInput:
    title: str
    description: str | None = None
    roadmap_id: uuid.UUID | None = None
    source_memory_id: uuid.UUID | None = None
    citations: list[CitationInput] = field(default_factory=list)


@dataclass
class GoalOut:
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    roadmap_id: uuid.UUID | None
    source_memory_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass
class TaskInput:
    title: str
    goal_id: uuid.UUID | None = None
    description: str | None = None
    position: int = 0
    source_memory_id: uuid.UUID | None = None
    citations: list[CitationInput] = field(default_factory=list)


@dataclass
class TaskOut:
    id: uuid.UUID
    title: str
    description: str | None
    status: str
    goal_id: uuid.UUID | None
    position: int
    source_memory_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass
class StatusUpdate:
    status: str
    reason: str | None = None
    actor: str = "system"
