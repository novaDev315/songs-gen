"""TaskQueue model for persistent task management."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class TaskQueue(Base):
    """TaskQueue model for persistent background task queue."""

    __tablename__ = "task_queue"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Task type (e.g., "suno_upload", "suno_download", "youtube_upload", "evaluate")
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Foreign key to song (optional - some tasks may not be song-specific)
    song_id: Mapped[str | None] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=True, index=True
    )

    # Task payload (JSON string)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    # Status values: pending, running, completed, failed

    # Priority (higher = more urgent)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)

    # Retry management
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    song: Mapped["Song | None"] = relationship("Song", back_populates="tasks")

    # Composite index for efficient queue queries
    __table_args__ = (
        Index("idx_task_queue_status_priority_created", "status", "priority", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<TaskQueue(id={self.id}, type={self.task_type}, status={self.status})>"
