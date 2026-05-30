# Evaluations

This directory holds the evaluation contracts and benchmark records that gate AI behavior. A phase that ships AI behavior (P3+) ships an entry here.

## What lives here
- **Benchmark contracts** — the held-out queries / inputs, the metric definition, and the accepted threshold.
- **Benchmark runs** — dated records of evaluation runs against the contract.
- **Eval set hygiene notes** — provenance of the held-out data, leakage concerns.

## File conventions
- One file per benchmark area: `retrieval-benchmarks.md`, `rag-metrics.md`, `summarization-faithfulness.md`, `reflection-quality.md`.
- Inside each file: a `Contract` section (stable), and a `Runs` section (append-only).
- Held-out data lives in `evaluations/data/<area>/` and is committed only if it is small and non-sensitive; otherwise a download script is provided.

## Contract template
```markdown
# <area> — Evaluation Contract

## Metric
Name, formula, and what it measures. Why this metric.

## Accepted threshold
Number(s). Set during the phase that owns the metric. Changing the threshold requires an ADR.

## Held-out set
Source, size, hash. How leakage is prevented.

## Runner
How to reproduce: `make eval-<area>`.

## Runs
| Date | Commit | Score | Pass? | Notes |
|---|---|---|---|---|
```

## Current
*(empty — first contract lands in P2, real entries in P3 onward)*
