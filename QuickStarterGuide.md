# ECI Quick-Starter Guide

> Get from zero to a running local stack in under 15 minutes.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Python | 3.12.x | Exactly 3.12 — the pyproject constraints are strict |
| [uv](https://docs.astral.sh/uv/) | 0.5+ | Replaces pip + venv + pip-tools; install with `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker + Docker Compose | 24+ / 2.27+ | Runs Postgres (pgvector), Prometheus, Grafana |
| Git | any | — |
| Ollama *(optional)* | 0.3+ | Local LLM runtime; install from [ollama.com](https://ollama.com) |

---

## Step 1 — Clone and install

```bash
git clone https://github.com/<your-org>/engineering-cognition-infrastructure.git
cd engineering-cognition-infrastructure

# Install all workspace packages + dev tooling in one shot
uv sync --all-packages
```

> **No uv?** Fall back to:
> ```bash
> python -m venv .venv && source .venv/bin/activate
> pip install -r requirements.txt -r requirements-dev.txt
> ```

---

## Step 2 — Start the local database

```bash
docker compose -f infra/docker/docker-compose.yml up -d postgres
```

This starts `pgvector/pgvector:pg16` on port `5432`.  
Wait ~5 seconds then verify: `docker compose -f infra/docker/docker-compose.yml ps`

---

## Step 3 — Configure environment variables

Copy the example env file and fill in the blanks:

```bash
cp .env.example .env
```

Minimum required values for local dev:

```dotenv
# Database
ECI_DB_URL=postgresql+psycopg://eci:eci@localhost:5432/eci

# Disable auth (dev only — never in production)
ECI_IDENTITY_AUTH_DISABLED=true

# Blob storage (local filesystem by default)
ECI_BLOB_BACKEND=local
ECI_BLOB_ROOT=./data/blobs

# LLM provider (Ollama offline default)
ECI_LLM_PROVIDER=ollama
ECI_LLM_OLLAMA_HOST=http://localhost:11434
```

---

## Step 4 — Run database migrations

```bash
uv run alembic -c packages/storage/alembic.ini upgrade head
```

This applies all 7 migrations (0001_initial → 0006_enterprise) creating ~20 tables.

---

## Step 5 — Start the API server

```bash
uv run uvicorn eci_api.main:app --reload --port 8000
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

Health check:

```bash
curl http://localhost:8000/healthz
# {"status":"ok"}
```

---

## Step 6 — (Optional) Start Ollama for local LLM

```bash
# Pull the models ECI uses
ollama pull llama3.2          # summarization + mental-model extraction (~2 GB)
ollama pull nomic-embed-text  # 768-dim embeddings (~270 MB)
```

Ollama runs on `http://localhost:11434` by default — matches the `ECI_LLM_OLLAMA_HOST` value above.

---

## Step 7 — Ingest your first document

```bash
# Ingest a markdown file
curl -X POST http://localhost:8000/documents \
  -F "file=@README.md" \
  -F "source=local" \
  -F "author=you@example.com"
```

You get back a `document_id` — use it to trigger compression:

```bash
curl -X POST http://localhost:8000/compress/documents/<document_id>
```

Then search:

```bash
curl -X POST http://localhost:8000/retrieval/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is ECI", "top_k": 5}'
```

---

## Step 8 — Run the test suite

```bash
# Unit tests only (no Postgres required)
uv run pytest -m "not integration"

# Full integration tests (Postgres must be running)
ECI_TEST_DB_URL=postgresql+psycopg://eci:eci@localhost:5432/eci_test \
  uv run pytest -m integration
```

---

## Step 9 — (Optional) Full observability stack

```bash
# Start Prometheus + Grafana + Alertmanager alongside the API
docker compose -f infra/docker/docker-compose.prod.yml up
```
Before starting the production compose stack, set `POSTGRES_PASSWORD`, `ECI_JWT_SECRET`, and `GRAFANA_ADMIN_PASSWORD` in `.env` or your shell. The compose file now fails fast if the required secrets are missing. The API image is canonically `eci-api`; local compatibility builds also tag `docker-ingestion-api` for older automation. If the default host ports are already taken, override `ECI_API_PORT`, `ECI_PROMETHEUS_HOST_PORT`, `ECI_ALERTMANAGER_PORT`, or `ECI_GRAFANA_PORT`.

| Service | URL | Default credentials |
|---------|-----|---------------------|
| API | http://localhost:8000 | n/a (auth disabled in dev) |
| Swagger UI | http://localhost:8000/docs | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |
| Alertmanager | http://localhost:9093 | — |

The Grafana SLO dashboard (`eci-slo-001`) is auto-provisioned on first start.

---

## Common environment variables reference

| Variable | Default | Description |
|----------|---------|-------------|
| `ECI_DB_URL` | *(required)* | SQLAlchemy PostgreSQL connection string |
| `ECI_IDENTITY_AUTH_DISABLED` | `false` | Set `true` to bypass JWT auth in dev |
| `ECI_BLOB_BACKEND` | `local` | `local` or `s3` |
| `ECI_BLOB_ROOT` | `./data/blobs` | Root path for local blob storage |
| `ECI_BLOB_S3_BUCKET` | — | S3 bucket name (when `blob_backend=s3`) |
| `ECI_BLOB_S3_REGION` | `us-east-1` | AWS region |
| `ECI_BLOB_S3_ENDPOINT_URL` | — | Custom endpoint (e.g., MinIO `http://localhost:9000`) |
| `ECI_LLM_PROVIDER` | `ollama` | `ollama`, `openai`, `anthropic`, `openrouter` |
| `ECI_LLM_OLLAMA_HOST` | `http://localhost:11434` | Ollama base URL |
| `ECI_LLM_API_KEY` | — | API key for cloud providers |
| `ECI_LLM_MODEL` | `llama3.2` | Model name (provider-specific) |
| `ECI_IDENTITY_OIDC_ISSUER` | — | OIDC provider URL (e.g., Keycloak/Auth0) |
| `ECI_IDENTITY_OIDC_CLIENT_ID` | — | OIDC client ID |
| `ECI_IDENTITY_OIDC_CLIENT_SECRET` | — | OIDC client secret |
| `ECI_IDENTITY_LOCAL_JWT_SECRET` | — | HS256 signing secret for local JWTs |
| `ECI_OTEL_ENDPOINT` | — | OTLP gRPC endpoint (e.g., `http://otel:4317`) |
| `ECI_PROMETHEUS_PORT` | `9464` | Port for Prometheus metrics scrape |

---

## Troubleshooting

**`psycopg.OperationalError: connection refused`**  
→ Postgres container is not running or not yet healthy. Run `docker compose ps` and check logs.

**`pgvector extension not found`**  
→ You must use the `pgvector/pgvector:pg16` image, not plain `postgres:16`. Check `docker-compose.yml`.

**`LLMProviderNotAvailable`**  
→ Ollama is not running. Either start it (`ollama serve`) or set `ECI_LLM_PROVIDER=openai` and provide `ECI_LLM_API_KEY`.

**`alembic.util.exc.CommandError: Can't locate revision`**  
→ Your DB was created from a different branch. Drop and recreate: `dropdb eci && createdb eci && alembic upgrade head`.

**Mypy `import-untyped` errors on optional packages (boto3, openai)**  
→ These are lazy-imported; mypy stubs are optional. Add `ignore_missing_imports = true` to the override section for those modules, or install the stubs: `pip install boto3-stubs`.

**`ModuleNotFoundError: No module named 'ingestion_api'`**  
→ The current Python package is `eci_api`, not `ingestion_api`. Rebuild from `infra/docker/api.Dockerfile` or use `infra/docker/docker-compose.prod.yml`, which now tags the image as both `eci-api` and legacy `docker-ingestion-api`.

---

## Where to go next

- Read [`README.md`](README.md) for architecture overview, API reference, and deployment guide.
- Read [`project-memory-bank/architecture-decisions/`](project-memory-bank/architecture-decisions/) for the full ADR log.
- Run `mkdocs serve` to browse the full documentation locally at http://localhost:8001.

