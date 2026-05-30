"""Unit tests for SummarizationService.

Uses the stub_provider fixture from conftest — no real LLM required.
"""

from __future__ import annotations

from eci_compression.dto import SummaryLevel
from eci_compression.summarizer import SummarizationService


def test_summarize_returns_summary_result(stub_provider) -> None:  # type: ignore[no-untyped-def]
    svc = SummarizationService(stub_provider)
    result = svc.summarize("Some document content here.", SummaryLevel.SHORT)
    assert result.level == SummaryLevel.SHORT
    assert result.content == "stub summary"
    assert result.word_count == 2
    assert result.model_used == "stub-0.1"
    assert result.latency_ms >= 0.0


def test_summarize_all_levels_returns_three(stub_provider) -> None:  # type: ignore[no-untyped-def]
    svc = SummarizationService(stub_provider)
    results = svc.summarize_all_levels("Some content.")
    assert len(results) == 3
    levels = {r.level for r in results}
    assert levels == {SummaryLevel.SHORT, SummaryLevel.MEDIUM, SummaryLevel.LONG}


def test_each_level_produces_a_result(stub_provider) -> None:  # type: ignore[no-untyped-def]
    svc = SummarizationService(stub_provider)
    for level in SummaryLevel:
        result = svc.summarize("content", level)
        assert result.level == level
        assert isinstance(result.content, str)


def test_empty_response_produces_zero_word_count(stub_provider) -> None:  # type: ignore[no-untyped-def]
    stub_provider._response = "   "
    svc = SummarizationService(stub_provider)
    result = svc.summarize("content", SummaryLevel.SHORT)
    assert result.content == ""
    assert result.word_count == 0
