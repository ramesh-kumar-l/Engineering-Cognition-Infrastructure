"""Public Pydantic DTOs for ingest requests + results.

These are the contract between the API layer and the ingest services.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


DocumentKind = Literal["markdown", "text", "pdf"]


class DocumentIngestRequest(BaseModel):
    kind: DocumentKind
    source: str = Field(min_length=1, max_length=512)
    title: str | None = None
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime | None = None
    ingested_by: str = "system"


class DocumentIngestResult(BaseModel):
    id: uuid.UUID
    content_hash: str
    kind: DocumentKind
    title: str | None
    source: str
    deduplicated: bool
    ingested_at: datetime


class NoteIngestRequest(BaseModel):
    body: str = Field(min_length=1, max_length=64 * 1024)
    source: str = Field(min_length=1, max_length=512)
    author: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime | None = None
    ingested_by: str = "system"


class NoteIngestResult(BaseModel):
    id: uuid.UUID
    content_hash: str
    source: str
    deduplicated: bool
    ingested_at: datetime
