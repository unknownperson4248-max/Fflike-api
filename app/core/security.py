"""API key authentication."""

import hashlib
import hmac

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader

from app.core.config import Settings, get_settings
from app.core.errors import AuthenticationError

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="Your API key. Configure accepted keys with FFLIKE_API_KEYS.",
)


def key_id(api_key: str) -> str:
    """Short, non-reversible identifier for a key, safe to use in logs and rate-limit buckets."""
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


def require_api_key(
    api_key: str | None = Security(api_key_header),
    settings: Settings = Depends(get_settings),
) -> str:
    """Returns the caller's key id if the key is valid, otherwise raises 401."""
    if not api_key:
        raise AuthenticationError(
            "Missing API key. Send it in the X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    # Constant-time comparison against every configured key.
    matched = False
    for valid in settings.api_key_set:
        if hmac.compare_digest(api_key.encode(), valid.encode()):
            matched = True
    if not matched:
        raise AuthenticationError("Invalid API key.", headers={"WWW-Authenticate": "ApiKey"})
    return key_id(api_key)
