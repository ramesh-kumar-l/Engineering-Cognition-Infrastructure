# ADR-010 — Production Hardening Strategy

- **Status:** Accepted
- **Date:** 2026-05-31
- **Deciders:** Project lead
- **Phase:** P8

## Context

Phase 7 delivered a multi-tenant, RBAC-guarded system. Phase 8 must make it GA-ready:
continuous security scanning, eval-gated releases, SLO measurement, disaster recovery,
and a horizontally-scalable blob store to replace the single-host `LocalBlobStore`.

## Decision

### 1. S3-compatible BlobStore adapter (ADR-004 follow-up)

Add `S3BlobStore` in `packages/ingest/src/eci_ingest/s3_blob_store.py` implementing
the existing `BlobStore` Protocol. `boto3` is an **optional** dependency, lazy-imported
at instantiation time. Selection: `ECI_BLOB_BACKEND=s3` (default: `local`).

Key layout: `<prefix><hash[:2]>/<hash[2:4]>/<hash>` — mirrors `LocalBlobStore` sharding
so migration tooling is straightforward.

**Why not MinIO client directly?** `boto3` speaks S3 API; MinIO exposes S3 API.
Same adapter works for AWS S3, MinIO, GCS (with compatibility mode), R2.

### 2. Security toolchain

Four tools wired into `.github/workflows/security.yml`:

| Tool | Category | Exit code |
|---|---|---|
| `pip-audit` | Dependency CVE scan | non-zero on HIGH/CRITICAL CVE |
| `bandit -ll` | SAST (Python AST) | non-zero on medium+ issue |
| `trufflesecurity/trufflehog@v3` | Secret scanning | non-zero on detected secret |
| `aquasecurity/trivy-action` | Container image CVEs | non-zero on CRITICAL/HIGH |

`bandit` and `pip-audit` are added to workspace dev dependencies.
Security workflow runs on every PR to `main`/`develop` and weekly (cron).

### 3. Continuous evaluation gating

`scripts/eval_gate.py` runs before every release:
- Verifies all eval contract files exist with thresholds defined.
- Runs unit-level evaluations (no Ollama required).
- When `ECI_EVAL_CORPUS_AVAILABLE=true`, runs integration-level retrieval benchmarks
  and compares against `evaluations/retrieval-benchmarks.md` thresholds.
- Exits non-zero on any threshold regression — blocks the release.

### 4. SLO definitions and measurement

Defined in `project-memory-bank/slos/slos.md`:

| SLO | Target | Alert threshold |
|---|---|---|
| Availability | 99.5% over 7d | < 99.0% for 5 min |
| p95 latency | ≤ 500ms | > 600ms for 5 min |
| p99 latency | ≤ 1500ms | > 2000ms for 5 min |
| Citation coverage | 100% | any miss |
| Retrieval Recall@5 | ≥ 0.70 | per release gate |

Grafana dashboard at `infra/grafana/dashboards/eci-slo.json` visualises all SLOs.
Alertmanager rules at `infra/prometheus/alerts/eci.yml`.

### 5. Observability stack (docker-compose.prod.yml)

`infra/docker/docker-compose.prod.yml` adds Prometheus (scraping `/metrics`),
Grafana (provisioned with datasource + SLO dashboard), and Alertmanager.
Local dev uses the existing `docker-compose.yml` (Postgres only).

### 6. Disaster recovery

`project-memory-bank/runbooks/disaster-recovery.md` documents:
- `pg_dump` backup cadence (daily, retained 30 days).
- S3 blob store backup (cross-region replication policy).
- Restore procedure with integrity check.
- DR drill protocol and log format.

## Consequences

**Positive.**
- Blob store is now horizontally-scalable (swap `ECI_BLOB_BACKEND=s3`).
- Every PR is scanned for CVEs, secrets, and SAST issues before merge.
- Releases are blocked on eval regressions — quality gates are enforced continuously.
- SLOs are measurable from day one; the dashboard is provisioned automatically.

**Negative.**
- `boto3` (~8 MB) is an optional dependency; it is never imported in the hot path.
- Trivy container scan adds ~2 min to the release workflow.
- Grafana/Prometheus add two Docker services to the prod stack.

**Neutral.**
- The DR runbook documents expected RTO/RPO but cannot be verified without an
  actual drill. The first drill is scheduled within 2 weeks of GA.

## Alternatives Considered

- **Separate S3 package** — rejected: `BlobStore` Protocol already seams it; the
  adapter is 60 lines and belongs with the ingest package.
- **GitHub Advanced Security (CodeQL)** — deferred: requires GitHub enterprise for
  private repos. Bandit covers the same OWASP top-10 surface for Python.
- **OpenSLO YAML for SLO definitions** — deferred: adds a new DSL for no immediate
  benefit; Grafana + Prometheus alerts are sufficient for P8.
