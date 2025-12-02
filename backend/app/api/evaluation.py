"""Evaluation API endpoints for song quality assessment."""

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.user import User
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse, EvaluationUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


class EvaluationList(BaseModel):
    """Schema for paginated evaluation list."""
    items: list[EvaluationResponse]
    total: int
    skip: int
    limit: int


@router.get("/evaluations", response_model=EvaluationList)
async def list_evaluations(
    current_user: Annotated[User, Depends(get_current_user)],
    song_id: Optional[str] = None,
    approved: Optional[bool] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> EvaluationList:
    """List evaluations with optional filtering."""
    query = select(Evaluation)

    if song_id:
        query = query.where(Evaluation.song_id == song_id)
    if approved is not None:
        query = query.where(Evaluation.approved == approved)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Evaluation.evaluated_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    evaluations = result.scalars().all()

    logger.info(f"User {current_user.username} listed {len(evaluations)} evaluations")

    return EvaluationList(
        items=[EvaluationResponse.model_validate(e) for e in evaluations],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/evaluations/pending")
async def get_pending_evaluations(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """Get songs that need evaluation."""
    result = await db.execute(
        select(Song)
        .where(Song.status == "downloaded")
        .where(~Song.evaluations.any())
        .order_by(Song.created_at.desc())
        .limit(limit)
    )
    pending = result.scalars().all()

    logger.info(f"User {current_user.username} retrieved {len(pending)} pending evaluations")

    return [
        {
            "id": song.id,
            "title": song.title,
            "genre": song.genre,
            "created_at": song.created_at.isoformat(),
        }
        for song in pending
    ]


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> EvaluationResponse:
    """Get a specific evaluation."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    return EvaluationResponse.model_validate(evaluation)


@router.post("/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    evaluation_data: EvaluationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> EvaluationResponse:
    """Create a new evaluation for a song."""
    # Verify song exists
    song_result = await db.execute(
        select(Song).where(Song.id == evaluation_data.song_id)
    )
    song = song_result.scalar_one_or_none()

    if not song:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with ID '{evaluation_data.song_id}' not found"
        )

    evaluation = Evaluation(
        song_id=evaluation_data.song_id,
        quality_score=evaluation_data.quality_score,
        vocal_quality=evaluation_data.vocal_quality,
        instrumental_quality=evaluation_data.instrumental_quality,
        mix_quality=evaluation_data.mix_quality,
        approved=evaluation_data.approved,
        notes=evaluation_data.notes,
        evaluated_by_id=current_user.id,
    )

    db.add(evaluation)

    # Update song status if approved
    if evaluation_data.approved:
        song.status = "evaluated"

    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"User {current_user.username} created evaluation for song {evaluation_data.song_id}")

    return EvaluationResponse.model_validate(evaluation)


@router.put("/evaluations/{evaluation_id}", response_model=EvaluationResponse)
async def update_evaluation(
    evaluation_id: int,
    evaluation_update: EvaluationUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> EvaluationResponse:
    """Update an existing evaluation."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    update_data = evaluation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evaluation, field, value)

    await db.commit()
    await db.refresh(evaluation)

    logger.info(f"User {current_user.username} updated evaluation {evaluation_id}")

    return EvaluationResponse.model_validate(evaluation)


@router.delete("/evaluations/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> None:
    """Delete an evaluation."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    await db.delete(evaluation)
    await db.commit()

    logger.info(f"User {current_user.username} deleted evaluation {evaluation_id}")


@router.post("/evaluations/{evaluation_id}/approve")
async def approve_evaluation(
    evaluation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Approve a song based on its evaluation."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    evaluation.approved = True

    # Update song status
    song_result = await db.execute(
        select(Song).where(Song.id == evaluation.song_id)
    )
    song = song_result.scalar_one_or_none()
    if song:
        song.status = "evaluated"

    await db.commit()

    logger.info(f"User {current_user.username} approved evaluation {evaluation_id}")

    return {"message": "Evaluation approved", "evaluation_id": evaluation_id}


@router.post("/evaluations/{evaluation_id}/reject")
async def reject_evaluation(
    evaluation_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Reject a song based on its evaluation."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.id == evaluation_id)
    )
    evaluation = result.scalar_one_or_none()

    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )

    evaluation.approved = False

    await db.commit()

    logger.info(f"User {current_user.username} rejected evaluation {evaluation_id}")

    return {"message": "Evaluation rejected", "evaluation_id": evaluation_id}
