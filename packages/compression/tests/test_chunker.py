"""Unit tests for TextChunker."""

from __future__ import annotations

from eci_compression.chunker import TextChunker


def test_short_text_returns_one_chunk() -> None:
    chunker = TextChunker(chunk_size_chars=500)
    chunks = chunker.chunk("Hello world. This is a short paragraph.")
    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert "Hello" in chunks[0].content


def test_empty_text_returns_empty_list() -> None:
    chunker = TextChunker()
    assert chunker.chunk("") == []
    assert chunker.chunk("   \n\n   ") == []


def test_long_text_splits_into_multiple_chunks() -> None:
    chunker = TextChunker(chunk_size_chars=120, overlap_chars=20)
    text = "\n\n".join(f"Paragraph {i}: " + "word " * 15 for i in range(8))
    chunks = chunker.chunk(text)
    assert len(chunks) > 1
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_chunks_have_unique_hashes() -> None:
    chunker = TextChunker(chunk_size_chars=100)
    text = "\n\n".join(f"Paragraph {i} with unique content {i * 7}." for i in range(6))
    chunks = chunker.chunk(text)
    hashes = {c.content_hash for c in chunks}
    assert len(hashes) == len(chunks), "Hash collision between chunks"


def test_word_count_property() -> None:
    chunker = TextChunker()
    chunks = chunker.chunk("one two three four five")
    assert chunks[0].word_count == 5


def test_fallback_for_single_long_paragraph() -> None:
    """A single paragraph longer than chunk_size is returned as one oversized chunk."""
    chunker = TextChunker(chunk_size_chars=50)
    long_para = "word " * 100
    chunks = chunker.chunk(long_para)
    assert len(chunks) >= 1


def test_source_id_affects_hash() -> None:
    """Same content with different source_ids must produce different hashes."""
    chunker = TextChunker()
    chunks_a = chunker.chunk("Same content.", source_id="doc-a")
    chunks_b = chunker.chunk("Same content.", source_id="doc-b")
    assert chunks_a[0].content_hash != chunks_b[0].content_hash
