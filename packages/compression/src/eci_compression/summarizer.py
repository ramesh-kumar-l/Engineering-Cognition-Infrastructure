"""Multi-level summarization service.

Produces SHORT (1-2 sentences), MEDIUM (1 paragraph), and LONG (3-5 paragraphs)
summaries for a given piece of content using the injected LLMProvider.
"""

from __future__ import annotations

import time

from eci_llm.errors import LLMProviderError
from eci_llm.protocol import LLMMessage, LLMProvider, LLMRequest
from eci_observability import get_logger, get_tracer

from eci_compression.dto import SummaryLevel, SummaryResult

_log = get_logger("eci_compression.summarizer")
_tracer = get_tracer("eci_compression")

_PROMPTS: dict[SummaryLevel, str] = {
    SummaryLevel.SHORT: (
        "Summarize the following content in 1-2 sentences. "
        "Be concise and capture only the most important point.\n\nContent:\n{content}"
    ),
    SummaryLevel.MEDIUM: (
        "Write a concise one-paragraph summary of the following content. "
        "Cover the main purpose, key points, and conclusions.\n\nContent:\n{content}"
    ),
    SummaryLevel.LONG: (
        "Write a comprehensive summary of the following content in 3-5 paragraphs. "
        "Cover the background, main points, key details, and conclusions.\n\nContent:\n{content}"
    ),
}

_MAX_TOKENS: dict[SummaryLevel, int] = {
    SummaryLevel.SHORT: 128,
    SummaryLevel.MEDIUM: 512,
    SummaryLevel.LONG: 1024,
}


class SummarizationService:
    """Produces summaries at three granularity levels using an LLM provider."""

    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def summarize(self, content: str, level: SummaryLevel) -> SummaryResult:
        with _tracer.start_as_current_span("compression.summarize") as span:
            span.set_attribute("compression.level", level.value)
            span.set_attribute("compression.provider", self._provider.model_name)

            prompt = _PROMPTS[level].format(content=content)
            request = LLMRequest(
                messages=[LLMMessage(role="user", content=prompt)],
                max_tokens=_MAX_TOKENS[level],
                temperature=0.1,
            )
            t0 = time.monotonic()
            try:
                response = self._provider.complete(request)
            except LLMProviderError:
                _log.exception("compression.summarize.error", level=level.value)
                raise
            latency_ms = (time.monotonic() - t0) * 1000.0

            text = response.content.strip()
            _log.info(
                "compression.summarize.done",
                level=level.value,
                word_count=len(text.split()),
                latency_ms=round(latency_ms, 1),
            )
            return SummaryResult(
                level=level,
                content=text,
                word_count=len(text.split()),
                model_used=response.model,
                latency_ms=latency_ms,
            )

    def summarize_all_levels(self, content: str) -> list[SummaryResult]:
        """Run summarization for all three levels in order: short → medium → long."""
        return [self.summarize(content, level) for level in SummaryLevel]
