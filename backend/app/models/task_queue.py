"""TaskQueue model for background job processing."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class TaskQueue(Base):
    """TaskQueue model for managing background tasks."""

    __tablename__ = "task_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Task type: suno_upload, suno_download, evaluate, youtube_upload, video_generate
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Foreign key to song (optional, some tasks may not be song-specific)
    song_id: Mapped[Optional[str]] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Task status: pending, running, completed, failed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )

    # Task priority (higher = more important)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)

    # Task payload (JSON string)
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Result data (JSON string)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    song: Mapped[Optional["Song"]] = relationship("Song", back_populates="tasks")

    def __repr__(self) -> str:
        """String representation."""
        return f"<TaskQueue(id={self.id}, type={self.task_type}, status={self.status})>"
