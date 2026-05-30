"""Ingest test fixtures. Reuses the DB session from packages/storage/tests/conftest.py.

pytest discovers that conftest automatically when both packages are workspace
members. We additionally provide a tmp blob store fixture for the
DocumentIngestService.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest

from eci_ingest.blob_store import BlobStore, LocalBlobStore


@pytest.fixture()
def blob_store(tmp_path: Path) -> Iterator[BlobStore]:
    yield LocalBlobStore(tmp_path / "blobs")
