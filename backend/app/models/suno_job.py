"""SunoJob model for tracking Suno generation jobs."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class SunoJob(Base):
    """SunoJob model for tracking Suno.com generation jobs."""

    __tablename__ = "suno_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to song
    song_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Suno-specific job ID
    suno_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    # Status values: pending, uploading, generating, completed, failed

    # Audio file information
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    downloaded_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    song: Mapped["Song"] = relationship("Song", back_populates="suno_jobs")

    def __repr__(self) -> str:
        """String representation."""
        return f"<SunoJob(id={self.id}, song_id={self.song_id}, status={self.status})>"
