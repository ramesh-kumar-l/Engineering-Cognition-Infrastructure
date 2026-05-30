# Retrieval Benchmarks — Phase 4

> This file is the source of truth for Phase 4 retrieval acceptance.
> A phase cannot exit until the thresholds below are met on the held-out evaluation set.

## Metrics and Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Recall@5 | ≥ 0.70 | At least 70% of relevant documents appear in top-5 results |
| MRR (Mean Reciprocal Rank) | ≥ 0.60 | First relevant result within top 2 on average |
| Citation coverage | 100% | Every returned result must carry a resolvable source citation |
| Empty-result rate | ≤ 10% | For queries with known-present answers in corpus |
| Embedding throughput | ≥ 10 chunks/sec | On Ollama/nomic-embed-text local; p95 latency |
| Search p95 latency | ≤ 500ms | End-to-end from query receipt to ranked citations returned |

## Evaluation Protocol

**Corpus:** Minimum 20 documents / notes ingested and embedded before benchmark run.

**Query set:** Minimum 30 held-out queries with known relevant document IDs (manually labelled).
- 10 exact-term queries (FTS advantage)
- 10 semantic/paraphrase queries (vector advantage)
- 10 mixed queries

**Runner:** `evaluations/run_retrieval_benchmarks.py` (to be created before P4 exit).
Outputs `evaluations/results/retrieval-YYYYMMDD.json` with per-query metrics.

## Baseline Run

**Status:** Deferred — awaiting Ollama-enabled CI/CD environment.

When the first baseline run is completed, record here:

| Date | Recall@5 | MRR | Citation Coverage | Notes |
|------|----------|-----|-------------------|-------|
| TBD  | TBD      | TBD | TBD               | First run |

## Trustworthiness Checklist (per AP-2 / charter RULE 6)

- [x] **Verifiable** — every Citation carries `source_id` resolvable to an ingested record.
- [x] **Auditable** — retrieval calls are OTel-traced with stages logged.
- [x] **Overridable** — caller can filter `source_types`, adjust `top_k`, set `min_score`.
- [x] **Traceable** — `retrieval_stages` dict in response shows FTS/vector/reranked counts.
- [x] **Explainable** — RRF score is deterministic and documented in ADR-006.
