.PHONY: help install lint type test smoke docs docs-build ci-local \
        db-up db-down db-migrate db-reset test-integration clean

PY := uv run
PYTHON_PKGS := apps/api packages/observability packages/storage packages/ingest packages/llm packages/compression packages/retrieval

help:
	@echo "Targets:"
	@echo "  install            sync workspace deps (uv)"
	@echo "  lint               ruff check + format"
	@echo "  type               mypy strict over packages"
	@echo "  test               pytest (unit only; integration skipped without ECI_TEST_DB_URL)"
	@echo "  smoke              run observability smoke script"
	@echo "  docs               serve MkDocs locally"
	@echo "  docs-build         strict docs build (CI gate)"
	@echo "  ci-local           lint + type + test + docs-build"
	@echo "  db-up              start local Postgres (docker compose)"
	@echo "  db-down            stop local Postgres"
	@echo "  db-migrate         run Alembic upgrade head"
	@echo "  db-reset           drop + recreate db (destructive)"
	@echo "  test-integration   pytest -m integration (requires db-up)"
	@echo "  clean              remove caches and build artifacts"

install:
	uv sync --all-packages

lint:
	$(PY) ruff check .
	$(PY) ruff format --check .

type:
	$(PY) mypy $(PYTHON_PKGS)

test:
	$(PY) pytest -m "not integration"

smoke:
	$(PY) python scripts/smoke.py

docs:
	$(PY) mkdocs serve

docs-build:
	$(PY) mkdocs build --strict

ci-local: lint type test docs-build smoke

db-up:
	docker compose -f infra/docker/docker-compose.yml up -d postgres

db-down:
	docker compose -f infra/docker/docker-compose.yml down

db-migrate:
	$(PY) alembic -c packages/storage/alembic.ini upgrade head

db-reset:
	docker compose -f infra/docker/docker-compose.yml down -v
	docker compose -f infra/docker/docker-compose.yml up -d postgres
	@sleep 3
	$(MAKE) db-migrate

test-integration:
	$(PY) pytest -m integration

test-llm:
	$(PY) pytest -m llm_integration

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache site build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name "*.egg-info" -prune -exec rm -rf {} +
