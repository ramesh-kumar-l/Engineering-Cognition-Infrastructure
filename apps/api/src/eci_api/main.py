"""FastAPI app factory.

Keep this file small. Routers live in ``eci_api.routers.*``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import REGISTRY, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from starlette.responses import Response

from eci_api.config import load_api_config
from eci_api.routers import health
from eci_observability import bootstrap, get_logger, shutdown_tracing

_log = get_logger("eci_api.main")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    cfg = bootstrap()
    _log.info("api.start", env=cfg.env, service=cfg.service_name)
    try:
        yield
    finally:
        shutdown_tracing()
        _log.info("api.stop")


def create_app() -> FastAPI:
    """Construct the FastAPI app. One call per process."""
    api_cfg = load_api_config()

    app = FastAPI(
        title="ECI API",
        version="0.1.0",
        description="Engineering Cognition Infrastructure backend.",
        lifespan=_lifespan,
    )
    if api_cfg.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=api_cfg.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(health.router)

    # Phase 2 routers are wired in eci_api.routers.documents / notes
    from eci_api.routers import documents, notes

    app.include_router(documents.router)
    app.include_router(notes.router)

    from eci_api.routers import compression

    app.include_router(compression.router)

    from eci_api.routers import memory, retrieval

    app.include_router(retrieval.router)
    app.include_router(memory.router)

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)

    FastAPIInstrumentor.instrument_app(app)
    return app


app = create_app()
