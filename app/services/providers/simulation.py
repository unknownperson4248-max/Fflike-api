"""Test-mode provider: simulates likes in memory.

Makes no network calls and never touches a real game account. Player data is
generated deterministically from the UID so results are repeatable.
"""

import asyncio
import hashlib

from app.core.errors import PlayerNotFoundError
from app.services.providers.base import LikeProvider, ProviderLikeResult, ProviderPlayer
from app.services.regions import Region

# UIDs ending in this suffix simulate a "player not found" response, useful for client testing.
NOT_FOUND_SUFFIX = "0000"


class SimulationProvider(LikeProvider):
    mode = "test"
    simulated = True

    def __init__(self) -> None:
        self._likes: dict[tuple[str, Region], int] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _seed(uid: str, region: Region) -> int:
        return int(hashlib.sha256(f"{region.value}:{uid}".encode()).hexdigest()[:8], 16)

    def _check_exists(self, uid: str) -> None:
        if uid.endswith(NOT_FOUND_SUFFIX):
            raise PlayerNotFoundError(f"Player {uid} not found (simulated).")

    def _nickname(self, uid: str, region: Region) -> str:
        return f"TestPlayer_{region.value}_{uid[-4:]}"

    def _current(self, uid: str, region: Region) -> int:
        return self._likes.setdefault((uid, region), self._seed(uid, region) % 5000)

    async def get_player(self, uid: str, region: Region) -> ProviderPlayer:
        self._check_exists(uid)
        async with self._lock:
            return ProviderPlayer(self._nickname(uid, region), self._current(uid, region))

    async def send_likes(self, uid: str, region: Region, quantity: int) -> ProviderLikeResult:
        self._check_exists(uid)
        async with self._lock:
            before = self._current(uid, region)
            after = before + quantity
            self._likes[(uid, region)] = after
        return ProviderLikeResult(self._nickname(uid, region), before, quantity, after)

    def reset(self) -> None:
        self._likes.clear()
