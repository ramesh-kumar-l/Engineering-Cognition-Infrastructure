"""Audit helpers — record status changes to the shared AuditEvent table."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from eci_storage.models.audit import AuditEvent


def record_status_change(
    session: Session,
    *,
    actor: str,
    target_type: str,
    target_id: uuid.UUID,
    prior_status: str,
    new_status: str,
    reason: str | None,
) -> None:
    """Append an immutable AuditEvent recording a status transition.

    Reuses the shared AuditEvent table (P2) — all write-path auditing in one place.
    """
    session.add(
        AuditEvent(
            actor=actor,
            action=f"{target_type}.status_change",
            target_type=target_type,
            target_id=target_id,
            prior_state={"status": prior_status},
            new_state={"status": new_status},
            reason=reason,
        )
    )
