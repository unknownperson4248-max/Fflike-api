from typing import Annotated

from fastapi import APIRouter, Depends, Path, Request

from app.api.deps import get_like_service
from app.core.rate_limit import enforce_rate_limit
from app.models import (
    UID_PATTERN,
    APIResponse,
    ErrorResponse,
    LikeRequest,
    LikeResult,
    PlayerStatus,
)
from app.services.like_service import LikeService
from app.services.regions import Region

router = APIRouter(prefix="/likes", tags=["Likes"])

ERRORS = {
    401: {"model": ErrorResponse, "description": "Missing or invalid API key"},
    404: {"model": ErrorResponse, "description": "Player not found"},
    422: {"model": ErrorResponse, "description": "Invalid UID, region or body"},
    429: {"model": ErrorResponse, "description": "Rate limit or daily limit reached"},
    502: {"model": ErrorResponse, "description": "Partner API error"},
    503: {"model": ErrorResponse, "description": "Provider not configured"},
}


@router.post(
    "",
    response_model=APIResponse[LikeResult],
    responses=ERRORS,
    summary="Send likes to a player",
)
async def send_likes(
    body: LikeRequest,
    request: Request,
    _: str = Depends(enforce_rate_limit),
    service: LikeService = Depends(get_like_service),
):
    """Sends likes to a player profile.

    In **test mode** (default) likes are simulated in memory and no real
    account is changed; the response has `"simulated": true`.

    Test helper: UIDs ending in `0000` return 404 player not found.
    """
    result = await service.send_likes(body.uid, body.region, body.quantity)
    return APIResponse(data=result, request_id=request.state.request_id)


@router.get(
    "/{region}/{uid}",
    response_model=APIResponse[PlayerStatus],
    responses=ERRORS,
    summary="Get a player's like count and today's quota",
)
async def get_status(
    request: Request,
    region: Region,
    uid: Annotated[str, Path(pattern=UID_PATTERN.pattern, examples=["123456789"])],
    _: str = Depends(enforce_rate_limit),
    service: LikeService = Depends(get_like_service),
):
    result = await service.get_status(uid, region)
    return APIResponse(data=result, request_id=request.state.request_id)
