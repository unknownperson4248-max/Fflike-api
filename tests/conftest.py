import pytest
from fastapi.testclient import TestClient

from app.core import rate_limit
from app.core.config import Settings
from app.main import create_app

API_KEY = "test-key-123"


def make_client(**overrides) -> TestClient:
    rate_limit._limiter = None
    settings = Settings(_env_file=None, api_keys=API_KEY, **overrides)
    return TestClient(create_app(settings))


@pytest.fixture
def client():
    with make_client() as c:
        yield c


@pytest.fixture
def auth():
    return {"X-API-Key": API_KEY}
