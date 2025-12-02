"""YouTube Studio API endpoints for video project management."""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.api.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.song import Song
from app.models.user import User
from app.models.video_project import VideoProject

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# Pydantic Schemas
class VideoProjectCreate(BaseModel):
    """Schema for creating a new video project."""

    song_id: str = Field(..., description="ID of the song to create video for")


class VideoProjectUpdate(BaseModel):
    """Schema for updating video project settings."""

    cover_type: Optional[str] = Field(None, description="Cover type: template, upload, generate")
    cover_path: Optional[str] = Field(None, description="Path to cover image")
    video_style: Optional[str] = Field(
        None, description="Video style: lyric_video, static_cover, animated"
    )
    lyric_style: Optional[str] = Field(
        None, description="Lyric style: fade, karaoke, scroll, word_karaoke, word_appear"
    )
    background_color: Optional[str] = Field(None, description="Background color hex code")
    text_color: Optional[str] = Field(None, description="Text color hex code")
    highlight_color: Optional[str] = Field(None, description="Highlight color hex code")
    highlight_effect: Optional[str] = Field(
        None, description="Highlight effect for word_karaoke: color, glow, bounce, underline"
    )
    background_style: Optional[str] = Field(
        None, description="Background animation: static, ken_burns, pulse, slideshow, color_shift"
    )
    slideshow_images_json: Optional[str] = Field(
        None, description="JSON list of image paths for slideshow mode"
    )
    slideshow_interval: Optional[int] = Field(
        None, description="Seconds between slideshow transitions"
    )
    custom_title: Optional[str] = Field(None, description="Custom video title")
    custom_description: Optional[str] = Field(None, description="Custom video description")
    custom_tags: Optional[str] = Field(None, description="Custom tags as JSON string")
    privacy: Optional[str] = Field(None, description="Privacy setting: private, unlisted, public")
    video_settings_json: Optional[str] = Field(None, description="UI video settings as JSON string")


class VideoProjectResponse(BaseModel):
    """Schema for video project response."""

    id: str
    song_id: str
    cover_type: Optional[str] = None
    cover_path: Optional[str] = None
    video_style: str
    lyric_style: str
    background_color: str
    text_color: str
    highlight_color: str
    highlight_effect: str = "color"
    background_style: str = "static"
    slideshow_images_json: Optional[str] = None
    slideshow_interval: int = 8
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    custom_tags: Optional[str] = None
    privacy: str
    lyric_timing_json: Optional[str] = None
    word_timing_json: Optional[str] = None
    video_settings_json: Optional[str] = None
    preview_path: Optional[str] = None
    output_path: Optional[str] = None
    status: str
    progress: int
    error_message: Optional[str] = None
    status_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
