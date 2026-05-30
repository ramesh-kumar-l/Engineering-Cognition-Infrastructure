# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

WORKDIR /app

# Copy workspace metadata first for layer caching
COPY pyproject.toml ./
COPY apps/api/pyproject.toml apps/api/
COPY packages/observability/pyproject.toml packages/observability/
COPY packages/storage/pyproject.toml packages/storage/
COPY packages/ingest/pyproject.toml packages/ingest/

# Then full source
COPY apps/api apps/api
COPY packages/observability packages/observability
COPY packages/storage packages/storage
COPY packages/ingest packages/ingest

RUN uv sync --all-packages --frozen --no-dev || uv sync --all-packages --no-dev

# Non-root runtime
RUN useradd --create-home --uid 10001 eci
USER eci

EXPOSE 8000 9464
ENV PATH="/opt/venv/bin:${PATH}"

CMD ["uvicorn", "eci_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
