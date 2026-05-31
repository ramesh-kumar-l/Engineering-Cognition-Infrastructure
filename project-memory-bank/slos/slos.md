# ECI Service Level Objectives

Ratified in ADR-010. SLOs are measured continuously in Grafana (`infra/grafana/dashboards/eci-slo.json`).
Alertmanager rules fire when the burn rate exceeds the thresholds below.

## SLO Definitions

### SLO-1 — Availability
- **Target:** 99.5% success rate over a rolling 7-day window.
- **Measurement:** `sum(rate(eci_requests_total{outcome!~"error"}[7d])) / sum(rate(eci_requests_total[7d]))`
- **Alert threshold:** Success rate < 99.0% for 5 consecutive minutes.
- **Alert name:** `ECILowAvailability` (severity: critical)
- **Excludes:** Health check probes (`/healthz`, `/readyz`, `/metrics`).

### SLO-2 — Request Latency p95
- **Target:** p95 ≤ 500ms for all non-streaming API endpoints.
- **Measurement:** `histogram_quantile(0.95, rate(eci_request_latency_seconds_bucket[5m]))`
- **Alert threshold:** p95 > 600ms for 5 consecutive minutes.
- **Alert name:** `ECIHighLatencyP95` (severity: warning)

### SLO-3 — Request Latency p99
- **Target:** p99 ≤ 1500ms.
- **Measurement:** `histogram_quantile(0.99, rate(eci_request_latency_seconds_bucket[5m]))`
- **Alert threshold:** p99 > 2000ms for 5 consecutive minutes.
- **Alert name:** `ECIHighLatencyP99` (severity: critical)

### SLO-4 — Citation Coverage
- **Target:** 100% of retrieval responses carry at least one resolvable source citation.
- **Measurement:** Evaluated per-release by `scripts/eval_gate.py` against the retrieval benchmark set.
- **Alert threshold:** Any release with citation coverage < 100% is blocked by the eval gate.
- **Alert name:** `ECIEvalGateBlock` (severity: blocker — blocks release workflow)

### SLO-5 — Retrieval Recall@5
- **Target:** Recall@5 ≥ 0.70 on the held-out query set.
- **Measurement:** Evaluated per-release; see `evaluations/retrieval-benchmarks.md`.
- **Alert threshold:** Recall@5 < 0.65 blocks the release.
- **Alert name:** `ECIEvalGateBlock`

## SLO Measurement Timeline

| SLO | First baseline | Status |
|-----|----------------|--------|
| Availability | Requires ≥1 week prod traffic | Pending |
| p95 / p99 latency | Requires ≥1 week prod traffic | Pending |
| Citation coverage | Blocked on Ollama CI corpus | Pending |
| Recall@5 | Blocked on Ollama CI corpus | Pending |

## Error Budget Policy

- If availability drops below 99.0% for > 1 hour: freeze non-critical deploys.
- If p95 exceeds 600ms for > 30 min: incident declared; on-call owns the response.
- If Recall@5 drops below 0.65 on any eval run: block release; revert last embedding change.

## Review Cadence

SLOs are reviewed at every phase exit and quarterly in production. Thresholds may
be tightened as operational data accumulates — they should never be relaxed without
explicit ADR.
