"""System status and monitoring endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.user import User

router = APIRouter()


@router.get("/system/status")
async def system_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get system status and statistics.

    Args:
        db: Database session
        current_user: Authenticated user

    Returns:
        Dictionary containing system status and statistics
    """
    # Count songs by status
    song_counts = {}
    for status in [
        "pending",
        "uploading",
        "generating",
        "downloaded",
        "evaluated",
        "uploaded",
        "failed",
    ]:
        result = await db.execute(select(func.count(Song.id)).where(Song.status == status))
        song_counts[status] = result.scalar() or 0

    # Count tasks by status
    task_counts = {}
    for status in ["pending", "running", "completed", "failed"]:
        result = await db.execute(
            select(func.count(TaskQueue.id)).where(TaskQueue.status == status)
        )
        task_counts[status] = result.scalar() or 0

    # Get total counts
    total_songs_result = await db.execute(select(func.count(Song.id)))
    total_songs = total_songs_result.scalar() or 0

    total_tasks_result = await db.execute(select(func.count(TaskQueue.id)))
    total_tasks = total_tasks_result.scalar() or 0

    return {
        "status": "operational",
        "workers": {
            "file_watcher": "running",
            "background_workers": "running",
            "backup_scheduler": "running",
        },
        "songs": {
            "total": total_songs,
            "by_status": song_counts,
        },
        "tasks": {
            "total": total_tasks,
            "by_status": task_counts,
        },
    }
