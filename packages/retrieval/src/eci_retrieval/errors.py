"""Retrieval error hierarchy."""

from __future__ import annotations


class RetrievalError(Exception):
    """Base error for all retrieval failures."""


class NoCitationError(RetrievalError):
    """Raised when a response is generated without any source citations.

    Enforces AP-2: "evidence before inference" — no answer without provenance.
    """


class EmbeddingError(RetrievalError):
    """Raised when an embedding operation fails."""


class SourceNotFoundError(RetrievalError):
    """Raised when the requested source (document or note) does not exist."""
