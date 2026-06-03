"""Idempotent dev-identity seeding for auth-disabled mode.

When ``ECI_IDENTITY_AUTH_DISABLED=true`` every request resolves to a fixed dev
tenant/user (see ``TokenService.dev_context``). Tenant-scoped writes — goals,
tasks, roadmaps — carry a ``tenant_id`` FK, so those rows must exist. This seeds
them once at startup.

It runs **only** in dev-bypass mode; with auth enabled (production) it is a no-op
and never touches the database.
"""

from __future__ import annotations

import uuid

from eci_identity.config import load_identity_config
from eci_observability import get_logger
from eci_storage import sessionmaker_for
from eci_storage.models.tenant import Tenant
from eci_storage.models.user import User

_log = get_logger("eci_api.dev_seed")


def seed_dev_identity() -> None:
    """Ensure the dev tenant + user exist when auth is disabled (idempotent)."""
    cfg = load_identity_config()
    if not cfg.auth_disabled:
        return

    tenant_id = uuid.UUID(cfg.dev_tenant_id)
    user_id = uuid.UUID(cfg.dev_user_id)
    session = sessionmaker_for()()
    try:
        if session.get(Tenant, tenant_id) is None:
            session.add(Tenant(id=tenant_id, name="Dev Workspace", slug="dev"))
        if session.get(User, user_id) is None:
            session.add(
                User(
                    id=user_id,
                    tenant_id=tenant_id,
                    email=cfg.dev_actor,
                    role="admin",
                    display_name="Dev User",
                )
            )
        session.commit()
        _log.info("dev_seed.ready", tenant_id=str(tenant_id))
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
