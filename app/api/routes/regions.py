from fastapi import APIRouter, Depends, Request

from app.core.rate_limit import enforce_rate_limit
from app.models import APIResponse, RegionInfo
from app.services.regions import REGION_NAMES

router = APIRouter(prefix="/regions", tags=["Regions"])


@router.get(
    "",
    response_model=APIResponse[list[RegionInfo]],
    summary="List supported regions",
)
async def list_regions(request: Request, _: str = Depends(enforce_rate_limit)):
    data = [RegionInfo(code=code, name=name) for code, name in REGION_NAMES.items()]
    return APIResponse(data=data, request_id=request.state.request_id)
