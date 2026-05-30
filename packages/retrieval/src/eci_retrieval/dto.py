"""Pure data transfer objects for retrieval — no ORM, no I/O."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RetrievalRequest:
    query: str
    top_k: int = 10
    source_types: list[str] = field(default_factory=lambda: ["document", "note"])


@dataclass
class ChunkHit:
    """Raw result from one retrieval stage before citation enrichment."""

    source_type: str  # "document" | "note"
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float


@dataclass
class Citation:
    """Enriched retrieval result — a chunk hit with source metadata attached."""

    source_type: str
    source_id: uuid.UUID
    chunk_index: int
    content: str
    score: float
    title: str | None
    source_uri: str | None


@dataclass
class RetrievalResult:
    query: str
    citations: list[Citation]
    retrieval_stages: dict[str, int]

    @property
    def has_citations(self) -> bool:
        return len(self.citations) > 0


@dataclass
class MemoryEntryInput:
    title: str
    body: str
    tags: list[str] = field(default_factory=list)
    source_type: str | None = None
    source_id: uuid.UUID | None = None


@dataclass
class MemoryEntryOut:
    id: uuid.UUID
    title: str
    body: str
    tags: list[str]
    source_type: str | None
    source_id: uuid.UUID | None
    version: int
    is_current: bool
    created_at: datetime
