"""Unit tests for MentalModelService.

Inline stub providers avoid cross-file imports so this file is self-contained.
"""

from __future__ import annotations

from eci_compression.mental_model import MentalModelService
from eci_llm.protocol import LLMRequest, LLMResponse


def test_extract_valid_json(json_stub_provider) -> None:  # type: ignore[no-untyped-def]
    svc = MentalModelService(json_stub_provider)
    result = svc.extract("Some document content.")
    assert result.claims == ["test claim"]
    assert len(result.entities) == 1
    assert result.entities[0].name == "TestEntity"
    assert result.entities[0].entity_type == "concept"
    assert len(result.relationships) == 1
    assert result.relationships[0].subject == "TestEntity"
    assert result.model_used == "stub-0.1"


def test_malformed_json_returns_empty_result(stub_provider) -> None:  # type: ignore[no-untyped-def]
    """Non-JSON response degrades gracefully — no exception raised."""
    svc = MentalModelService(stub_provider)
    result = svc.extract("Some content.")
    assert result.claims == []
    assert result.entities == []
    assert result.relationships == []


def test_markdown_fenced_json_is_parsed() -> None:
    class _FencedProvider:
        @property
        def model_name(self) -> str:
            return "stub-0.1"

        def complete(self, request: LLMRequest) -> LLMResponse:
            payload = (
                "```json\n"
                '{"claims": ["fenced claim"], "entities": [], "relationships": []}\n'
                "```"
            )
            return LLMResponse(content=payload, model="stub-0.1")

    svc = MentalModelService(_FencedProvider())
    result = svc.extract("content")
    assert result.claims == ["fenced claim"]


def test_partial_json_fields_do_not_raise() -> None:
    """JSON with only some expected keys — missing fields default to []."""

    class _PartialProvider:
        @property
        def model_name(self) -> str:
            return "stub-0.1"

        def complete(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(content='{"claims": ["only claims"]}', model="stub-0.1")

    svc = MentalModelService(_PartialProvider())
    result = svc.extract("content")
    assert result.claims == ["only claims"]
    assert result.entities == []
    assert result.relationships == []
