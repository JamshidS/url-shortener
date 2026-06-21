from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class UrlCreate(BaseModel):
    original_url: AnyHttpUrl
    expires_at: datetime | None = None


class UrlResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_url: str
    short_code: str = Field(min_length=4, max_length=10)
    created_at: datetime
    expires_at: datetime | None
    is_active: bool


class ErrorResponse(BaseModel):
    detail: str
