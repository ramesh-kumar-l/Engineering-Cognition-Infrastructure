"""Append-only audit helper shared by ingest services."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from eci_storage.models import AuditEvent


def record_audit(
    session: Session,
    *,
    actor: str,
    action: str,
    target_type: str,
    target_id: uuid.UUID | None,
    new_state: dict[str, Any] | None = None,
    prior_state: dict[str, Any] | None = None,
    reason: str | None = None,
) -> AuditEvent:
    """Insert an AuditEvent. Caller owns the transaction."""
    event = AuditEvent(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        prior_state=prior_state,
        new_state=new_state,
        reason=reason,
    )
    session.add(event)
    session.flush()
    return event
