"""Official provider: forwards requests to an authorized partner API.

This adapter only works with an HTTPS API that you have written permission
to use (for example, a partner or developer program from the game publisher).
It does not contain, and must never be changed to use, private game-client
endpoints, bundled encryption keys, or pools of player accounts.

Expected partner API contract (adjust `_parse_*` if yours differs):

    GET  {base}/players/{region}/{uid}          -> {"nickname": str, "likes": int}
    POST {base}/players/{region}/{uid}/likes    body {"quantity": int}
                                                -> {"nickname": str, "likes_before": int,
                                                    "likes_added": int, "likes_after": int}

Authentication: `Authorization: Bearer <FFLIKE_OFFICIAL_API_TOKEN>`.
"""

from urllib.parse import urlparse

import httpx

from app.core.config import Settings
from app.core.errors import PlayerNotFoundError, ProviderUnavailableError, UpstreamError
from app.services.providers.base import LikeProvider, ProviderLikeResult, ProviderPlayer
from app.services.regions import Region


class OfficialProvider(LikeProvider):
    mode = "official"
    simulated = False

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.base_url = settings.official_api_base_url
        self._configured = bool(self.base_url and settings.official_api_token)
        if self._configured:
            host = (urlparse(self.base_url).hostname or "").lower()
            if host not in settings.allowed_hosts:
                raise ValueError(
                    f"Host '{host}' is not in FFLIKE_OFFICIAL_API_ALLOWED_HOSTS. "
                    "Only authorized hosts may be called."
                )
        self._client = client or httpx.AsyncClient(
            timeout=settings.official_api_timeout_seconds,
            headers={
                "Authorization": f"Bearer {settings.official_api_token}",
                "User-Agent": f"fflike-api/{settings.app_version}",
            },
            follow_redirects=False,  # Never get redirected to an unapproved host.
        )

    def _ensure_configured(self) -> None:
        if not self._configured:
            raise ProviderUnavailableError(
                "Official mode is enabled but no authorized partner API is configured. "
                "Set FFLIKE_OFFICIAL_API_BASE_URL, FFLIKE_OFFICIAL_API_TOKEN and "
                "FFLIKE_OFFICIAL_API_ALLOWED_HOSTS, or use FFLIKE_PROVIDER_MODE=test."
            )

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        self._ensure_configured()
        try:
            resp = await self._client.request(method, f"{self.base_url}{path}", **kwargs)
        except httpx.TimeoutException as exc:
            raise UpstreamError("Partner API timed out.") from exc
        except httpx.HTTPError as exc:
            raise UpstreamError("Could not reach partner API.") from exc

        if resp.status_code == 404:
            raise PlayerNotFoundError("Player not found.")
        if resp.status_code in (401, 403):
            raise ProviderUnavailableError("Partner API rejected our credentials.")
        if resp.status_code == 429:
            raise UpstreamError("Partner API rate limit reached. Try again later.")
        if resp.status_code >= 400:
            raise UpstreamError(f"Partner API returned HTTP {resp.status_code}.")
        try:
            return resp.json()
        except ValueError as exc:
            raise UpstreamError("Partner API returned invalid JSON.") from exc

    async def get_player(self, uid: str, region: Region) -> ProviderPlayer:
        data = await self._request("GET", f"/players/{region.value}/{uid}")
        try:
            return ProviderPlayer(data.get("nickname"), int(data["likes"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise UpstreamError("Unexpected partner API response.") from exc

    async def send_likes(self, uid: str, region: Region, quantity: int) -> ProviderLikeResult:
        data = await self._request(
            "POST", f"/players/{region.value}/{uid}/likes", json={"quantity": quantity}
        )
        try:
            return ProviderLikeResult(
                data.get("nickname"),
                int(data["likes_before"]),
                int(data["likes_added"]),
                int(data["likes_after"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise UpstreamError("Unexpected partner API response.") from exc

    async def close(self) -> None:
        await self._client.aclose()
