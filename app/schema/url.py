
from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, Field
from pydantic import BaseModel


class UrlBase(BaseModel):
    """Base model for URL data."""
    original_url: str = Field(..., example="https://www.example.com")
    short_code: Optional[str] = Field(None, example="abc123")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)


class UrlCreate(UrlBase):
    """Model for creating a new URL entry."""
    pass

class UrlUpdate(BaseModel):
    """Model for updating an existing URL entry."""
    original_url: Optional[str] = Field(None, example="https://www.example.com")
    short_code: Optional[str] = Field(None, example="abc123")


class UrlResponse(UrlBase):
    """Model for URL response data."""
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., example=1)

    