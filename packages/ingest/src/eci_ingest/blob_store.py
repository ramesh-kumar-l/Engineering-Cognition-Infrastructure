"""Blob storage — Protocol + local filesystem implementation.

Future adapters (S3/MinIO) implement :class:`BlobStore` without touching the
ingest service.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from eci_ingest.config import IngestConfig, load_ingest_config


class BlobStore(Protocol):
    """Content-addressed binary store."""

    def put(self, content_hash: str, data: bytes) -> str:
        """Write ``data`` under ``content_hash``. Return the storage URI."""

    def get(self, content_hash: str) -> bytes:
        """Read bytes by hash. Raises FileNotFoundError if absent."""

    def exists(self, content_hash: str) -> bool:  # pragma: no cover - trivial
        ...

    def uri_for(self, content_hash: str) -> str:
        ...


class LocalBlobStore:
    """Filesystem-backed BlobStore. Sharded by hash prefix."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, content_hash: str) -> Path:
        if len(content_hash) < 4:
            raise ValueError("content_hash too short")
        return self.root / content_hash[:2] / content_hash[2:4] / content_hash

    def uri_for(self, content_hash: str) -> str:
        return self._path_for(content_hash).as_uri()

    def exists(self, content_hash: str) -> bool:
        return self._path_for(content_hash).exists()

    def put(self, content_hash: str, data: bytes) -> str:
        path = self._path_for(content_hash)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            tmp = path.with_suffix(".tmp")
            tmp.write_bytes(data)
            tmp.replace(path)
        return path.as_uri()

    def get(self, content_hash: str) -> bytes:
        return self._path_for(content_hash).read_bytes()


_STORE: BlobStore | None = None


def get_blob_store(config: IngestConfig | None = None) -> BlobStore:
    """Return the process-wide BlobStore singleton."""
    global _STORE
    if _STORE is not None:
        return _STORE
    cfg = config or load_ingest_config()
    _STORE = LocalBlobStore(cfg.blob_root)
    return _STORE
