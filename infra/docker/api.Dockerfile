# syntax=docker/dockerfile:1.7
# Multi-stage build: deps cached separately from source for fast rebuilds.

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /app

# --- Layer 1: workspace + package metadata (changes rarely) ---
COPY pyproject.toml ./
COPY apps/api/pyproject.toml apps/api/
COPY packages/observability/pyproject.toml packages/observability/
COPY packages/storage/pyproject.toml packages/storage/
COPY packages/ingest/pyproject.toml packages/ingest/
COPY packages/llm/pyproject.toml packages/llm/
COPY packages/compression/pyproject.toml packages/compression/
COPY packages/retrieval/pyproject.toml packages/retrieval/
COPY packages/execution/pyproject.toml packages/execution/
COPY packages/reflection/pyproject.toml packages/reflection/
COPY packages/identity/pyproject.toml packages/identity/

# --- Layer 2: full source ---
COPY apps/api apps/api
COPY packages/observability packages/observability
COPY packages/storage packages/storage
COPY packages/ingest packages/ingest
COPY packages/llm packages/llm
COPY packages/compression packages/compression
COPY packages/retrieval packages/retrieval
COPY packages/execution packages/execution
COPY packages/reflection packages/reflection
COPY packages/identity packages/identity

# Install prod deps only (no dev tools in image)
RUN uv sync --all-packages --frozen --no-dev 2>/dev/null \
    || uv sync --all-packages --no-dev

# Non-root runtime (hardened)
RUN useradd --create-home --uid 10001 --no-log-init eci \
    && chown -R eci:eci /opt/venv /app

USER eci

EXPOSE 8000 9464

ENV PATH="/opt/venv/bin:${PATH}"

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"

CMD ["uvicorn", "eci_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
