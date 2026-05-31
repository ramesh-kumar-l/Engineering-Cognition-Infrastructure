"""Data-transfer objects for the reflection package."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

VALID_CADENCES = frozenset({"weekly", "monthly", "milestone"})
VALID_CONFIDENCES = frozenset({"low", "medium", "high"})
VALID_SCOPES = frozenset({"global", "project", "component"})


@dataclass
class EvidenceInput:
    source_type: str  # goal|task|memory_entry
    source_id: uuid.UUID
    summary: str


@dataclass
class EvidenceOut:
    id: uuid.UUID
    lesson_id: uuid.UUID
    source_type: str
    source_id: uuid.UUID
    summary: str


@dataclass
class LessonInput:
    claim: str
    evidence: list[EvidenceInput] = field(default_factory=list)
    scope: str = "global"
    confidence: str = "medium"
    retrospective_id: uuid.UUID | None = None
    supersedes_id: uuid.UUID | None = None


@dataclass
class LessonOut:
    id: uuid.UUID
    retrospective_id: uuid.UUID | None
    claim: str
    scope: str
    confidence: str
    status: str
    supersedes_id: uuid.UUID | None
    evidence: list[EvidenceOut]
    created_at: datetime
    updated_at: datetime


@dataclass
class RetrospectiveInput:
    cadence: str
    scope_type: str | None = None  # roadmap|goal|global
    scope_id: uuid.UUID | None = None
    notes: str | None = None


@dataclass
class RetrospectiveOut:
    id: uuid.UUID
    cadence: str
    scope_type: str | None
    scope_id: uuid.UUID | None
    status: str
    started_at: datetime
    completed_at: datetime | None
    notes: str | None
    lesson_count: int
    created_at: datetime
    updated_at: datetime
