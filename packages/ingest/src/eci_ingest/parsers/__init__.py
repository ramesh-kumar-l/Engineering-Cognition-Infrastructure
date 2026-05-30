"""Parsers — one file per source kind.

Public surface: :class:`Parser`, :func:`parse`.
"""

from eci_ingest.parsers.base import ParsedContent, Parser, parse
from eci_ingest.parsers.markdown import MarkdownParser
from eci_ingest.parsers.pdf import PdfParser
from eci_ingest.parsers.plaintext import PlaintextParser

__all__ = [
    "MarkdownParser",
    "ParsedContent",
    "Parser",
    "PdfParser",
    "PlaintextParser",
    "parse",
]
