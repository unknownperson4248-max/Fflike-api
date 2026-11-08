from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

router = APIRouter(tags=["System"])


@router.get("/health", summary="Health check")
async def health(settings: Settings = Depends(get_settings)) -> dict:
    """Public liveness check. Does not require an API key."""
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": settings.app_version,
            "mode": settings.provider_mode.value,
        },
    }
