"""Pydantic schemas for task queue operations."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class TaskQueueCreate(BaseModel):
    """Schema for creating a new task."""

    task_type: str
    song_id: Optional[str] = None
    payload: Optional[str] = None
    priority: int = 0


class TaskQueueUpdate(BaseModel):
    """Schema for updating a task."""

    status: Optional[str] = None
    error_message: Optional[str] = None


class TaskQueueResponse(BaseModel):
    """Schema for task responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    task_type: str
    song_id: Optional[str] = None
    status: str
    priority: int
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    payload_json: Optional[str] = None
    result_json: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TaskQueueListMeta(BaseModel):
    """Metadata for paginated responses."""

    total: int
    skip: int
    limit: int
    has_more: bool


class TaskQueueList(BaseModel):
    """Schema for paginated task list response."""

    items: list[TaskQueueResponse]
    meta: TaskQueueListMeta


class QueueStats(BaseModel):
    """Schema for queue statistics."""

    pending_count: int
    running_count: int
    completed_count: int
    failed_count: int
    total_count: int
    suno_upload_count: int = 0
    suno_download_count: int = 0
    youtube_upload_count: int = 0
    evaluate_count: int = 0
    avg_completion_time_seconds: Optional[float] = None
    oldest_pending_task_age_seconds: Optional[int] = None
