"""Identity configuration — OIDC provider settings and JWT parameters."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IdentityConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ECI_IDENTITY_",
        env_file=".env",
        extra="ignore",
    )

    oidc_issuer: str = Field(default="", description="OIDC issuer URL")
    oidc_client_id: str = Field(default="", description="OIDC client ID")
    oidc_client_secret: str = Field(default="", description="OIDC client secret")
    oidc_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback",
        description="Redirect URI registered with the OIDC provider",
    )

    local_jwt_secret: str = Field(
        default="dev-secret-change-in-production",
        description="HS256 signing secret for local JWTs",
    )
    local_jwt_algorithm: str = Field(default="HS256")
    local_jwt_expire_seconds: int = Field(default=86400, description="Token TTL in seconds")

    # When true, all requests receive a fixed dev context — no token needed.
    auth_disabled: bool = Field(default=False)
    dev_tenant_id: str = Field(default="00000000-0000-0000-0000-000000000001")
    dev_user_id: str = Field(default="00000000-0000-0000-0000-000000000002")
    dev_actor: str = Field(default="dev@localhost")


def load_identity_config() -> IdentityConfig:
    return IdentityConfig()
