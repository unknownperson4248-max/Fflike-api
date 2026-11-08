"""FastAPI application entry point.

Run locally:  uvicorn app.main:app --reload
Docs:         http://localhost:8000/docs
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.router import api_router
from app.api.routes import health
from app.core.config import ProviderMode, Settings, get_settings
from app.core.errors import register_exception_handlers
from app.services.like_service import DailyQuota, LikeService
from app.services.providers.base import LikeProvider
from app.services.providers.official import OfficialProvider
from app.services.providers.simulation import SimulationProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("fflike")


def build_provider(settings: Settings) -> LikeProvider:
    if settings.provider_mode is ProviderMode.OFFICIAL:
        return OfficialProvider(settings)
    return SimulationProvider()


DESCRIPTION = """
REST API for sending likes to Free Fire player profiles.

### Modes
* **test** (default): likes are simulated in memory. No network calls, no real accounts changed.
* **official**: forwards to an authorized partner API configured by the operator.
  Unofficial or reverse-engineered game endpoints are not supported.

### Authentication
Send your key in the `X-API-Key` header. Click **Authorize** above to try requests here.

### Limits
* Per-key rate limit (see `X-RateLimit-*` response headers).
* Daily cap on likes per UID, reset at 00:00 UTC.
"""


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        provider = build_provider(settings)
        app.state.like_service = LikeService(provider, DailyQuota(settings.daily_likes_per_uid))
        logger.info("Started in %s mode", settings.provider_mode.value)
        yield
        await provider.close()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.dependency_overrides[get_settings] = lambda: settings

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id[:64]
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    register_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(api_router)
    return app


app = create_app()
