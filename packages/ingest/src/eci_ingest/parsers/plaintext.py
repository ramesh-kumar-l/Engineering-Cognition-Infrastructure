"""Plaintext parser — utf-8 decode, first line as title."""

from __future__ import annotations

from eci_ingest.errors import ParseError
from eci_ingest.parsers.base import ParsedContent


class PlaintextParser:
    kind = "text"

    def parse(self, data: bytes) -> ParsedContent:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ParseError(f"text not utf-8: {exc}") from exc
        stripped = text.strip()
        first_line = stripped.splitlines()[0] if stripped else ""
        title = first_line[:120] or None
        return ParsedContent(title=title, body=stripped, metadata={})
