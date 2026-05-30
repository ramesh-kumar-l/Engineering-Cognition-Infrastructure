"""DTOs for compression requests and results.

These are pure data classes — no ORM, no HTTP. Shared between services and tests.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SummaryLevel(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class SourceType(str, Enum):
    DOCUMENT = "document"
    NOTE = "note"


@dataclass
class CompressionRequest:
    source_id: uuid.UUID
    source_type: SourceType


@dataclass
class SummaryResult:
    level: SummaryLevel
    content: str
    word_count: int
    model_used: str
    latency_ms: float = 0.0


@dataclass
class EntityRecord:
    name: str
    entity_type: str
    description: str


@dataclass
class RelationshipRecord:
    subject: str
    predicate: str
    object: str


@dataclass
class MentalModelResult:
    claims: list[str] = field(default_factory=list)
    entities: list[EntityRecord] = field(default_factory=list)
    relationships: list[RelationshipRecord] = field(default_factory=list)
    model_used: str = ""
    latency_ms: float = 0.0


@dataclass
class PlaybookResult:
    title: str | None
    applicable_when: str
    parameters: list[dict[str, str]]
    steps: list[dict[str, Any]]
    model_used: str = ""
    latency_ms: float = 0.0


@dataclass
class CompressionResult:
    source_id: uuid.UUID
    source_type: SourceType
    summaries: list[SummaryResult] = field(default_factory=list)
    mental_model: MentalModelResult | None = None
    playbook: PlaybookResult | None = None
    compressed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
