"""In-memory sliding-window rate limiter, keyed per API key.

This works for a single process. For multiple workers or servers, swap the
storage for Redis (same interface: `hit(key) -> (allowed, remaining, retry_after)`).
"""

import asyncio
import math
import time
from collections import defaultdict, deque

from fastapi import Depends, Response

from app.core.config import Settings, get_settings
from app.core.errors import RateLimitError
from app.core.security import require_api_key


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str) -> tuple[bool, int, int]:
        now = time.monotonic()
        async with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= now - self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                retry_after = max(1, math.ceil(hits[0] + self.window - now))
                return False, 0, retry_after
            hits.append(now)
            return True, self.limit - len(hits), 0

    def reset(self) -> None:
        self._hits.clear()


_limiter: SlidingWindowLimiter | None = None


def get_limiter(settings: Settings = Depends(get_settings)) -> SlidingWindowLimiter:
    global _limiter
    if (
        _limiter is None
        or _limiter.limit != settings.rate_limit_requests
        or _limiter.window != settings.rate_limit_window_seconds
    ):
        _limiter = SlidingWindowLimiter(
            settings.rate_limit_requests, settings.rate_limit_window_seconds
        )
    return _limiter


async def enforce_rate_limit(
    response: Response,
    client_id: str = Depends(require_api_key),
    limiter: SlidingWindowLimiter = Depends(get_limiter),
) -> str:
    """Authenticates, then counts the request against the caller's quota."""
    allowed, remaining, retry_after = await limiter.hit(client_id)
    headers = {
        "X-RateLimit-Limit": str(limiter.limit),
        "X-RateLimit-Remaining": str(remaining),
    }
    if not allowed:
        headers["Retry-After"] = str(retry_after)
        raise RateLimitError(
            f"Rate limit exceeded. Try again in {retry_after} seconds.", headers=headers
        )
    response.headers.update(headers)
    return client_id
