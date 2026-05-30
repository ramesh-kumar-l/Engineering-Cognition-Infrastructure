"""Hashing unit tests — no DB."""

from __future__ import annotations

from eci_ingest.hashing import content_hash_bytes, content_hash_text


def test_bytes_hash_is_stable() -> None:
    h1 = content_hash_bytes(b"hello")
    h2 = content_hash_bytes(b"hello")
    assert h1 == h2
    assert len(h1) == 64


def test_bytes_hash_changes_with_input() -> None:
    assert content_hash_bytes(b"hello") != content_hash_bytes(b"hellp")


def test_text_hash_includes_parts() -> None:
    base = content_hash_text("body")
    with_source = content_hash_text("body", "source-a")
    with_source_b = content_hash_text("body", "source-b")
    assert base != with_source
    assert with_source != with_source_b
