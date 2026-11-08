"""Request and response schemas."""

import re
from datetime import datetime
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, Field, field_validator

from app.services.regions import Region, parse_region

# Free Fire UIDs are numeric, 8 to 12 digits, no leading zero.
UID_PATTERN = re.compile(r"^[1-9][0-9]{7,11}$")


def validate_uid(value: str | int) -> str:
    uid = str(value).strip()
    if not UID_PATTERN.fullmatch(uid):
        raise ValueError("UID must be 8-12 digits and must not start with 0.")
    return uid


class LikeRequest(BaseModel):
    uid: str = Field(..., description="Player UID (8-12 digits).", examples=["123456789"])
    region: Region = Field(..., description="Player's server region.", examples=["BD"])
    quantity: int = Field(
        default=1, ge=1, le=100, description="Number of likes to request (1-100)."
    )

    @field_validator("uid", mode="before")
    @classmethod
    def _uid(cls, v):
        return validate_uid(v)

    @field_validator("region", mode="before")
    @classmethod
    def _region(cls, v):
        if isinstance(v, str):
            try:
                return parse_region(v)
            except ValueError:
                raise ValueError(
                    f"Unsupported region '{v}'. See GET /api/v1/regions."
                ) from None
        return v


class LikeResult(BaseModel):
    uid: str
    region: Region
    nickname: str | None = None
    likes_before: int
    likes_added: int
    likes_after: int
    daily_remaining: int = Field(description="Likes this UID can still receive today.")
    mode: Literal["test", "official"]
    simulated: bool = Field(description="True when no real game account was modified.")
    timestamp: datetime


class PlayerStatus(BaseModel):
    uid: str
    region: Region
    nickname: str | None = None
    likes: int
    daily_received: int
    daily_remaining: int
    mode: Literal["test", "official"]
    simulated: bool


class RegionInfo(BaseModel):
    code: Region
    name: str


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: Literal[True] = True
    data: T
    request_id: str | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class ErrorResponse(BaseModel):
    success: Literal[False] = False
    error: ErrorDetail
    request_id: str | None = None
