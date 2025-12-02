"""Task queue management API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.schemas.queue import (
    QueueStats,
    TaskQueueCreate,
    TaskQueueList,
    TaskQueueListMeta,
    TaskQueueResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/queue/tasks", response_model=TaskQueueList)
async def list_tasks(
    status_filter: Optional[str] = None,
    task_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueList:
    """
    List all tasks with filtering and pagination.

    - **status_filter**: Filter by task status (pending, running, completed, failed)
    - **task_type**: Filter by task type (suno_upload, suno_download, youtube_upload, evaluate)
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 200)
    """
    # Limit max results
    limit = min(limit, 200)

    # Build query
    query = select(TaskQueue)

    # Apply filters
