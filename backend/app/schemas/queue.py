"""Task queue schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskQueueBase(BaseModel):
    """Base schema for task queue data."""

    task_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Task type (suno_upload, suno_download, youtube_upload, evaluate)",
    )
    song_id: Optional[str] = Field(None, max_length=255, description="Related song ID")
    payload: Optional[str] = Field(None, description="Task payload as JSON string")
    priority: int = Field(0, ge=0, le=100, description="Task priority (0-100, higher = more urgent)")


class TaskQueueCreate(TaskQueueBase):
    """Schema for creating a new task."""

    pass


class TaskQueueUpdate(BaseModel):
    """Schema for updating task status."""

    status: Optional[str] = Field(None, min_length=1, max_length=20)
    error_message: Optional[str] = None
    retry_count: Optional[int] = Field(None, ge=0)


class TaskQueueResponse(BaseModel):
    """Schema for task response."""

    id: int
    task_type: str
    song_id: Optional[str] = None
    payload: Optional[str] = None
    status: str
    priority: int
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class QueueStats(BaseModel):
    """Queue statistics."""

    # Status counts
    pending_count: int = 0
    running_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    total_count: int = 0

    # Task type counts
    suno_upload_count: int = 0
    suno_download_count: int = 0
    youtube_upload_count: int = 0
    evaluate_count: int = 0

    # Performance metrics
    avg_completion_time_seconds: Optional[float] = None
    oldest_pending_task_age_seconds: Optional[int] = None


class TaskQueueListMeta(BaseModel):
    """Pagination metadata for task list."""

    total: int
    skip: int
    limit: int
    has_more: bool


class TaskQueueList(BaseModel):
    """Paginated list of tasks."""

    items: list[TaskQueueResponse]
    meta: TaskQueueListMeta
