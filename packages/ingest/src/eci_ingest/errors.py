"""Ingest exceptions. Map to HTTP at the router boundary, not here."""

from __future__ import annotations


class IngestError(Exception):
    """Base class for ingest-layer errors."""


class UnsupportedSource(IngestError):
    """Content-type / kind not supported."""


class ParseError(IngestError):
    """Source bytes could not be parsed."""


class SourceTooLarge(IngestError):
    """Source exceeds ECI_INGEST_MAX_BYTES."""
