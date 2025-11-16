"""Evaluation schemas for request/response validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class EvaluationBase(BaseModel):
    """Base schema for evaluation data."""

    audio_quality_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Audio quality score (0-100)")
    duration_seconds: Optional[float] = Field(None, ge=0.0, description="Song duration in seconds")
    file_size_mb: Optional[float] = Field(None, ge=0.0, description="File size in MB")
    sample_rate: Optional[int] = Field(None, ge=0, description="Audio sample rate (Hz)")
    bitrate: Optional[int] = Field(None, ge=0, description="Audio bitrate (kbps)")


class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation."""

    song_id: str = Field(..., min_length=1, max_length=255, description="Song ID to evaluate")


class ManualEvaluation(BaseModel):
    """Schema for manual evaluation update."""

    manual_rating: Optional[int] = Field(None, ge=1, le=10, description="Manual rating (1-10)")
    approved: Optional[bool] = Field(None, description="Approval status")
    notes: Optional[str] = Field(None, description="Evaluator notes")


class EvaluationUpdate(EvaluationBase):
    """Schema for updating evaluation."""

    manual_rating: Optional[int] = Field(None, ge=1, le=10)
    approved: Optional[bool] = None
    notes: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Schema for evaluation response."""

    id: int
    song_id: str

    # Automated metrics
    audio_quality_score: Optional[float] = None
    duration_seconds: Optional[float] = None
    file_size_mb: Optional[float] = None
    sample_rate: Optional[int] = None
    bitrate: Optional[int] = None

    # Manual review
    manual_rating: Optional[int] = None
    approved: Optional[bool] = None
    notes: Optional[str] = None

    # Metadata
    evaluated_by: Optional[int] = None
    evaluated_at: datetime

    # Include song details
    song_title: Optional[str] = None
    song_genre: Optional[str] = None
    song_status: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class BatchApproval(BaseModel):
    """Schema for batch approval."""

    song_ids: list[str] = Field(..., min_items=1, description="List of song IDs to approve")
    notes: Optional[str] = Field(None, description="Optional notes for all approvals")


class BatchApprovalResult(BaseModel):
    """Result of batch approval operation."""

    approved_count: int
    failed_count: int
    approved_song_ids: list[str]
    failed_song_ids: list[str]
    errors: dict[str, str]  # song_id -> error message


class EvaluationListMeta(BaseModel):
    """Pagination metadata for evaluation list."""

    total: int
    skip: int
    limit: int
    has_more: bool


class EvaluationList(BaseModel):
    """Paginated list of evaluations."""

    items: list[EvaluationResponse]
    meta: EvaluationListMeta
