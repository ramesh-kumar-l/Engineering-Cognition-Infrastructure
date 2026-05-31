"""Unit tests for RBAC helpers — no DB required."""

from __future__ import annotations

import uuid

import pytest

from eci_identity.dto import RequestContext
from eci_identity.errors import PermissionDeniedError
from eci_identity.rbac import can_admin, can_write, require_role, role_rank


def _ctx(role: str) -> RequestContext:
    return RequestContext(
        user_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        role=role,
        actor="test@example.com",
    )


def test_role_rank_ordering() -> None:
    assert role_rank("viewer") < role_rank("member")
    assert role_rank("member") < role_rank("admin")
    assert role_rank("unknown") == -1


def test_require_role_passes_for_equal() -> None:
    require_role(_ctx("member"), "member")  # no exception


def test_require_role_passes_for_higher() -> None:
    require_role(_ctx("admin"), "member")  # admin satisfies member requirement


def test_require_role_fails_for_lower() -> None:
    with pytest.raises(PermissionDeniedError):
        require_role(_ctx("viewer"), "member")


def test_require_admin_fails_for_member() -> None:
    with pytest.raises(PermissionDeniedError):
        require_role(_ctx("member"), "admin")


def test_can_write_member() -> None:
    assert can_write(_ctx("member")) is True


def test_can_write_viewer() -> None:
    assert can_write(_ctx("viewer")) is False


def test_can_admin_admin() -> None:
    assert can_admin(_ctx("admin")) is True


def test_can_admin_member() -> None:
    assert can_admin(_ctx("member")) is False


def test_rbac_deny_observable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify PermissionDeniedError message includes both roles."""
    with pytest.raises(PermissionDeniedError, match="viewer"):
        require_role(_ctx("viewer"), "admin")
