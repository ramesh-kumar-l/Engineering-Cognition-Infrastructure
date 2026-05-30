"""Parser unit tests — no DB."""

from __future__ import annotations

import pytest

from eci_ingest.errors import ParseError, UnsupportedSource
from eci_ingest.parsers import parse


def test_markdown_with_frontmatter_extracts_title() -> None:
    src = b"---\ntitle: Hello\nauthor: A\n---\n\n# body heading\n\ntext"
    parsed = parse("markdown", src)
    assert parsed.title == "Hello"
    assert "body heading" in parsed.body
    assert parsed.metadata.get("author") == "A"


def test_markdown_without_frontmatter_uses_first_heading() -> None:
    src = b"# Title From Heading\n\nsome body"
    parsed = parse("markdown", src)
    assert parsed.title == "Title From Heading"


def test_plaintext_first_line_as_title() -> None:
    src = b"Hello world\nsecond line"
    parsed = parse("text", src)
    assert parsed.title == "Hello world"
    assert "second line" in parsed.body


def test_unsupported_kind_raises() -> None:
    with pytest.raises(UnsupportedSource):
        parse("docx", b"x")


def test_non_utf8_markdown_raises() -> None:
    with pytest.raises(ParseError):
        parse("markdown", b"\xff\xfe\x00\x00")
