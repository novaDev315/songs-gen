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
    if status_filter:
        query = query.where(TaskQueue.status == status_filter)
    if task_type:
        query = query.where(TaskQueue.task_type == task_type)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by priority (desc) then created_at (asc)
    query = query.order_by(TaskQueue.priority.desc(), TaskQueue.created_at.asc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()

    logger.info(
        f"User {current_user.username} listed {len(tasks)} tasks (total: {total}, skip: {skip}, limit: {limit})"
    )

    return TaskQueueList(
        items=[TaskQueueResponse.model_validate(task) for task in tasks],
        meta=TaskQueueListMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(tasks)) < total,
        ),
    )


@router.get("/queue/stats", response_model=QueueStats)
async def queue_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueueStats:
    """
    Get queue statistics.

    Returns:
    - Status counts (pending, running, completed, failed)
    - Task type counts
    - Performance metrics
    """
    # Count by status
    status_counts = await db.execute(
        select(TaskQueue.status, func.count(TaskQueue.id))
        .group_by(TaskQueue.status)
    )
    status_dict = {row[0]: row[1] for row in status_counts.fetchall()}

    # Count by task type
    type_counts = await db.execute(
        select(TaskQueue.task_type, func.count(TaskQueue.id))
        .group_by(TaskQueue.task_type)
    )
    type_dict = {row[0]: row[1] for row in type_counts.fetchall()}

    # Total count
    total_result = await db.execute(select(func.count(TaskQueue.id)))
    total = total_result.scalar() or 0

    # Calculate average completion time for completed tasks
    avg_time_result = await db.execute(
        select(
            func.avg(
                func.julianday(TaskQueue.completed_at) - func.julianday(TaskQueue.created_at)
            ) * 86400  # Convert days to seconds
        ).where(
            TaskQueue.status == "completed",
            TaskQueue.completed_at.isnot(None),
        )
    )
    avg_completion_time = avg_time_result.scalar()

    # Get oldest pending task age
    oldest_pending_result = await db.execute(
        select(
            func.min(
                func.julianday(func.now()) - func.julianday(TaskQueue.created_at)
            ) * 86400  # Convert to seconds
        ).where(TaskQueue.status == "pending")
    )
    oldest_pending_age = oldest_pending_result.scalar()

    logger.info(f"User {current_user.username} retrieved queue stats")

    return QueueStats(
        pending_count=status_dict.get("pending", 0),
        running_count=status_dict.get("running", 0),
        completed_count=status_dict.get("completed", 0),
        failed_count=status_dict.get("failed", 0),
        total_count=total,
        suno_upload_count=type_dict.get("suno_upload", 0),
        suno_download_count=type_dict.get("suno_download", 0),
        youtube_upload_count=type_dict.get("youtube_upload", 0),
        evaluate_count=type_dict.get("evaluate", 0),
        avg_completion_time_seconds=avg_completion_time,
        oldest_pending_task_age_seconds=int(oldest_pending_age) if oldest_pending_age else None,
    )


@router.post("/queue/tasks", status_code=status.HTTP_201_CREATED, response_model=TaskQueueResponse)
async def enqueue_task(
    task_data: TaskQueueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueResponse:
    """
    Add task to queue manually.

    - **task_data**: Task details including type, song_id, payload, and priority
    """
    # Validate task type
    valid_task_types = ["suno_upload", "suno_download", "youtube_upload", "evaluate"]
    if task_data.task_type not in valid_task_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task_type. Must be one of: {', '.join(valid_task_types)}",
        )

    # Create task
    task = TaskQueue(
        task_type=task_data.task_type,
        song_id=task_data.song_id,
        payload=task_data.payload,
        priority=task_data.priority,
        status="pending",
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} created task {task.id} (type: {task_data.task_type}, song: {task_data.song_id})"
    )

    return TaskQueueResponse.model_validate(task)


@router.delete("/queue/tasks/{task_id}")
async def cancel_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Cancel pending task.

    Only tasks with status 'pending' can be cancelled.

    - **task_id**: Task ID to cancel
    """
    result = await db.execute(select(TaskQueue).where(TaskQueue.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    if task.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task with status '{task.status}'. Only 'pending' tasks can be cancelled.",
        )

    task_type = task.task_type
    song_id = task.song_id

    await db.delete(task)
    await db.commit()

    logger.info(f"User {current_user.username} cancelled task {task_id} (type: {task_type})")

    return {
        "message": f"Task {task_id} cancelled successfully",
        "task_id": task_id,
        "task_type": task_type,
        "song_id": song_id,
    }


@router.post("/queue/tasks/{task_id}/retry", response_model=TaskQueueResponse)
async def retry_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueResponse:
    """
    Retry failed task.

    Resets task status to 'pending' and clears error information.

    - **task_id**: Task ID to retry
    """
    result = await db.execute(select(TaskQueue).where(TaskQueue.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    if task.status not in ["failed", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot retry task with status '{task.status}'. Only 'failed' or 'completed' tasks can be retried.",
        )

    # Reset task to pending
    task.status = "pending"
    task.error_message = None
    task.started_at = None
    task.completed_at = None
    # Don't reset retry_count - it tracks total retry attempts

    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} retried task {task_id} (type: {task.task_type}, retry count: {task.retry_count})"
    )

    return TaskQueueResponse.model_validate(task)


@router.post("/queue/clear-completed")
async def clear_completed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Clear all completed tasks from the queue.

    Deletes all tasks with status 'completed'.
    """
    result = await db.execute(
        delete(TaskQueue).where(TaskQueue.status == "completed")
    )
    await db.commit()

    deleted_count = result.rowcount

    logger.info(f"User {current_user.username} cleared {deleted_count} completed tasks")

    return {
        "message": f"Cleared {deleted_count} completed tasks",
        "deleted_count": deleted_count,
    }


@router.post("/queue/clear-failed")
async def clear_failed(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Clear all failed tasks from the queue.

    Deletes all tasks with status 'failed'.
    """
    result = await db.execute(
        delete(TaskQueue).where(TaskQueue.status == "failed")
    )
    await db.commit()

    deleted_count = result.rowcount

    logger.info(f"User {current_user.username} cleared {deleted_count} failed tasks")

    return {
        "message": f"Cleared {deleted_count} failed tasks",
        "deleted_count": deleted_count,
    }


@router.post("/queue/tasks/{task_id}/complete", response_model=TaskQueueResponse)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueResponse:
    """
    Mark a task as completed.

    Used by external workers (e.g., local Suno worker) to report task completion.

    - **task_id**: Task ID to mark as completed
    """
    result = await db.execute(select(TaskQueue).where(TaskQueue.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    if task.status == "completed":
        # Already completed, just return it
        return TaskQueueResponse.model_validate(task)

    # Mark as completed
    task.status = "completed"
    task.completed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} marked task {task_id} as completed (type: {task.task_type})"
    )

    return TaskQueueResponse.model_validate(task)


@router.post("/queue/tasks/{task_id}/fail", response_model=TaskQueueResponse)
async def fail_task(
    task_id: int,
    error: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueResponse:
    """
    Mark a task as failed.

    Used by external workers (e.g., local Suno worker) to report task failure.

    - **task_id**: Task ID to mark as failed
    - **error**: Optional error message describing the failure
    """
    result = await db.execute(select(TaskQueue).where(TaskQueue.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    # Mark as failed
    task.status = "failed"
    task.completed_at = datetime.utcnow()
    if error:
        task.error_message = error
    task.retry_count = (task.retry_count or 0) + 1

    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} marked task {task_id} as failed (type: {task.task_type}, error: {error})"
    )

    return TaskQueueResponse.model_validate(task)


@router.post("/queue/tasks/{task_id}/start", response_model=TaskQueueResponse)
async def start_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TaskQueueResponse:
    """
    Mark a task as running/in-progress.

    Used by external workers to indicate they've started processing a task.

    - **task_id**: Task ID to mark as running
    """
    result = await db.execute(select(TaskQueue).where(TaskQueue.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    if task.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start task with status '{task.status}'. Only 'pending' tasks can be started.",
        )

    # Mark as running
    task.status = "running"
    task.started_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} started task {task_id} (type: {task.task_type})"
    )

    return TaskQueueResponse.model_validate(task)


@router.get("/suno/status")
async def get_suno_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Check Suno session status.

    Returns whether a valid session file exists.
    Session is created by running: python tools/suno_auth_setup.py
    """
    from pathlib import Path
    from app.config import get_settings
    
    settings = get_settings()
    
    try:
        session_file = Path(settings.SUNO_SESSION_FILE)
        if not session_file.is_absolute():
            session_file = Path("/app/data") / session_file.name
        
        if session_file.exists():
            # Check file size to ensure it's not empty
            if session_file.stat().st_size > 100:
                return {
                    "connected": True,
                    "message": "Session file found - Suno integration active"
                }
            else:
                return {
                    "connected": False,
                    "message": "Session file is empty or corrupted"
                }
        else:
            return {
                "connected": False,
                "message": f"No session file found. Run: python tools/suno_auth_setup.py"
            }
    except Exception as e:
        logger.error(f"Error checking Suno status: {e}")
        return {
            "connected": False,
            "message": f"Error checking status: {str(e)}"
        }


@router.post("/suno/refresh-session")
async def refresh_suno_session(
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Check and validate Suno session.
    
    Note: Actual session refresh requires running the setup script manually.
    This endpoint just checks the current session status.
    """
    from pathlib import Path
    from app.config import get_settings
    
    settings = get_settings()
    
    try:
        session_file = Path(settings.SUNO_SESSION_FILE)
        if not session_file.is_absolute():
            session_file = Path("/app/data") / session_file.name
        
        if session_file.exists() and session_file.stat().st_size > 100:
            return {
                "connected": True,
                "message": "Session is valid"
            }
        else:
            return {
                "connected": False,
                "message": "Session expired or missing. Run: python tools/suno_auth_setup.py"
            }
    except Exception as e:
        logger.error(f"Error refreshing Suno session: {e}")
        return {
            "connected": False,
            "message": f"Error: {str(e)}"
        }
