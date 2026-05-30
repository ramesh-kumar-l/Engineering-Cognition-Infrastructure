"""Content hashing — sha256 hex.

Single function family so the ingest layer never reaches for a hash directly.
"""

from __future__ import annotations

import hashlib


def content_hash_bytes(data: bytes) -> str:
    """Return sha256 hex of the bytes."""
    return hashlib.sha256(data).hexdigest()


def content_hash_text(text: str, *parts: str) -> str:
    """Hash a text payload optionally joined with stable extra parts.

    Used for Notes (which have no raw blob): the hash incorporates
    ``body``, ``source``, ``author``, and ``captured_at`` so semantically
    identical content from the same origin de-duplicates.
    """
    joined = "\x1f".join((text, *parts)).encode("utf-8")
    return hashlib.sha256(joined).hexdigest()
