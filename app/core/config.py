"""Application settings, loaded from environment variables or a .env file."""

from enum import Enum
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderMode(str, Enum):
    """Which like provider handles requests."""

    TEST = "test"  # Simulated likes. No network calls, no real accounts touched.
    OFFICIAL = "official"  # Forwards to an authorized partner API you have a contract for.


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="FFLIKE_", extra="ignore"
    )

    app_name: str = "Free Fire Like API"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Comma-separated list of accepted API keys. Use long random values in production.
    api_keys: str = Field(default="dev-test-key")

    provider_mode: ProviderMode = ProviderMode.TEST

    # Rate limiting: max requests per API key within the window.
    rate_limit_requests: int = Field(default=30, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)

    # Max likes one UID may receive per day through this API (applies to both modes).
    daily_likes_per_uid: int = Field(default=100, ge=1)

    # Official provider. Only used when provider_mode=official.
    official_api_base_url: str = ""
    official_api_token: str = ""
    official_api_timeout_seconds: float = Field(default=10.0, gt=0)
    # Hosts the official provider is allowed to call. Requests to any other host are refused.
    official_api_allowed_hosts: str = ""

    @field_validator("official_api_base_url")
    @classmethod
    def _https_only(cls, value: str) -> str:
        if value and not value.startswith("https://"):
            raise ValueError("official_api_base_url must use https://")
        return value.rstrip("/")

    @property
    def api_key_set(self) -> frozenset[str]:
        return frozenset(k.strip() for k in self.api_keys.split(",") if k.strip())

    @property
    def allowed_hosts(self) -> frozenset[str]:
        return frozenset(
            h.strip().lower() for h in self.official_api_allowed_hosts.split(",") if h.strip()
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
