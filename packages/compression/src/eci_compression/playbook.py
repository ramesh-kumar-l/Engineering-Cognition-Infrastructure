"""Playbook extraction — reusable procedural recipe from document content.

If the content describes a process, procedure, or how-to, the LLM extracts it as
a structured playbook with parameters and numbered steps. Non-procedural content
returns a result with title=None and an empty steps list.
"""

from __future__ import annotations

import json
import time
from typing import Any

from eci_llm.errors import LLMParseError, LLMProviderError
from eci_llm.protocol import LLMMessage, LLMProvider, LLMRequest
from eci_observability import get_logger, get_tracer

from eci_compression.dto import PlaybookResult

_log = get_logger("eci_compression.playbook")
_tracer = get_tracer("eci_compression")

_SYSTEM = (
    "You are a knowledge-extraction assistant. "
    "Return ONLY valid JSON — no markdown fences, no extra text."
)

_PROMPT = (
    "If the following content describes a process, procedure, or how-to, extract it "
    "as a reusable playbook. Return ONLY a JSON object:\n"
    '{{"title": "playbook title or null if not a procedure", '
    '"applicable_when": "when to use this playbook", '
    '"parameters": [{{"name": "...", "description": "..."}}], '
    '"steps": [{{"step": 1, "action": "...", "notes": ""}}]}}\n'
    "If the content is NOT a procedure, return: "
    '{{"title": null, "applicable_when": "", "parameters": [], "steps": []}}\n\n'
    "Content:\n{content}"
)

_EMPTY: dict[str, Any] = {
    "title": None,
    "applicable_when": "",
    "parameters": [],
    "steps": [],
}


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[1:end])
    return text


def _parse_playbook(raw: str) -> dict[str, Any]:
    try:
        result = json.loads(_strip_fences(raw))
        if not isinstance(result, dict):
            raise LLMParseError("Expected a JSON object")
        return result  # type: ignore[return-value]
    except (json.JSONDecodeError, LLMParseError) as exc:
        raise LLMParseError(f"Playbook JSON parse failed: {exc}") from exc


class PlaybookService:
    """Extracts a reusable playbook from content when the content is procedural."""

    def __init__(self, provider: LLMProvider, max_tokens: int = 1024) -> None:
        self._provider = provider
        self._max_tokens = max_tokens

    def extract(self, content: str) -> PlaybookResult:
        with _tracer.start_as_current_span("compression.playbook") as span:
            span.set_attribute("compression.provider", self._provider.model_name)

            request = LLMRequest(
                messages=[LLMMessage(role="user", content=_PROMPT.format(content=content))],
                system=_SYSTEM,
                max_tokens=self._max_tokens,
                temperature=0.0,
            )
            t0 = time.monotonic()
            try:
                response = self._provider.complete(request)
            except LLMProviderError:
                _log.exception("compression.playbook.error")
                raise
            latency_ms = (time.monotonic() - t0) * 1000.0

            try:
                data = _parse_playbook(response.content)
            except LLMParseError:
                _log.warning("compression.playbook.parse_error", raw=response.content[:200])
                data = _EMPTY

            result = PlaybookResult(
                title=data.get("title") or None,
                applicable_when=str(data.get("applicable_when", "")),
                parameters=[p for p in data.get("parameters", []) if isinstance(p, dict)],
                steps=[s for s in data.get("steps", []) if isinstance(s, dict)],
                model_used=response.model,
                latency_ms=latency_ms,
            )
            _log.info(
                "compression.playbook.done",
                title=result.title,
                steps=len(result.steps),
                latency_ms=round(latency_ms, 1),
            )
            return result
