"""Mental-model extraction — key claims, entities, and relationships.

The LLM is asked to return a JSON object. Malformed responses degrade gracefully
to an empty result (claims/entities/relationships all empty lists) rather than
raising an exception, matching AP-2 (evidence before inference; partial evidence
is better than none).
"""

from __future__ import annotations

import json
import time
from typing import Any

from eci_llm.errors import LLMParseError, LLMProviderError
from eci_llm.protocol import LLMMessage, LLMProvider, LLMRequest
from eci_observability import get_logger, get_tracer

from eci_compression.dto import EntityRecord, MentalModelResult, RelationshipRecord

_log = get_logger("eci_compression.mental_model")
_tracer = get_tracer("eci_compression")

_SYSTEM = (
    "You are a knowledge-extraction assistant. "
    "Return ONLY valid JSON — no markdown fences, no extra text."
)

_PROMPT = (
    "Analyze the following content and extract a structured mental model.\n"
    "Return ONLY a JSON object with this exact structure:\n"
    '{{"claims": ["key factual claim or assertion"], '
    '"entities": [{{"name": "...", "type": "person|org|concept|system|process|other", '
    '"description": "..."}}], '
    '"relationships": [{{"subject": "...", "predicate": "...", "object": "..."}}]}}\n\n'
    "Content:\n{content}"
)


def _strip_fences(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        end = len(lines) - 1 if lines[-1].strip() == "```" else len(lines)
        text = "\n".join(lines[1:end])
    return text


def _parse_mental_model(raw: str) -> dict[str, Any]:
    try:
        result = json.loads(_strip_fences(raw))
        if not isinstance(result, dict):
            raise LLMParseError("Expected a JSON object")
        return result  # type: ignore[return-value]
    except (json.JSONDecodeError, LLMParseError) as exc:
        raise LLMParseError(f"Mental-model JSON parse failed: {exc}") from exc


class MentalModelService:
    """Extracts claims, entities, and relationships from content using an LLM."""

    def __init__(self, provider: LLMProvider, max_tokens: int = 1024) -> None:
        self._provider = provider
        self._max_tokens = max_tokens

    def extract(self, content: str) -> MentalModelResult:
        with _tracer.start_as_current_span("compression.mental_model") as span:
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
                _log.exception("compression.mental_model.error")
                raise
            latency_ms = (time.monotonic() - t0) * 1000.0

            try:
                data = _parse_mental_model(response.content)
            except LLMParseError:
                _log.warning(
                    "compression.mental_model.parse_error", raw=response.content[:200]
                )
                data = {}

            claims = [str(c) for c in data.get("claims", []) if c]
            entities = [
                EntityRecord(
                    name=str(e.get("name", "")),
                    entity_type=str(e.get("type", "other")),
                    description=str(e.get("description", "")),
                )
                for e in data.get("entities", [])
                if isinstance(e, dict)
            ]
            relationships = [
                RelationshipRecord(
                    subject=str(r.get("subject", "")),
                    predicate=str(r.get("predicate", "")),
                    object=str(r.get("object", "")),
                )
                for r in data.get("relationships", [])
                if isinstance(r, dict)
            ]

            _log.info(
                "compression.mental_model.done",
                claims=len(claims),
                entities=len(entities),
                relationships=len(relationships),
                latency_ms=round(latency_ms, 1),
            )
            return MentalModelResult(
                claims=claims,
                entities=entities,
                relationships=relationships,
                model_used=response.model,
                latency_ms=latency_ms,
            )
