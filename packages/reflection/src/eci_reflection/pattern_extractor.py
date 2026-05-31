"""PatternExtractor — uses an LLM to derive lessons from execution history."""

from __future__ import annotations

import json

from eci_llm.protocol import LLMMessage, LLMProvider, LLMRequest
from eci_observability import get_logger

from eci_reflection.dto import EvidenceInput, LessonInput

_log = get_logger("eci_reflection.pattern_extractor")

_SYSTEM_PROMPT = (
    "You are an engineering retrospective assistant. "
    "Given a list of completed goals and tasks, extract actionable lessons learned. "
    "Return a JSON array only — no prose. Each element must have: "
    '{"claim": "<lesson string>", "scope": "<global|project|component>", '
    '"confidence": "<low|medium|high>", "evidence_indices": [<0-based indices>]}. '
    "Produce 1–5 lessons. If no patterns are apparent, return []."
)

_USER_TEMPLATE = "Execution items:\n{items}\n\nExtract lessons:"


def _format_items(items: list[dict[str, str]]) -> str:
    return "\n".join(
        f"{i}. [{item['type']}] {item['title']}: {item.get('description', '')}"
        for i, item in enumerate(items)
    )


class PatternExtractor:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    def extract(
        self,
        items: list[dict[str, str]],  # [{type, id, title, description}]
    ) -> list[LessonInput]:
        if not items:
            return []

        prompt = _USER_TEMPLATE.format(items=_format_items(items))
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=_SYSTEM_PROMPT),
                LLMMessage(role="user", content=prompt),
            ],
            max_tokens=1024,
            temperature=0.2,
        )
        try:
            response = self._provider.complete(request)
            raw = response.content.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            parsed = json.loads(raw)
        except Exception as exc:
            _log.warning("pattern_extractor.parse_failed", error=str(exc))
            return []

        lessons: list[LessonInput] = []
        for entry in parsed:
            if not isinstance(entry, dict) or "claim" not in entry:
                continue
            evidence_indices: list[int] = entry.get("evidence_indices", [])
            evidence = [
                EvidenceInput(
                    source_type=items[i]["type"],
                    source_id=items[i]["id"],  # type: ignore[arg-type]
                    summary=items[i]["title"],
                )
                for i in evidence_indices
                if 0 <= i < len(items)
            ]
            lessons.append(
                LessonInput(
                    claim=str(entry["claim"]),
                    scope=str(entry.get("scope", "global")),
                    confidence=str(entry.get("confidence", "medium")),
                    evidence=evidence,
                )
            )
        return lessons
