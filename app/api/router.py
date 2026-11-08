from fastapi import APIRouter

from app.api.routes import likes, regions

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(likes.router)
api_router.include_router(regions.router)
