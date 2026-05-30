"""PDF parser — text-only extraction via pypdf.

PDF binary extraction is lossy by design (no formatting). For high-fidelity
extraction we will revisit in a later phase with an ADR.
"""

from __future__ import annotations

import io
from typing import Any

from pypdf import PdfReader
from pypdf.errors import PyPdfError

from eci_ingest.errors import ParseError
from eci_ingest.parsers.base import ParsedContent


class PdfParser:
    kind = "pdf"

    def parse(self, data: bytes) -> ParsedContent:
        try:
            reader = PdfReader(io.BytesIO(data))
        except PyPdfError as exc:
            raise ParseError(f"pdf open failed: {exc}") from exc
        if reader.is_encrypted:
            raise ParseError("pdf is encrypted")

        chunks: list[str] = []
        for page in reader.pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception as exc:  # pypdf can raise generic errors per page
                raise ParseError(f"pdf page extract failed: {exc}") from exc
        body = "\n\n".join(c.strip() for c in chunks if c.strip())

        info: dict[str, Any] = {}
        if reader.metadata is not None:
            info = {
                k.lstrip("/"): str(v)
                for k, v in reader.metadata.items()
                if v is not None
            }
        title = info.get("Title") or None
        return ParsedContent(title=title, body=body, metadata=info)
