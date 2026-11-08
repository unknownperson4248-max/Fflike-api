"""Business logic: daily caps per UID, then delegate to the active provider."""

import asyncio
from datetime import date, datetime, timezone

from app.core.errors import DailyLimitError
from app.models import LikeResult, PlayerStatus
from app.services.providers.base import LikeProvider
from app.services.regions import Region


class DailyQuota:
    """Tracks how many likes each UID received today (UTC). Resets at midnight UTC."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._day = self._today()
        self._used: dict[tuple[str, Region], int] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _today() -> date:
        return datetime.now(timezone.utc).date()

    def _roll(self) -> None:
        today = self._today()
        if today != self._day:
            self._day = today
            self._used.clear()

    def used(self, uid: str, region: Region) -> int:
        self._roll()
        return self._used.get((uid, region), 0)

    async def reserve(self, uid: str, region: Region, quantity: int) -> int:
        """Reserves up to `quantity` likes. Returns how many were granted."""
        async with self._lock:
            self._roll()
            used = self._used.get((uid, region), 0)
            granted = min(quantity, self.limit - used)
            if granted <= 0:
                raise DailyLimitError(
                    f"UID {uid} already received the daily maximum of {self.limit} likes. "
                    "Try again after 00:00 UTC."
                )
            self._used[(uid, region)] = used + granted
            return granted

    async def release(self, uid: str, region: Region, quantity: int) -> None:
        async with self._lock:
            key = (uid, region)
            self._used[key] = max(0, self._used.get(key, 0) - quantity)

    def reset(self) -> None:
        self._used.clear()


class LikeService:
    def __init__(self, provider: LikeProvider, quota: DailyQuota) -> None:
        self.provider = provider
        self.quota = quota

    async def send_likes(self, uid: str, region: Region, quantity: int) -> LikeResult:
        # Look the player up first so we don't burn quota on unknown UIDs.
        await self.provider.get_player(uid, region)
        granted = await self.quota.reserve(uid, region, quantity)
        try:
            result = await self.provider.send_likes(uid, region, granted)
        except Exception:
            await self.quota.release(uid, region, granted)
            raise
        if result.likes_added < granted:
            await self.quota.release(uid, region, granted - result.likes_added)
        return LikeResult(
            uid=uid,
            region=region,
            nickname=result.nickname,
            likes_before=result.likes_before,
            likes_added=result.likes_added,
            likes_after=result.likes_after,
            daily_remaining=self.quota.limit - self.quota.used(uid, region),
            mode=self.provider.mode,
            simulated=self.provider.simulated,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_status(self, uid: str, region: Region) -> PlayerStatus:
        player = await self.provider.get_player(uid, region)
        used = self.quota.used(uid, region)
        return PlayerStatus(
            uid=uid,
            region=region,
            nickname=player.nickname,
            likes=player.likes,
            daily_received=used,
            daily_remaining=self.quota.limit - used,
            mode=self.provider.mode,
            simulated=self.provider.simulated,
        )
