# Evaluation: Summarization Faithfulness (P3)

**Phase:** 3 — Knowledge Compression
**Status:** Contract defined. Baseline to be established on first Ollama integration run.

## What is being measured

Faithfulness measures whether the generated summary contains only information
that is present in the source document. An unfaithful summary introduces facts
not in the source — this violates AP-2 (evidence before inference).

## Evaluation set

10 documents drawn from the Phase 2 integration test corpus:
- 3 markdown documents (technical how-tos)
- 3 plain-text documents (engineering notes)
- 2 PDF documents (design specs)
- 2 notes (short-form)

The set is held out; documents are not used as training data for any LLM.

## Metrics and accepted thresholds

| Metric | Threshold | How measured |
|---|---|---|
| Faithfulness (SHORT) | ≥ 0.90 | Human spot-check: fraction of sentences traceable to source |
| Faithfulness (MEDIUM) | ≥ 0.90 | Same |
| Faithfulness (LONG) | ≥ 0.85 | Same (longer output has more surface area for drift) |
| Empty-summary rate | 0% | `result.content` must be non-empty for all docs |
| JSON parse success (mental model) | ≥ 0.80 | `len(result.claims) > 0` for docs with ≥ 3 sentences |
| Latency SHORT (Ollama llama3.2, local) | p95 ≤ 15s | Wall-clock time per call |
| Latency MEDIUM | p95 ≤ 30s | Wall-clock time per call |
| Latency LONG | p95 ≤ 60s | Wall-clock time per call |

Thresholds are intentionally conservative for P3. They will be tightened in P6
(Reflection Engine) when evaluation-driven development becomes a CI gate.

## How to run

```bash
# Requires Ollama running locally with llama3.2 pulled
ECI_LLM_PROVIDER=ollama \
ECI_LLM_MODEL=llama3.2 \
ECI_TEST_DB_URL=postgresql+psycopg://eci:eci@localhost:5432/eci_test \
make test-llm
```

Results are written to stdout. Spot-check faithfulness manually on the SHORT
and MEDIUM summaries of the 10 held-out documents.

## Baseline run

*(To be filled after first Ollama integration run.)*

| Run date | Model | SHORT faithfulness | MEDIUM faithfulness | LONG faithfulness | Notes |
|---|---|---|---|---|---|
| — | — | — | — | — | Not yet run |

## What a regression looks like

A regression is:
- Faithfulness drops below threshold on any level.
- Empty-summary rate > 0% (LLM returned nothing for a doc).
- JSON parse success drops below 0.80 (mental-model extraction degraded).
- Latency p95 exceeds threshold (model or hardware regression).

If any of these occur, do not ship the release candidate (P8 policy, pre-wired here).
