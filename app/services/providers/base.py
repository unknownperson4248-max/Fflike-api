"""Provider interface. A provider is the only component that talks to a game service."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.regions import Region


@dataclass
class ProviderLikeResult:
    nickname: str | None
    likes_before: int
    likes_added: int
    likes_after: int


@dataclass
class ProviderPlayer:
    nickname: str | None
    likes: int


class LikeProvider(ABC):
    mode: str
    simulated: bool

    @abstractmethod
    async def get_player(self, uid: str, region: Region) -> ProviderPlayer: ...

    @abstractmethod
    async def send_likes(self, uid: str, region: Region, quantity: int) -> ProviderLikeResult: ...

    async def close(self) -> None:  # noqa: B027 - optional hook
        pass
