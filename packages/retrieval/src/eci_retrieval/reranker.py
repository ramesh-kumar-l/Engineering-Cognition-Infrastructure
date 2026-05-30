"""RRFReranker — Reciprocal Rank Fusion for combining FTS and vector hit lists."""

from __future__ import annotations

import uuid
from collections import defaultdict

from eci_retrieval.dto import ChunkHit

# Chunk identity key: (source_type, source_id, chunk_index)
_HitKey = tuple[str, uuid.UUID, int]


class RRFReranker:
    """Reciprocal Rank Fusion (Cormack et al., 2009).

    Score for each hit = Σ  1 / (k + rank_in_list)
    where k=60 is the standard default that prevents dominance by top-ranked items.
    """

    def __init__(self, k: int = 60) -> None:
        self._k = k

    def rerank(
        self,
        fts_hits: list[ChunkHit],
        vector_hits: list[ChunkHit],
        top_k: int,
    ) -> list[ChunkHit]:
        """Merge two ranked lists and return top *top_k* hits by combined RRF score."""
        scores: dict[_HitKey, float] = defaultdict(float)
        hit_by_key: dict[_HitKey, ChunkHit] = {}

        for rank, hit in enumerate(fts_hits):
            key = (hit.source_type, hit.source_id, hit.chunk_index)
            scores[key] += 1.0 / (self._k + rank + 1)
            hit_by_key[key] = hit

        for rank, hit in enumerate(vector_hits):
            key = (hit.source_type, hit.source_id, hit.chunk_index)
            scores[key] += 1.0 / (self._k + rank + 1)
            hit_by_key.setdefault(key, hit)

        ranked_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[:top_k]
        return [
            ChunkHit(
                source_type=hit_by_key[key].source_type,
                source_id=hit_by_key[key].source_id,
                chunk_index=hit_by_key[key].chunk_index,
                content=hit_by_key[key].content,
                score=scores[key],
            )
            for key in ranked_keys
        ]
