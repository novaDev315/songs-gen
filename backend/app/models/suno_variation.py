"""SunoVariation model for tracking individual variations from Suno generation."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.suno_job import SunoJob


class SunoVariation(Base):
    """SunoVariation model for tracking individual audio variations from Suno.

    Suno generates 2 variations per upload. This model tracks each variation
    independently, allowing users to compare and select the best one.
    """

    __tablename__ = "suno_variations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to suno_job
    suno_job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suno_jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Suno-specific identifiers
    suno_variation_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    variation_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Audio data
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Selection status
    is_selected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Status tracking: pending, downloading, downloaded, failed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)

    # Audio metadata
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    downloaded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    selected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    suno_job: Mapped["SunoJob"] = relationship("SunoJob", back_populates="variations")

    def __repr__(self) -> str:
        """String representation."""
        return f"<SunoVariation(id={self.id}, job_id={self.suno_job_id}, index={self.variation_index}, selected={self.is_selected})>"
