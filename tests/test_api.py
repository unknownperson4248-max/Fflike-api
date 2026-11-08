import httpx
import pytest

from app.core.config import Settings
from app.core.errors import PlayerNotFoundError, ProviderUnavailableError, UpstreamError
from app.services.providers.official import OfficialProvider
from app.services.regions import Region
from tests.conftest import make_client

UID = "123456789"


def test_health_is_public(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["data"]["mode"] == "test"
    assert "X-Request-ID" in r.headers


def test_docs_available(client):
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json").json()
    assert "/api/v1/likes" in spec["paths"]
    assert "APIKeyHeader" in spec["components"]["securitySchemes"]


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong"}])
def test_auth_required(client, headers):
    r = client.post("/api/v1/likes", json={"uid": UID, "region": "BD"}, headers=headers)
    assert r.status_code == 401
    assert r.json()["success"] is False
    assert r.json()["error"]["code"] == "invalid_api_key"


def test_send_likes_simulated(client, auth):
    r = client.post("/api/v1/likes", json={"uid": UID, "region": "BD", "quantity": 5}, headers=auth)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    assert data["simulated"] is True and data["mode"] == "test"
    assert data["likes_added"] == 5
    assert data["likes_after"] == data["likes_before"] + 5
    assert data["daily_remaining"] == 95

    status = client.get(f"/api/v1/likes/BD/{UID}", headers=auth).json()["data"]
    assert status["likes"] == data["likes_after"]
    assert status["daily_received"] == 5


@pytest.mark.parametrize("region,expected", [("bd", "BD"), ("India", "IND"), ("id", "ID")])
def test_region_aliases(client, auth, region, expected):
    r = client.post("/api/v1/likes", json={"uid": UID, "region": region}, headers=auth)
    assert r.status_code == 200
    assert r.json()["data"]["region"] == expected


def test_regions_are_separate(client, auth):
    client.post("/api/v1/likes", json={"uid": UID, "region": "BD", "quantity": 3}, headers=auth)
    status = client.get(f"/api/v1/likes/IND/{UID}", headers=auth).json()["data"]
    assert status["daily_received"] == 0


@pytest.mark.parametrize("uid", ["123", "0123456789", "12345abc9", "1234567890123", ""])
def test_invalid_uid(client, auth, uid):
    r = client.post("/api/v1/likes", json={"uid": uid, "region": "BD"}, headers=auth)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_invalid_uid_in_path(client, auth):
    assert client.get("/api/v1/likes/BD/abc", headers=auth).status_code == 422


def test_invalid_region(client, auth):
    r = client.post("/api/v1/likes", json={"uid": UID, "region": "XX"}, headers=auth)
    assert r.status_code == 422
    assert "Unsupported region" in r.json()["error"]["details"][0]["message"]


@pytest.mark.parametrize("q", [0, 101])
def test_invalid_quantity(client, auth, q):
    r = client.post("/api/v1/likes", json={"uid": UID, "region": "BD", "quantity": q}, headers=auth)
    assert r.status_code == 422


def test_player_not_found_does_not_use_quota(client, auth):
    r = client.post("/api/v1/likes", json={"uid": "123450000", "region": "BD"}, headers=auth)
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "player_not_found"


def test_daily_limit():
    with make_client(daily_likes_per_uid=10) as c:
        h = {"X-API-Key": "test-key-123"}
        r = c.post("/api/v1/likes", json={"uid": UID, "region": "BD", "quantity": 8}, headers=h)
        assert r.json()["data"]["daily_remaining"] == 2
        # Partial grant: asked for 5, only 2 left.
        r = c.post("/api/v1/likes", json={"uid": UID, "region": "BD", "quantity": 5}, headers=h)
        assert r.json()["data"]["likes_added"] == 2
        r = c.post("/api/v1/likes", json={"uid": UID, "region": "BD"}, headers=h)
        assert r.status_code == 429
        assert r.json()["error"]["code"] == "daily_limit_reached"


def test_rate_limit():
    with make_client(rate_limit_requests=3, rate_limit_window_seconds=60) as c:
        h = {"X-API-Key": "test-key-123"}
        for i in range(3):
            r = c.get("/api/v1/regions", headers=h)
            assert r.status_code == 200
            assert r.headers["X-RateLimit-Remaining"] == str(2 - i)
        r = c.get("/api/v1/regions", headers=h)
        assert r.status_code == 429
        assert r.json()["error"]["code"] == "rate_limited"
        assert int(r.headers["Retry-After"]) >= 1


def test_regions_list(client, auth):
    data = client.get("/api/v1/regions", headers=auth).json()["data"]
    codes = {r["code"] for r in data}
    assert {"BD", "IND", "ID"} <= codes


def test_official_mode_unconfigured_returns_503():
    with make_client(provider_mode="official") as c:
        r = c.post("/api/v1/likes", json={"uid": UID, "region": "BD"}, headers={"X-API-Key": "test-key-123"})
        assert r.status_code == 503
        assert r.json()["error"]["code"] == "provider_unavailable"


# --- Official provider, against a mocked partner API ---

def _official(handler, **kw) -> OfficialProvider:
    settings = Settings(
        _env_file=None,
        official_api_base_url="https://partner.example.com/v1",
        official_api_token="secret",
        official_api_allowed_hosts="partner.example.com",
        **kw,
    )
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OfficialProvider(settings, client=client)


def test_official_rejects_unlisted_host():
    with pytest.raises(ValueError, match="not in"):
        OfficialProvider(Settings(
            _env_file=None,
            official_api_base_url="https://evil.example.com",
            official_api_token="x",
            official_api_allowed_hosts="partner.example.com",
        ))


def test_official_requires_https():
    with pytest.raises(ValueError):
        Settings(_env_file=None, official_api_base_url="http://partner.example.com")


async def test_official_send_likes():
    def handler(req: httpx.Request):
        assert req.url.path == "/v1/players/BD/123456789/likes"
        return httpx.Response(200, json={"nickname": "P", "likes_before": 10, "likes_added": 2, "likes_after": 12})

    res = await _official(handler).send_likes(UID, Region.BD, 2)
    assert res.likes_after == 12


@pytest.mark.parametrize("status,exc", [(404, PlayerNotFoundError), (403, ProviderUnavailableError), (500, UpstreamError)])
async def test_official_error_mapping(status, exc):
    provider = _official(lambda req: httpx.Response(status))
    with pytest.raises(exc):
        await provider.get_player(UID, Region.BD)
