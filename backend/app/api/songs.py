"""Song management API endpoints."""

import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.video_project import VideoProject
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


async def compute_song_effective_status(
    song: Song, db: AsyncSession
) -> tuple[str, Optional[str]]:
    """Compute effective status and youtube_url for a song based on video project."""
    result = await db.execute(
        select(VideoProject)
        .where(VideoProject.song_id == song.id)
        .order_by(VideoProject.created_at.desc())
        .limit(1)
    )
    video_project = result.scalar_one_or_none()

    youtube_url = None
    effective_status = song.status

    if video_project:
        youtube_url = video_project.youtube_url
        if youtube_url:
            effective_status = "published"
        elif video_project.output_path:
            effective_status = "video_ready"
        elif song.audio_path:
            effective_status = "audio_ready"

    return effective_status, youtube_url


@router.get("/songs", response_model=SongList)
async def list_songs(
    status_filter: Optional[str] = None,
    genre: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongList:
    """List all songs with filtering and pagination."""
    limit = min(limit, 100)

    query = select(Song)

    if status_filter:
        query = query.where(Song.status == status_filter)
    if genre:
        query = query.where(Song.genre == genre)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Song.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    songs = result.scalars().all()

    logger.info(f"User {current_user.username} listed {len(songs)} songs")

    items = []
    for song in songs:
        effective_status, youtube_url = await compute_song_effective_status(song, db)
        song_dict = {
            "id": song.id,
            "title": song.title,
            "genre": song.genre,
            "style_prompt": song.style_prompt,
            "lyrics": song.lyrics,
            "file_path": song.file_path,
            "status": song.status,
            "effective_status": effective_status,
            "metadata_json": song.metadata_json,
            "audio_path": song.audio_path,
            "youtube_url": youtube_url,
            "created_at": song.created_at,
            "updated_at": song.updated_at,
        }
        items.append(SongResponse(**song_dict))

    return SongList(
        items=items,
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
    """Get song details by ID."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    logger.info(f"User {current_user.username} retrieved song {song_id}")

    effective_status, youtube_url = await compute_song_effective_status(song, db)

    return SongResponse(
        id=song.id,
        title=song.title,
        genre=song.genre,
        style_prompt=song.style_prompt,
        lyrics=song.lyrics,
        file_path=song.file_path,
        status=song.status,
        effective_status=effective_status,
        metadata_json=song.metadata_json,
        audio_path=song.audio_path,
        youtube_url=youtube_url,
        created_at=song.created_at,
        updated_at=song.updated_at,
    )


@router.get("/songs/{song_id}/audio")
async def get_song_audio(
    song_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Stream audio file for a song."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    if not song.audio_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audio file available for song '{song_id}'",
        )

    audio_path = Path(song.audio_path)
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file not found at '{song.audio_path}'",
        )

    media_type = "audio/wav" if audio_path.suffix.lower() == ".wav" else "audio/mpeg"

    logger.info(f"User {current_user.username} streaming audio for song {song_id}")

    return FileResponse(
        path=str(audio_path),
        media_type=media_type,
        filename=f"{song.title or 'audio'}{audio_path.suffix}",
    )


@router.post("/songs", status_code=status.HTTP_201_CREATED, response_model=SongResponse)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SongResponse:
    """Create a new song manually."""
    song_id = str(uuid.uuid4())

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
    """Update song metadata."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    update_data = song_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(song, field, value)

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
    """Delete song and all related records."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    song_title = song.title

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
    """Get detailed song status in the pipeline."""
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

    latest_suno_status = None
    if song.suno_jobs:
        latest_suno = max(song.suno_jobs, key=lambda x: x.created_at)
        latest_suno_status = latest_suno.status

    evaluation_count = len(song.evaluations)
    is_evaluated = False
    is_approved = None
    manual_rating = None

    if song.evaluations:
        latest_eval = max(song.evaluations, key=lambda x: x.evaluated_at)
        is_evaluated = True
        is_approved = latest_eval.approved
        manual_rating = latest_eval.manual_rating

    latest_youtube_status = None
    video_url = None
    if song.youtube_uploads:
        latest_youtube = max(song.youtube_uploads, key=lambda x: x.uploaded_at)
        latest_youtube_status = latest_youtube.upload_status
        video_url = latest_youtube.video_url

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
    """Queue song for Suno upload."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    if song.status in ["uploading", "generating"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Song is already in status '{song.status}'",
        )

    task = TaskQueue(
        task_type="suno_upload",
        song_id=song_id,
        priority=min(priority, 100),
        status="pending",
    )

    db.add(task)

    song.status = "uploading"
    song.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(task)

    logger.info(f"User {current_user.username} queued song {song_id} for Suno upload")

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
    """Queue song for download from Suno."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    task = TaskQueue(
        task_type="suno_download",
        song_id=song_id,
        priority=min(priority, 100),
        status="pending",
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"User {current_user.username} queued song {song_id} for download")

    return {
        "message": f"Song '{song.title}' queued for download",
        "song_id": song_id,
        "task_id": task.id,
    }


@router.get("/songs/{song_id}/video-project")
async def get_song_video_project(
    song_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get video project for a song."""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{song_id}' not found",
        )

    project_result = await db.execute(
        select(VideoProject)
        .where(VideoProject.song_id == song_id)
        .order_by(VideoProject.created_at.desc())
        .limit(1)
    )
    project = project_result.scalar_one_or_none()

    logger.info(f"User {current_user.username} retrieved video project for song {song_id}")

    if not project:
        return {"video_project": None}

    return {
        "video_project": {
            "id": project.id,
            "song_id": project.song_id,
            "cover_type": project.cover_type,
            "cover_path": project.cover_path,
            "video_style": project.video_style,
            "lyric_style": project.lyric_style,
            "preview_path": project.preview_path,
            "output_path": project.output_path,
            "youtube_url": project.youtube_url,
            "youtube_video_id": project.youtube_video_id,
            "status": project.status,
            "progress": project.progress,
            "error_message": project.error_message,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        }
    }
