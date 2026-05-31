"""OIDCService — authorization URL builder and code exchange."""

from __future__ import annotations

import uuid

import httpx
from jose import JWTError, jwt  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from eci_identity.config import IdentityConfig
from eci_identity.dto import AuthResponse, TokenClaims, UserInput
from eci_identity.errors import InvalidTokenError, OIDCError
from eci_identity.token_service import TokenService
from eci_identity.user_service import UserService

_SCOPES = "openid email profile"


class OIDCService:
    def __init__(self, config: IdentityConfig, session: Session) -> None:
        self._cfg = config
        self._tokens = TokenService(config)
        self._users = UserService(session)

    def build_auth_url(self) -> dict[str, str]:
        """Return the OIDC authorization URL and a state value for CSRF protection."""
        if not self._cfg.oidc_issuer:
            raise OIDCError("OIDC not configured (ECI_IDENTITY_OIDC_ISSUER not set)")
        import secrets

        state = secrets.token_urlsafe(32)
        params = "&".join([
            f"response_type=code",
            f"client_id={self._cfg.oidc_client_id}",
            f"redirect_uri={self._cfg.oidc_redirect_uri}",
            f"scope={_SCOPES.replace(' ', '+')}",
            f"state={state}",
        ])
        return {"auth_url": f"{self._cfg.oidc_issuer}/authorize?{params}", "state": state}

    def exchange_code(self, code: str, tenant_id: uuid.UUID) -> AuthResponse:
        """Exchange authorization code → ID token → local JWT. Create user if new."""
        try:
            oidc_cfg = self._fetch_oidc_config()
            resp = httpx.post(
                oidc_cfg["token_endpoint"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self._cfg.oidc_redirect_uri,
                    "client_id": self._cfg.oidc_client_id,
                    "client_secret": self._cfg.oidc_client_secret,
                },
                timeout=10,
            )
            resp.raise_for_status()
            id_token: str = resp.json()["id_token"]
        except (httpx.HTTPError, KeyError) as exc:
            raise OIDCError(f"Code exchange failed: {exc}") from exc

        claims = self._decode_id_token(id_token, oidc_cfg)

        user = self._users.get_by_external_id(tenant_id, claims.sub)
        if user is None:
            user = self._users.create_user(
                UserInput(
                    tenant_id=tenant_id,
                    email=claims.email,
                    role="member",
                    external_id=claims.sub,
                )
            )

        local_jwt = self._tokens.issue(user.id, tenant_id, user.email, user.role)
        return AuthResponse(access_token=local_jwt, user=user)

    def _fetch_oidc_config(self) -> dict[str, str]:
        try:
            r = httpx.get(
                f"{self._cfg.oidc_issuer}/.well-known/openid-configuration", timeout=10
            )
            r.raise_for_status()
            return r.json()  # type: ignore[no-any-return]
        except httpx.HTTPError as exc:
            raise OIDCError(f"Cannot reach OIDC discovery endpoint: {exc}") from exc

    def _decode_id_token(self, id_token: str, oidc_cfg: dict[str, str]) -> TokenClaims:
        try:
            jwks_r = httpx.get(oidc_cfg["jwks_uri"], timeout=10)
            jwks_r.raise_for_status()
            claims: dict[str, object] = jwt.decode(
                id_token,
                jwks_r.json(),
                algorithms=["RS256"],
                audience=self._cfg.oidc_client_id,
            )
        except JWTError as exc:
            raise InvalidTokenError(f"ID token invalid: {exc}") from exc
        except httpx.HTTPError as exc:
            raise OIDCError(f"JWKS fetch failed: {exc}") from exc
        return TokenClaims(
            sub=str(claims["sub"]),
            email=str(claims.get("email", "")),
            iss=str(claims.get("iss", "")),
        )
