"""Compression error hierarchy."""

from __future__ import annotations


class CompressionError(Exception):
    """Base for all compression errors."""


class SourceNotFound(CompressionError):
    """Document or Note with the given ID does not exist."""


class ContentTooLarge(CompressionError):
    """Content exceeds the maximum allowed size for LLM processing."""


class ParseOutputError(CompressionError):
    """LLM returned output that could not be parsed as structured data."""
