"""Parser Protocol + dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from eci_ingest.errors import UnsupportedSource


@dataclass(frozen=True)
class ParsedContent:
    """Normalized parser output."""

    title: str | None
    body: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Parser(Protocol):
    kind: str

    def parse(self, data: bytes) -> ParsedContent: ...


def parse(kind: str, data: bytes) -> ParsedContent:
    """Dispatch by ``kind``. Importing late avoids parser-package cycles."""
    from eci_ingest.parsers.markdown import MarkdownParser
    from eci_ingest.parsers.pdf import PdfParser
    from eci_ingest.parsers.plaintext import PlaintextParser

    registry: dict[str, Parser] = {
        "markdown": MarkdownParser(),
        "text": PlaintextParser(),
        "pdf": PdfParser(),
    }
    parser = registry.get(kind)
    if parser is None:
        raise UnsupportedSource(f"unknown kind: {kind}")
    return parser.parse(data)
