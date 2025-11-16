"""YouTube upload API endpoints."""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.youtube_upload import YouTubeUpload
from app.schemas.youtube import (
    OAuthCallback,
    OAuthURL,
    YouTubeUploadCreate,
    YouTubeUploadList,
    YouTubeUploadListMeta,
    YouTubeUploadResponse,
)
from app.services.youtube_uploader import get_youtube_uploader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/youtube/uploads", response_model=YouTubeUploadList)
async def list_uploads(
    upload_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> YouTubeUploadList:
    """
    List YouTube uploads with filtering and pagination.

    - **upload_status**: Filter by upload status (pending, uploading, processing, published, failed)
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    # Limit max results
    limit = min(limit, 100)

    # Build query with song relationship
    query = select(YouTubeUpload).options(selectinload(YouTubeUpload.song))

    # Apply filter
    if upload_status:
        query = query.where(YouTubeUpload.upload_status == upload_status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by upload date (most recent first)
    query = query.order_by(YouTubeUpload.uploaded_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    uploads = result.scalars().all()

    # Build response with song details
    items = []
    for upload in uploads:
        upload_dict = YouTubeUploadResponse.model_validate(upload).model_dump()
        if upload.song:
            upload_dict["song_title"] = upload.song.title
            upload_dict["song_genre"] = upload.song.genre
        items.append(YouTubeUploadResponse(**upload_dict))

    logger.info(
        f"User {current_user.username} listed {len(items)} YouTube uploads (total: {total})"
    )

    return YouTubeUploadList(
        items=items,
        meta=YouTubeUploadListMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        ),
    )


@router.get("/youtube/uploads/{upload_id}", response_model=YouTubeUploadResponse)
async def get_upload(
    upload_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> YouTubeUploadResponse:
    """
    Get YouTube upload details.

    - **upload_id**: Upload ID to retrieve
    """
    result = await db.execute(
        select(YouTubeUpload)
        .where(YouTubeUpload.id == upload_id)
        .options(selectinload(YouTubeUpload.song))
    )
    upload = result.scalar_one_or_none()

    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"YouTube upload with ID {upload_id} not found",
        )

    # Build response with song details
    upload_dict = YouTubeUploadResponse.model_validate(upload).model_dump()
    if upload.song:
        upload_dict["song_title"] = upload.song.title
        upload_dict["song_genre"] = upload.song.genre

    logger.info(f"User {current_user.username} retrieved YouTube upload {upload_id}")

    return YouTubeUploadResponse(**upload_dict)


@router.post("/youtube/upload", status_code=status.HTTP_201_CREATED, response_model=YouTubeUploadResponse)
async def upload_to_youtube(
    upload_data: YouTubeUploadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> YouTubeUploadResponse:
    """
    Queue song for YouTube upload.

    Verifies song is approved and creates upload record + task.

    - **upload_data**: YouTube upload metadata (song_id, title, description, tags, privacy)
    """
    # Find song
    result = await db.execute(
        select(Song)
        .where(Song.id == upload_data.song_id)
        .options(selectinload(Song.evaluations))
    )
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{upload_data.song_id}' not found",
        )

    # Verify song is evaluated/approved
    if song.status not in ["evaluated", "uploaded"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Song must be evaluated before uploading (current status: {song.status})",
        )

    # Check if song has approved evaluation
    if song.evaluations:
        latest_eval = max(song.evaluations, key=lambda x: x.evaluated_at)
        if latest_eval.approved is not True:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Song must be approved before YouTube upload",
            )
    else:
        logger.warning(
            f"Song {song.id} is in status '{song.status}' but has no evaluation - allowing upload"
        )

    # Create YouTube upload record
    youtube_upload = YouTubeUpload(
        song_id=upload_data.song_id,
        title=upload_data.title,
        description=upload_data.description,
        tags=upload_data.tags,
        privacy=upload_data.privacy,
        upload_status="pending",
        uploaded_by=current_user.id,
        uploaded_at=datetime.utcnow(),
    )

    db.add(youtube_upload)

    # Create task queue entry
    task = TaskQueue(
        task_type="youtube_upload",
        song_id=song.id,
        priority=50,  # Medium priority
        status="pending",
    )
    db.add(task)

    await db.commit()
    await db.refresh(youtube_upload)
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} queued song {song.id} for YouTube upload (upload {youtube_upload.id}, task {task.id})"
    )

    # Build response
    upload_dict = YouTubeUploadResponse.model_validate(youtube_upload).model_dump()
    upload_dict["song_title"] = song.title
    upload_dict["song_genre"] = song.genre

    return YouTubeUploadResponse(**upload_dict)


@router.get("/youtube/oauth-url", response_model=OAuthURL)
async def get_oauth_url(
    current_user: User = Depends(get_current_user),
) -> OAuthURL:
    """
    Get YouTube OAuth authorization URL.

    Generates a Google OAuth2 authorization URL for YouTube Data API access.
    User should be redirected to this URL to grant permissions.

    Returns:
    - **authorization_url**: URL to redirect user for OAuth authorization
    - **state**: CSRF protection state parameter (optional)

    Raises:
    - **500**: If OAuth credentials not configured or URL generation fails
    """
    logger.info(f"User {current_user.username} requested YouTube OAuth URL")

    try:
        uploader = get_youtube_uploader()
        auth_url = uploader.get_auth_url()

        logger.info(f"Generated YouTube OAuth URL for user {current_user.username}")

        return OAuthURL(
            authorization_url=auth_url,
            state=None  # State is handled internally by google-auth-oauthlib
        )

    except ValueError as e:
        logger.error(f"Error generating OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate OAuth URL: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating OAuth URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error generating OAuth URL"
        )


@router.post("/youtube/oauth-callback")
async def oauth_callback(
    callback_data: OAuthCallback,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Handle YouTube OAuth callback.

    Exchanges the authorization code for access/refresh tokens and stores them
    securely for future YouTube uploads.

    - **callback_data**: OAuth authorization code and optional state

    Returns:
    - Success message with authentication status

    Raises:
    - **400**: If OAuth authentication fails (invalid code)
    - **500**: If token storage fails
    """
    logger.info(f"User {current_user.username} completed YouTube OAuth callback")

    try:
        uploader = get_youtube_uploader()
        success = uploader.handle_oauth_callback(callback_data.code)

        if success:
            logger.info(f"YouTube OAuth successful for user {current_user.username}")
            return {
                "message": "YouTube authentication successful",
                "status": "authenticated",
                "user": current_user.username
            }
        else:
            logger.warning(f"YouTube OAuth failed for user {current_user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth authentication failed - invalid authorization code"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback error for user {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )


@router.delete("/youtube/uploads/{upload_id}")
async def delete_upload_record(
    upload_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Delete YouTube upload record from database.

    NOTE: This does NOT delete the video from YouTube - only the local record.

    - **upload_id**: Upload ID to delete
    """
    result = await db.execute(select(YouTubeUpload).where(YouTubeUpload.id == upload_id))
    upload = result.scalar_one_or_none()

    if not upload:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"YouTube upload with ID {upload_id} not found",
        )

    song_id = upload.song_id
    video_id = upload.video_id

    await db.delete(upload)
    await db.commit()

    logger.info(
        f"User {current_user.username} deleted YouTube upload record {upload_id} (song: {song_id}, video: {video_id})"
    )

    return {
        "message": f"YouTube upload record {upload_id} deleted successfully",
        "upload_id": upload_id,
        "song_id": song_id,
        "video_id": video_id,
        "note": "This only deleted the local record - the video may still exist on YouTube",
    }
