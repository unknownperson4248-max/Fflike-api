from fastapi import Request

from app.services.like_service import LikeService


def get_like_service(request: Request) -> LikeService:
    return request.app.state.like_service
