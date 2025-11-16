"""Song schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SongBase(BaseModel):
    """Base schema for song data."""

    title: str = Field(..., min_length=1, max_length=255, description="Song title")
    genre: str = Field(..., min_length=1, max_length=50, description="Music genre")
    style_prompt: str = Field(..., min_length=1, description="Suno AI style prompt")
    lyrics: str = Field(..., min_length=1, description="Song lyrics with structure tags")
    metadata_json: Optional[str] = Field(None, description="Additional metadata as JSON string")


class SongCreate(SongBase):
    """Schema for creating a new song."""

    file_path: str = Field(..., min_length=1, max_length=500, description="Path to source .md file")


class SongUpdate(BaseModel):
    """Schema for updating song metadata."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    style_prompt: Optional[str] = Field(None, min_length=1)
    lyrics: Optional[str] = Field(None, min_length=1)
    metadata_json: Optional[str] = None
    file_path: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = Field(None, min_length=1, max_length=20)


class SongResponse(BaseModel):
    """Schema for song response."""

    id: str
    title: str
    genre: str
    style_prompt: str
    lyrics: str
    file_path: str
    status: str
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SongStatus(BaseModel):
    """Detailed song status in pipeline."""

    id: str
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    # Related status information
    suno_job_count: int = 0
    latest_suno_status: Optional[str] = None

    evaluation_count: int = 0
    is_evaluated: bool = False
    is_approved: Optional[bool] = None
    manual_rating: Optional[int] = None

    youtube_upload_count: int = 0
    latest_youtube_status: Optional[str] = None
    video_url: Optional[str] = None

    pending_tasks: int = 0
    running_tasks: int = 0
    failed_tasks: int = 0


class SongListMeta(BaseModel):
    """Pagination metadata for song list."""

    total: int
    skip: int
    limit: int
    has_more: bool


class SongList(BaseModel):
    """Paginated list of songs."""

    items: list[SongResponse]
    meta: SongListMeta
