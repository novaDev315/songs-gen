"""Song management API endpoints."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.youtube_upload import YouTubeUpload
from app.schemas.song import (
    SongCreate,
    SongList,
    SongListMeta,
    SongResponse,
    SongStatus,
    SongUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/songs", response_model=SongList)
async def list_songs(
    status_filter: Optional[str] = None,
    genre: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongList:
    """
    List all songs with filtering and pagination.

    - **status_filter**: Filter by song status (pending, uploading, generating, downloaded, evaluated, uploaded, failed)
    - **genre**: Filter by music genre
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    # Limit max results
    limit = min(limit, 100)

    # Build query
    query = select(Song)

    # Apply filters
    if status_filter:
        query = query.where(Song.status == status_filter)
    if genre:
        query = query.where(Song.genre == genre)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering
    query = query.order_by(Song.created_at.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    songs = result.scalars().all()

    logger.info(
        f"User {current_user.username} listed {len(songs)} songs (total: {total}, skip: {skip}, limit: {limit})"
    )

    return SongList(
        items=[SongResponse.model_validate(song) for song in songs],
        meta=SongListMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(songs)) < total,
        ),
    )


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongResponse:
    """
    Get song details by ID.

    - **song_id**: Unique song identifier
    """
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    logger.info(f"User {current_user.username} retrieved song {song_id}")

    return SongResponse.model_validate(song)


@router.post("/songs", status_code=status.HTTP_201_CREATED, response_model=SongResponse)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongResponse:
    """
    Create a new song manually.

    - **song_data**: Song metadata including title, genre, style_prompt, lyrics, and file_path
    """
    # Generate unique ID
    song_id = str(uuid.uuid4())

    # Create song model
    song = Song(
        id=song_id,
        title=song_data.title,
        genre=song_data.genre,
        style_prompt=song_data.style_prompt,
        lyrics=song_data.lyrics,
        file_path=song_data.file_path,
        metadata_json=song_data.metadata_json,
        status="pending",
    )

    db.add(song)
    await db.commit()
    await db.refresh(song)

    logger.info(f"User {current_user.username} created song {song_id} - {song_data.title}")

    return SongResponse.model_validate(song)


@router.put("/songs/{song_id}", response_model=SongResponse)
async def update_song(
    song_id: str,
    song_update: SongUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongResponse:
    """
    Update song metadata.

    - **song_id**: Song ID to update
    - **song_update**: Fields to update (all optional)
    """
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    # Update fields if provided
    update_data = song_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(song, field, value)

    # Update timestamp
    song.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(song)

    logger.info(f"User {current_user.username} updated song {song_id}")

    return SongResponse.model_validate(song)


@router.delete("/songs/{song_id}")
async def delete_song(
    song_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Delete song and all related records.

    - **song_id**: Song ID to delete

    Cascade deletes: suno_jobs, evaluations, youtube_uploads, tasks
    """
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    song_title = song.title

    # Delete song (cascade will handle related records)
    await db.delete(song)
    await db.commit()

    logger.info(f"User {current_user.username} deleted song {song_id} - {song_title}")

    return {
        "message": f"Song '{song_title}' deleted successfully",
        "deleted_id": song_id,
    }


@router.get("/songs/{song_id}/status", response_model=SongStatus)
async def get_song_status(
    song_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongStatus:
    """
    Get detailed song status in the pipeline.

    Includes:
    - Suno job status
    - Evaluation status
    - YouTube upload status
    - Pending/running/failed tasks

    - **song_id**: Song ID to check
    """
    # Load song with all relationships
    result = await db.execute(
        select(Song)
        .where(Song.id == song_id)
        .options(
            selectinload(Song.suno_jobs),
            selectinload(Song.evaluations),
            selectinload(Song.youtube_uploads),
            selectinload(Song.tasks),
        )
    )
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    # Get latest suno job status
    latest_suno_status = None
    if song.suno_jobs:
        latest_suno = max(song.suno_jobs, key=lambda x: x.created_at)
        latest_suno_status = latest_suno.status

    # Get evaluation status
    evaluation_count = len(song.evaluations)
    is_evaluated = False
    is_approved = None
    manual_rating = None

    if song.evaluations:
        latest_eval = max(song.evaluations, key=lambda x: x.evaluated_at)
        is_evaluated = True
        is_approved = latest_eval.approved
        manual_rating = latest_eval.manual_rating

    # Get YouTube upload status
    latest_youtube_status = None
    video_url = None
    if song.youtube_uploads:
        latest_youtube = max(song.youtube_uploads, key=lambda x: x.uploaded_at)
        latest_youtube_status = latest_youtube.upload_status
        video_url = latest_youtube.video_url

    # Count tasks by status
    pending_tasks = sum(1 for task in song.tasks if task.status == "pending")
    running_tasks = sum(1 for task in song.tasks if task.status == "running")
    failed_tasks = sum(1 for task in song.tasks if task.status == "failed")

    logger.info(f"User {current_user.username} checked status for song {song_id}")

    return SongStatus(
        id=song.id,
        title=song.title,
        status=song.status,
        created_at=song.created_at,
        updated_at=song.updated_at,
        suno_job_count=len(song.suno_jobs),
        latest_suno_status=latest_suno_status,
        evaluation_count=evaluation_count,
        is_evaluated=is_evaluated,
        is_approved=is_approved,
        manual_rating=manual_rating,
        youtube_upload_count=len(song.youtube_uploads),
        latest_youtube_status=latest_youtube_status,
        video_url=video_url,
        pending_tasks=pending_tasks,
        running_tasks=running_tasks,
        failed_tasks=failed_tasks,
    )


@router.post("/songs/{song_id}/upload-to-suno")
async def upload_to_suno(
    song_id: str,
    priority: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Queue song for Suno upload.

    Creates a task in the queue and updates song status.

    - **song_id**: Song ID to upload
    - **priority**: Task priority (0-100, default 0)
    """
    # Find song
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    # Check if already uploading/generating
    if song.status in ["uploading", "generating"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Song is already in status '{song.status}'",
        )

    # Create task queue entry
    task = TaskQueue(
        task_type="suno_upload",
        song_id=song_id,
        priority=min(priority, 100),
        status="pending",
    )

    db.add(task)

    # Update song status
    song.status = "uploading"
    song.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(task)

    logger.info(f"User {current_user.username} queued song {song_id} for Suno upload (task {task.id})")

    return {
        "message": f"Song '{song.title}' queued for Suno upload",
        "song_id": song_id,
        "task_id": task.id,
        "status": song.status,
    }


@router.post("/songs/{song_id}/download")
async def download_song(
    song_id: str,
    priority: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Queue song for download from Suno.

    Creates a download task in the queue.

    - **song_id**: Song ID to download
    - **priority**: Task priority (0-100, default 0)
    """
    # Find song
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    # Check if song is in generating status
    if song.status != "generating":
        logger.warning(
            f"Song {song_id} download requested but status is '{song.status}' (expected 'generating')"
        )

    # Create task queue entry
    task = TaskQueue(
        task_type="suno_download",
        song_id=song_id,
        priority=min(priority, 100),
        status="pending",
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"User {current_user.username} queued song {song_id} for download (task {task.id})")

    return {
        "message": f"Song '{song.title}' queued for download",
        "song_id": song_id,
        "task_id": task.id,
    }
