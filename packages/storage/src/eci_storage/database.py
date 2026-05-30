"""SQLAlchemy engine + session factory.

Single ``Engine`` per process; sessions are per-request / per-unit-of-work.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from eci_storage.config import StorageConfig, load_storage_config

_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def get_engine(config: StorageConfig | None = None) -> Engine:
    """Return the process-wide Engine. Constructed on first call."""
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        return _ENGINE
    cfg = config or load_storage_config()
    _ENGINE = create_engine(
        cfg.db_url,
        pool_size=cfg.db_pool_size,
        max_overflow=cfg.db_max_overflow,
        pool_pre_ping=cfg.db_pool_pre_ping,
        echo=cfg.db_echo,
        future=True,
    )
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, expire_on_commit=False, future=True)
    return _ENGINE


def sessionmaker_for(engine: Engine | None = None) -> sessionmaker[Session]:
    """Return the process-wide sessionmaker."""
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        get_engine() if engine is None else _bind(engine)
    assert _SESSION_FACTORY is not None
    return _SESSION_FACTORY


def _bind(engine: Engine) -> None:
    global _ENGINE, _SESSION_FACTORY
    _ENGINE = engine
    _SESSION_FACTORY = sessionmaker(bind=engine, expire_on_commit=False, future=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a Session, commit on success, rollback on error, always close."""
    factory = sessionmaker_for()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
