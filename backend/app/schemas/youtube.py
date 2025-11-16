"""YouTube upload schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class YouTubeUploadBase(BaseModel):
    """Base schema for YouTube upload data."""

    title: str = Field(..., min_length=1, max_length=255, description="Video title")
    description: Optional[str] = Field(None, description="Video description")
    tags: Optional[str] = Field(None, description="Comma-separated tags")
    privacy: str = Field(
        "private",
        pattern="^(private|unlisted|public)$",
        description="Video privacy setting",
    )


class YouTubeUploadCreate(YouTubeUploadBase):
    """Schema for creating a YouTube upload."""

    song_id: str = Field(..., min_length=1, max_length=255, description="Song ID to upload")


class YouTubeUploadUpdate(BaseModel):
    """Schema for updating YouTube upload."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[str] = None
    privacy: Optional[str] = Field(None, pattern="^(private|unlisted|public)$")
    upload_status: Optional[str] = Field(None, min_length=1, max_length=20)
    video_id: Optional[str] = Field(None, max_length=50)
    video_url: Optional[str] = None
    error_message: Optional[str] = None


class YouTubeUploadResponse(BaseModel):
    """Schema for YouTube upload response."""

    id: int
    song_id: str

    # Video information
    video_id: Optional[str] = None
    video_url: Optional[str] = None

    # Upload status
    upload_status: str

    # Video metadata
    title: str
    description: Optional[str] = None
    tags: Optional[str] = None
    privacy: str

    # Error tracking
    error_message: Optional[str] = None

    # Metadata
    uploaded_by: Optional[int] = None
    uploaded_at: datetime

    # Include song details
    song_title: Optional[str] = None
    song_genre: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class OAuthURL(BaseModel):
    """OAuth authorization URL response."""

    authorization_url: str = Field(..., description="YouTube OAuth authorization URL")
    state: Optional[str] = Field(None, description="State parameter for CSRF protection")


class OAuthCallback(BaseModel):
    """OAuth callback data."""

    code: str = Field(..., description="Authorization code from OAuth callback")
    state: Optional[str] = Field(None, description="State parameter for verification")


class YouTubeUploadListMeta(BaseModel):
    """Pagination metadata for upload list."""

    total: int
    skip: int
    limit: int
    has_more: bool


class YouTubeUploadList(BaseModel):
    """Paginated list of YouTube uploads."""

    items: list[YouTubeUploadResponse]
    meta: YouTubeUploadListMeta
