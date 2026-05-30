"""Text chunker — splits on paragraph boundaries with configurable overlap.

Used to prepare content for embedding in Phase 4. In Phase 3, chunking is
available as a utility but embeddings are not yet stored.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_index: int
    content: str
    content_hash: str

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class TextChunker:
    """Splits text into overlapping chunks bounded by paragraph breaks."""

    def __init__(self, chunk_size_chars: int = 1_000, overlap_chars: int = 100) -> None:
        self._chunk_size = chunk_size_chars
        self._overlap = overlap_chars

    def chunk(self, text: str, source_id: str = "") -> list[TextChunk]:
        """Split *text* into chunks. Returns empty list for blank input."""
        if not text.strip():
            return []

        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
        chunks: list[TextChunk] = []
        current = ""
        idx = 0

        for para in paragraphs:
            if len(current) + len(para) + 2 > self._chunk_size and current:
                chunks.append(self._make_chunk(idx, current, source_id))
                idx += 1
                overlap_tail = current[-self._overlap :] if self._overlap else ""
                current = (overlap_tail + "\n\n" + para).strip() if overlap_tail else para
            else:
                current = (current + "\n\n" + para).strip() if current else para

        if current.strip():
            chunks.append(self._make_chunk(idx, current, source_id))

        if not chunks:
            chunks.append(self._make_chunk(0, text[: self._chunk_size], source_id))

        return chunks

    @staticmethod
    def _make_chunk(idx: int, content: str, source_id: str) -> TextChunk:
        content = content.strip()
        raw = f"{source_id}\x1f{idx}\x1f{content}".encode()
        h = hashlib.sha256(raw).hexdigest()
        return TextChunk(chunk_index=idx, content=content, content_hash=h)
