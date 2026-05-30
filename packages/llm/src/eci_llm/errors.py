"""LLM runtime error hierarchy."""

from __future__ import annotations


class LLMError(Exception):
    """Base for all LLM runtime errors."""


class LLMProviderError(LLMError):
    """Provider call failed (network, HTTP, or API-level error)."""


class LLMParseError(LLMError):
    """LLM output could not be parsed as expected (e.g., malformed JSON)."""


class LLMProviderNotAvailable(LLMError):
    """Selected provider package is not installed."""
