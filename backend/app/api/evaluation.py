"""Evaluation API endpoints for song quality assessment."""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.schemas.evaluation import (
    BatchApproval,
    BatchApprovalResult,
    EvaluationCreate,
    EvaluationList,
    EvaluationListMeta,
    EvaluationResponse,
    EvaluationUpdate,
    ManualEvaluation,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/evaluations", response_model=EvaluationList)
async def list_evaluations(
    approved: Optional[bool] = None,
    min_rating: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationList:
    """
    List all evaluations with filtering and pagination.

    - **approved**: Filter by approval status (true/false)
    - **min_rating**: Minimum manual rating (1-10)
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 100)
    """
    # Limit max results
    limit = min(limit, 100)

    # Build query with song relationship
    query = select(Evaluation).options(selectinload(Evaluation.song))

    # Apply filters
    if approved is not None:
        query = query.where(Evaluation.approved == approved)
    if min_rating is not None:
        query = query.where(
            Evaluation.manual_rating.isnot(None),
            Evaluation.manual_rating >= min_rating,
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by evaluation date (most recent first)
    query = query.order_by(Evaluation.evaluated_at.desc())

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    evaluations = result.scalars().all()

    # Build response with song details
    items = []
    for evaluation in evaluations:
        eval_dict = EvaluationResponse.model_validate(evaluation).model_dump()
        if evaluation.song:
            eval_dict["song_title"] = evaluation.song.title
            eval_dict["song_genre"] = evaluation.song.genre
            eval_dict["song_status"] = evaluation.song.status
        items.append(EvaluationResponse(**eval_dict))

    logger.info(
        f"User {current_user.username} listed {len(items)} evaluations (total: {total})"
    )

    return EvaluationList(
        items=items,
        meta=EvaluationListMeta(
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        ),
    )


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationResponse:
    """
    Get evaluation details.

    - **evaluation_id**: Evaluation ID to retrieve
    """
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(selectinload(Evaluation.song))
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found",
        )

    # Build response with song details
    eval_dict = EvaluationResponse.model_validate(evaluation).model_dump()
    if evaluation.song:
        eval_dict["song_title"] = evaluation.song.title
        eval_dict["song_genre"] = evaluation.song.genre
        eval_dict["song_status"] = evaluation.song.status

    logger.info(f"User {current_user.username} retrieved evaluation {evaluation_id}")

    return EvaluationResponse(**eval_dict)


@router.post("/evaluations", status_code=status.HTTP_201_CREATED, response_model=EvaluationResponse)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationResponse:
    """
    Create manual evaluation for a song.

    - **evaluation_data**: Evaluation metrics including song_id and quality scores
    """
    # Verify song exists
    result = await db.execute(select(Song).where(Song.id == evaluation_data.song_id))
    song = result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{evaluation_data.song_id}' not found",
        )

    # Create evaluation
    evaluation = Evaluation(
        song_id=evaluation_data.song_id,
        audio_quality_score=evaluation_data.audio_quality_score,
        duration_seconds=evaluation_data.duration_seconds,
        file_size_mb=evaluation_data.file_size_mb,
        sample_rate=evaluation_data.sample_rate,
        bitrate=evaluation_data.bitrate,
        evaluated_by=current_user.id,
        evaluated_at=datetime.now(timezone.utc),
    )

    db.add(evaluation)
    await db.commit()
    await db.refresh(evaluation)

    logger.info(
        f"User {current_user.username} created evaluation {evaluation.id} for song {evaluation_data.song_id}"
    )

    # Build response
    eval_dict = EvaluationResponse.model_validate(evaluation).model_dump()
    eval_dict["song_title"] = song.title
    eval_dict["song_genre"] = song.genre
    eval_dict["song_status"] = song.status

    return EvaluationResponse(**eval_dict)


@router.put("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: int,
    manual_eval: ManualEvaluation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EvaluationResponse:
    """
    Update manual evaluation fields.

    - **evaluation_id**: Evaluation ID to update
    - **manual_eval**: Manual evaluation data (rating, approved, notes)
    """
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(selectinload(Evaluation.song))
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found",
        )

    # Update manual fields
    update_data = manual_eval.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(evaluation, field, value)

    # Update evaluator and timestamp
    evaluation.evaluated_by = current_user.id
    evaluation.evaluated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(evaluation)

    # Build response with song details
    eval_dict = EvaluationResponse.model_validate(evaluation).model_dump()
    if evaluation.song:
        eval_dict["song_title"] = evaluation.song.title
        eval_dict["song_genre"] = evaluation.song.genre
        eval_dict["song_status"] = evaluation.song.status

    logger.info(
        f"User {current_user.username} updated evaluation {evaluation_id} (approved: {evaluation.approved})"
    )

    return EvaluationResponse(**eval_dict)


@router.post("/evaluations/{evaluation_id}/approve")
async def approve_song(
    evaluation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Approve song for YouTube upload.

    Sets evaluation approved=True, updates song status to 'evaluated',
    and creates a YouTube upload task.

    - **evaluation_id**: Evaluation ID to approve
    """
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(selectinload(Evaluation.song))
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found",
        )

    if evaluation.approved is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Song is already approved",
        )

    # Approve evaluation
    evaluation.approved = True
    evaluation.evaluated_by = current_user.id
    evaluation.evaluated_at = datetime.now(timezone.utc)

    # Update song status
    song = evaluation.song
    song.status = "evaluated"
    song.updated_at = datetime.now(timezone.utc)

    # Create YouTube upload task
    task = TaskQueue(
        task_type="youtube_upload",
        song_id=song.id,
        priority=50,  # Medium priority
        status="pending",
    )
    db.add(task)

    await db.commit()
    await db.refresh(task)

    logger.info(
        f"User {current_user.username} approved song {song.id} (evaluation {evaluation_id}, task {task.id})"
    )

    return {
        "message": f"Song '{song.title}' approved for YouTube upload",
        "evaluation_id": evaluation_id,
        "song_id": song.id,
        "task_id": task.id,
    }


@router.post("/evaluations/{evaluation_id}/reject")
async def reject_song(
    evaluation_id: int,
    notes: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Reject song.

    Sets evaluation approved=False, adds notes, and updates song status to 'failed'.

    - **evaluation_id**: Evaluation ID to reject
    - **notes**: Reason for rejection
    """
    result = await db.execute(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(selectinload(Evaluation.song))
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation with ID {evaluation_id} not found",
        )

    # Reject evaluation
    evaluation.approved = False
    evaluation.notes = notes
    evaluation.evaluated_by = current_user.id
    evaluation.evaluated_at = datetime.now(timezone.utc)

    # Update song status
    song = evaluation.song
    song.status = "failed"
    song.updated_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(
        f"User {current_user.username} rejected song {song.id} (evaluation {evaluation_id}): {notes}"
    )

    return {
        "message": f"Song '{song.title}' rejected",
        "evaluation_id": evaluation_id,
        "song_id": song.id,
        "notes": notes,
    }


@router.post("/evaluations/batch-approve", response_model=BatchApprovalResult)
async def batch_approve(
    batch: BatchApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BatchApprovalResult:
    """
    Approve multiple songs in batch.

    For each song:
    - Finds or creates evaluation
    - Sets approved=True
    - Updates song status to 'evaluated'
    - Creates YouTube upload task

    - **batch**: List of song IDs to approve and optional notes
    """
    approved_song_ids = []
    failed_song_ids = []
    errors = {}

    for song_id in batch.song_ids:
        try:
            # Find song
            result = await db.execute(
                select(Song)
                .where(Song.id == song_id)
                .options(selectinload(Song.evaluations))
            )
            song = result.scalar_one_or_none()

            if not song:
                failed_song_ids.append(song_id)
                errors[song_id] = "Song not found"
                continue

            # Find or create evaluation
            evaluation = None
            if song.evaluations:
                # Use most recent evaluation
                evaluation = max(song.evaluations, key=lambda x: x.evaluated_at)
            else:
                # Create new evaluation
                evaluation = Evaluation(
                    song_id=song_id,
                    evaluated_by=current_user.id,
                    evaluated_at=datetime.now(timezone.utc),
                )
                db.add(evaluation)

            # Approve evaluation
            evaluation.approved = True
            evaluation.notes = batch.notes
            evaluation.evaluated_by = current_user.id
            evaluation.evaluated_at = datetime.now(timezone.utc)

            # Update song status
            song.status = "evaluated"
            song.updated_at = datetime.now(timezone.utc)

            # Create YouTube upload task
            task = TaskQueue(
                task_type="youtube_upload",
                song_id=song_id,
                priority=50,
                status="pending",
            )
            db.add(task)

            approved_song_ids.append(song_id)

        except Exception as e:
            logger.error(f"Error approving song {song_id}: {str(e)}")
            failed_song_ids.append(song_id)
            errors[song_id] = str(e)

    await db.commit()

    logger.info(
        f"User {current_user.username} batch approved {len(approved_song_ids)} songs, {len(failed_song_ids)} failed"
    )

    return BatchApprovalResult(
        approved_count=len(approved_song_ids),
        failed_count=len(failed_song_ids),
        approved_song_ids=approved_song_ids,
        failed_song_ids=failed_song_ids,
        errors=errors,
    )


@router.get("/evaluations/pending")
async def pending_evaluations(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """
    Get songs pending manual evaluation.

    Returns songs with status 'downloaded' that either:
    - Have no evaluation, OR
    - Have evaluation but not yet approved/rejected

    - **limit**: Maximum number of songs to return (max 100)
    """
    limit = min(limit, 100)

    # Find songs with status 'downloaded'
    result = await db.execute(
        select(Song)
        .where(Song.status == "downloaded")
        .options(selectinload(Song.evaluations))
        .order_by(Song.created_at.asc())
        .limit(limit)
    )
    songs = result.scalars().all()

    # Filter songs that need evaluation
    pending = []
    for song in songs:
        needs_evaluation = False

        if not song.evaluations:
            # No evaluation at all
            needs_evaluation = True
        else:
            # Check if any evaluation is approved/rejected
            latest_eval = max(song.evaluations, key=lambda x: x.evaluated_at)
            if latest_eval.approved is None:
                needs_evaluation = True

        if needs_evaluation:
            pending.append({
                "song_id": song.id,
                "title": song.title,
                "genre": song.genre,
                "created_at": song.created_at.isoformat(),
                "has_evaluation": len(song.evaluations) > 0,
                "evaluation_id": song.evaluations[0].id if song.evaluations else None,
            })

    logger.info(f"User {current_user.username} retrieved {len(pending)} pending evaluations")

    return pending
