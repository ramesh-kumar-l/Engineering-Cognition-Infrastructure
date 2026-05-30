"""Unit tests for RRFReranker — no database or LLM required."""

from __future__ import annotations

import uuid

from eci_retrieval.dto import ChunkHit
from eci_retrieval.reranker import RRFReranker

_DOC_A = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
_DOC_B = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000001")
_DOC_C = uuid.UUID("cccccccc-0000-0000-0000-000000000001")


def _hit(source_id: uuid.UUID, chunk_index: int = 0, score: float = 1.0) -> ChunkHit:
    return ChunkHit(
        source_type="document",
        source_id=source_id,
        chunk_index=chunk_index,
        content="sample content",
        score=score,
    )


def test_rrf_merges_two_lists() -> None:
    fts = [_hit(_DOC_A), _hit(_DOC_B)]
    vec = [_hit(_DOC_B), _hit(_DOC_C)]
    reranker = RRFReranker(k=60)
    results = reranker.rerank(fts, vec, top_k=3)
    assert len(results) == 3
    # DOC_B appears in both lists — should be ranked first
    assert results[0].source_id == _DOC_B


def test_rrf_top_k_limits_output() -> None:
    fts = [_hit(_DOC_A), _hit(_DOC_B), _hit(_DOC_C)]
    vec = [_hit(_DOC_C), _hit(_DOC_A), _hit(_DOC_B)]
    results = RRFReranker().rerank(fts, vec, top_k=2)
    assert len(results) == 2


def test_rrf_empty_lists_return_empty() -> None:
    results = RRFReranker().rerank([], [], top_k=10)
    assert results == []


def test_rrf_single_list_preserves_rank() -> None:
    fts = [_hit(_DOC_A), _hit(_DOC_B), _hit(_DOC_C)]
    results = RRFReranker().rerank(fts, [], top_k=3)
    assert [r.source_id for r in results] == [_DOC_A, _DOC_B, _DOC_C]


def test_rrf_scores_are_positive() -> None:
    fts = [_hit(_DOC_A)]
    vec = [_hit(_DOC_A)]
    results = RRFReranker().rerank(fts, vec, top_k=1)
    assert results[0].score > 0.0


def test_rrf_deduplicates_same_chunk() -> None:
    """Same chunk appearing in both lists is returned only once."""
    fts = [_hit(_DOC_A, chunk_index=0), _hit(_DOC_B, chunk_index=0)]
    vec = [_hit(_DOC_A, chunk_index=0), _hit(_DOC_C, chunk_index=0)]
    results = RRFReranker().rerank(fts, vec, top_k=10)
    ids = [r.source_id for r in results]
    assert ids.count(_DOC_A) == 1
