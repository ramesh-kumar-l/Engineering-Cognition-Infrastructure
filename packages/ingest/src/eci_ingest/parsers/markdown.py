"""Markdown parser — strips YAML frontmatter, extracts first heading as title."""

from __future__ import annotations

import re
from typing import Any

import frontmatter

from eci_ingest.errors import ParseError
from eci_ingest.parsers.base import ParsedContent

_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


class MarkdownParser:
    kind = "markdown"

    def parse(self, data: bytes) -> ParsedContent:
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ParseError(f"markdown not utf-8: {exc}") from exc
        try:
            post = frontmatter.loads(text)
        except Exception as exc:  # frontmatter raises generic errors
            raise ParseError(f"frontmatter parse failed: {exc}") from exc

        body = post.content.strip()
        meta: dict[str, Any] = dict(post.metadata or {})
        title = meta.pop("title", None)
        if title is None:
            match = _HEADING_RE.search(body)
            title = match.group(1) if match else None
        return ParsedContent(title=title, body=body, metadata=meta)
