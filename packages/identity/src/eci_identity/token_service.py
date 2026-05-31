"""TokenService — issue and validate local HS256 JWTs."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from jose import JWTError, jwt  # type: ignore[import-untyped]
from jose.exceptions import ExpiredSignatureError  # type: ignore[import-untyped]

from eci_identity.config import IdentityConfig
from eci_identity.dto import RequestContext
from eci_identity.errors import ExpiredTokenError, InvalidTokenError


class TokenService:
    def __init__(self, config: IdentityConfig) -> None:
        self._cfg = config

    def issue(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        email: str,
        role: str,
    ) -> str:
        """Sign and return a short-lived HS256 JWT."""
        now = int(datetime.now(timezone.utc).timestamp())
        payload = {
            "sub": str(user_id),
            "email": email,
            "tenant_id": str(tenant_id),
            "role": role,
            "iat": now,
            "exp": now + self._cfg.local_jwt_expire_seconds,
        }
        return jwt.encode(  # type: ignore[no-any-return]
            payload,
            self._cfg.local_jwt_secret,
            algorithm=self._cfg.local_jwt_algorithm,
        )

    def decode(self, token: str) -> RequestContext:
        """Decode and validate a local JWT; raise on failure."""
        try:
            claims: dict[str, object] = jwt.decode(
                token,
                self._cfg.local_jwt_secret,
                algorithms=[self._cfg.local_jwt_algorithm],
            )
        except ExpiredSignatureError as exc:
            raise ExpiredTokenError("Token has expired") from exc
        except JWTError as exc:
            raise InvalidTokenError(f"Invalid token: {exc}") from exc

        return RequestContext(
            user_id=uuid.UUID(str(claims["sub"])),
            tenant_id=uuid.UUID(str(claims["tenant_id"])),
            role=str(claims.get("role", "viewer")),
            actor=str(claims.get("email", claims["sub"])),
        )

    def dev_context(self) -> RequestContext:
        """Fixed RequestContext for dev/test when auth is disabled."""
        return RequestContext(
            user_id=uuid.UUID(self._cfg.dev_user_id),
            tenant_id=uuid.UUID(self._cfg.dev_tenant_id),
            role="admin",
            actor=self._cfg.dev_actor,
        )
