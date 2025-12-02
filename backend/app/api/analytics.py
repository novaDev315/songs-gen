"""Analytics API endpoints for song statistics and metrics."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.database import get_db
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.evaluation import Evaluation
from app.models.youtube_upload import YouTubeUpload
from app.models.video_project import VideoProject

logger = logging.getLogger(__name__)
router = APIRouter()


class OverviewStats(BaseModel):
    """Overview statistics."""
    total_songs: int
    songs_this_week: int
    songs_this_month: int
    published_songs: int
    pending_songs: int
    failed_songs: int


class GenreStats(BaseModel):
    """Statistics by genre."""
    genre: str
    count: int
    percentage: float


class TimeSeriesPoint(BaseModel):
    """Time series data point."""
    date: str
    count: int


class QualityStats(BaseModel):
    """Quality score statistics."""
    average_score: float
    min_score: float
    max_score: float
    songs_above_threshold: int
    songs_below_threshold: int


class AnalyticsDashboard(BaseModel):
    """Complete analytics dashboard data."""
    overview: OverviewStats
    genres: list[GenreStats]
    songs_over_time: list[TimeSeriesPoint]
    quality: Optional[QualityStats]


@router.get("/analytics/overview", response_model=OverviewStats)
async def get_overview_stats(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> OverviewStats:
    """Get overview statistics."""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Total songs
    total_result = await db.execute(select(func.count()).select_from(Song))
    total_songs = total_result.scalar() or 0

    # Songs this week
    week_result = await db.execute(
        select(func.count()).select_from(Song).where(Song.created_at >= week_ago)
    )
    songs_this_week = week_result.scalar() or 0

    # Songs this month
    month_result = await db.execute(
        select(func.count()).select_from(Song).where(Song.created_at >= month_ago)
    )
    songs_this_month = month_result.scalar() or 0

    # Status counts
    published_result = await db.execute(
        select(func.count()).select_from(Song).where(Song.status == "published")
    )
    published_songs = published_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count()).select_from(Song).where(Song.status == "pending")
    )
    pending_songs = pending_result.scalar() or 0

    failed_result = await db.execute(
        select(func.count()).select_from(Song).where(Song.status == "failed")
    )
    failed_songs = failed_result.scalar() or 0

    return OverviewStats(
        total_songs=total_songs,
        songs_this_week=songs_this_week,
        songs_this_month=songs_this_month,
        published_songs=published_songs,
        pending_songs=pending_songs,
        failed_songs=failed_songs
    )


@router.get("/analytics/genres", response_model=list[GenreStats])
async def get_genre_stats(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> list[GenreStats]:
    """Get statistics grouped by genre."""
    result = await db.execute(
        select(Song.genre, func.count(Song.id).label("count"))
        .group_by(Song.genre)
        .order_by(func.count(Song.id).desc())
    )
    rows = result.all()

    total = sum(row.count for row in rows)
    if total == 0:
        return []

    return [
        GenreStats(
            genre=row.genre or "Unknown",
            count=row.count,
            percentage=round(row.count / total * 100, 1)
        )
        for row in rows
    ]


@router.get("/analytics/timeline", response_model=list[TimeSeriesPoint])
async def get_timeline_stats(
    current_user: Annotated[object, Depends(get_current_user)],
    days: int = Query(default=30, ge=7, le=365),
    db: AsyncSession = Depends(get_db)
) -> list[TimeSeriesPoint]:
    """Get song creation timeline."""
    start_date = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(Song.created_at).label("date"),
            func.count(Song.id).label("count")
        )
        .where(Song.created_at >= start_date)
        .group_by(func.date(Song.created_at))
        .order_by(func.date(Song.created_at))
    )
    rows = result.all()

    return [
        TimeSeriesPoint(date=str(row.date), count=row.count)
        for row in rows
    ]


@router.get("/analytics/quality", response_model=Optional[QualityStats])
async def get_quality_stats(
    current_user: Annotated[object, Depends(get_current_user)],
    threshold: float = Query(default=3.0, ge=1, le=5),
    db: AsyncSession = Depends(get_db)
) -> Optional[QualityStats]:
    """Get quality score statistics from evaluations (rating is 1-5 scale)."""
    result = await db.execute(
        select(
            func.avg(Evaluation.rating).label("avg"),
            func.min(Evaluation.rating).label("min"),
            func.max(Evaluation.rating).label("max"),
            func.count(Evaluation.id).label("total")
        ).where(Evaluation.rating.isnot(None))
    )
    row = result.one_or_none()

    if not row or row.total == 0:
        return None

    # Count above/below threshold (rating is 1-5)
    above_result = await db.execute(
        select(func.count()).select_from(Evaluation).where(
            Evaluation.rating.isnot(None),
            Evaluation.rating >= threshold
        )
    )
    above = above_result.scalar() or 0

    below_result = await db.execute(
        select(func.count()).select_from(Evaluation).where(
            Evaluation.rating.isnot(None),
            Evaluation.rating < threshold
        )
    )
    below = below_result.scalar() or 0

    # Convert 1-5 scale to percentage for display
    avg_pct = (row.avg or 0) * 20  # 5 -> 100%
    min_pct = (row.min or 0) * 20
    max_pct = (row.max or 0) * 20

    return QualityStats(
        average_score=round(avg_pct, 1),
        min_score=round(min_pct, 1),
        max_score=round(max_pct, 1),
        songs_above_threshold=above,
        songs_below_threshold=below
    )


@router.get("/analytics/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    current_user: Annotated[object, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
) -> AnalyticsDashboard:
    """Get complete analytics dashboard data."""
    overview = await get_overview_stats(current_user, db)
    genres = await get_genre_stats(current_user, db)
    timeline = await get_timeline_stats(current_user, days=30, db=db)
    quality = await get_quality_stats(current_user, threshold=3.0, db=db)

    return AnalyticsDashboard(
        overview=overview,
        genres=genres,
        songs_over_time=timeline,
        quality=quality
    )
