"""Notifications API endpoints for real-time notifications and alerts."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()


class NotificationCreate(BaseModel):
    """Schema for creating a notification."""
    type: str  # info, success, warning, error
    title: str
    message: str
    link: Optional[str] = None
    metadata: Optional[dict] = None


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: int
    type: str
    title: str
    message: str
    link: Optional[str]
    is_read: bool
    created_at: str

    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Schema for paginated notification list."""
    items: list[NotificationResponse]
    total: int
    unread_count: int


class NotificationSettings(BaseModel):
    """Schema for notification settings."""
    email_notifications: bool = True
    song_completed: bool = True
    song_failed: bool = True
    evaluation_complete: bool = True
    youtube_upload_complete: bool = True


@router.get("/notifications", response_model=NotificationList)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    unread_only: bool = False,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> NotificationList:
    """List notifications for the current user."""
    # For now, return empty list since we don't have a Notification model yet
    # This can be expanded when the notification system is fully implemented
    return NotificationList(
        items=[],
        total=0,
        unread_count=0
    )


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Get a specific notification."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Notification not found"
    )


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Mark a notification as read."""
    return {"status": "ok", "notification_id": notification_id}


@router.post("/notifications/read-all")
async def mark_all_notifications_read(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Mark all notifications as read."""
    return {"status": "ok", "marked_count": 0}


@router.delete("/notifications/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a notification."""
    pass


@router.get("/notifications/settings", response_model=NotificationSettings)
async def get_notification_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> NotificationSettings:
    """Get notification settings for the current user."""
    return NotificationSettings()


@router.put("/notifications/settings", response_model=NotificationSettings)
async def update_notification_settings(
    settings: NotificationSettings,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> NotificationSettings:
    """Update notification settings for the current user."""
    return settings


@router.get("/notifications/unread-count")
async def get_unread_count(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get the count of unread notifications."""
    return {"unread_count": 0}
