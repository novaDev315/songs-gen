"""System API endpoints for health checks, metrics, and admin operations."""

import logging
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.suno_job import SunoJob
from app.models.youtube_upload import YouTubeUpload

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()


class SystemStatus(BaseModel):
    """System status response."""
    status: str
    version: str
    environment: str
    uptime_seconds: float
    python_version: str
    platform: str


class DatabaseStatus(BaseModel):
    """Database status response."""
    connected: bool
    total_songs: int
    pending_tasks: int
    active_suno_jobs: int
    recent_uploads: int


class StorageStatus(BaseModel):
    """Storage status response."""
    download_folder_exists: bool
    download_folder_size_mb: float
    watch_folder_exists: bool
    data_folder_exists: bool
    cover_art_folder_exists: bool
    video_cache_folder_exists: bool


class SystemMetrics(BaseModel):
    """Combined system metrics."""
    system: SystemStatus
    database: DatabaseStatus
    storage: StorageStatus


# Track application start time
_start_time = datetime.now(timezone.utc)


def _get_folder_size(path: Path) -> float:
    """Get folder size in MB."""
    if not path.exists():
        return 0.0
    total = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
    return total / (1024 * 1024)


@router.get("/system/status", response_model=SystemStatus)
async def get_system_status(
    current_user: Annotated[object, Depends(get_current_user)]
) -> SystemStatus:
    """Get basic system status."""
    uptime = (datetime.now(timezone.utc) - _start_time).total_seconds()

    return SystemStatus(
        status="healthy",
        version="1.0.0",
        environment=settings.APP_ENV,
        uptime_seconds=uptime,
        python_version=platform.python_version(),
        platform=platform.system()
    )


@router.get("/system/database", response_model=DatabaseStatus)
async def get_database_status(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> DatabaseStatus:
    """Get database status and counts."""
    try:
        # Test connection
        await db.execute(text("SELECT 1"))

        # Get counts
        songs_result = await db.execute(select(func.count()).select_from(Song))
        total_songs = songs_result.scalar() or 0

        tasks_result = await db.execute(
            select(func.count()).select_from(TaskQueue).where(TaskQueue.status == "pending")
        )
        pending_tasks = tasks_result.scalar() or 0

        suno_result = await db.execute(
            select(func.count()).select_from(SunoJob).where(SunoJob.status.in_(["pending", "processing"]))
        )
        active_suno_jobs = suno_result.scalar() or 0

        uploads_result = await db.execute(
            select(func.count()).select_from(YouTubeUpload).where(YouTubeUpload.upload_status == "published")
        )
        recent_uploads = uploads_result.scalar() or 0

        return DatabaseStatus(
            connected=True,
            total_songs=total_songs,
            pending_tasks=pending_tasks,
            active_suno_jobs=active_suno_jobs,
            recent_uploads=recent_uploads
        )

    except Exception as e:
        logger.error(f"Database status check failed: {e}")
        return DatabaseStatus(
            connected=False,
            total_songs=0,
            pending_tasks=0,
            active_suno_jobs=0,
            recent_uploads=0
        )


@router.get("/system/storage", response_model=StorageStatus)
async def get_storage_status(
    current_user: Annotated[object, Depends(get_current_user)]
) -> StorageStatus:
    """Get storage status."""
    download_folder = Path(settings.DOWNLOAD_FOLDER)
    watch_folder = Path(settings.WATCH_FOLDER)
    data_folder = Path(settings.DATA_FOLDER)
    cover_art_folder = Path(settings.COVER_ART_PATH)
    video_cache_folder = Path(settings.VIDEO_CACHE_PATH)

    return StorageStatus(
        download_folder_exists=download_folder.exists(),
        download_folder_size_mb=_get_folder_size(download_folder),
        watch_folder_exists=watch_folder.exists(),
        data_folder_exists=data_folder.exists(),
        cover_art_folder_exists=cover_art_folder.exists(),
        video_cache_folder_exists=video_cache_folder.exists()
    )


@router.get("/system/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> SystemMetrics:
    """Get comprehensive system metrics."""
    system_status = await get_system_status(current_user)
    database_status = await get_database_status(current_user, db)
    storage_status = await get_storage_status(current_user)

    return SystemMetrics(
        system=system_status,
        database=database_status,
        storage=storage_status
    )


@router.post("/system/cleanup")
async def cleanup_system(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Clean up old tasks and temporary files."""
    cleaned = {
        "completed_tasks_removed": 0,
        "temp_files_removed": 0
    }

    try:
        # Clean up old completed tasks (older than 30 days)
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)

        result = await db.execute(
            select(TaskQueue).where(
                TaskQueue.status == "completed",
                TaskQueue.completed_at < cutoff
            )
        )
        old_tasks = result.scalars().all()

        for task in old_tasks:
            await db.delete(task)
            cleaned["completed_tasks_removed"] += 1

        await db.commit()

        logger.info(f"System cleanup completed: {cleaned}")
        return {"status": "success", "cleaned": cleaned}

    except Exception as e:
        logger.error(f"System cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )
