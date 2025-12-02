"""YouTubeUpload model for tracking YouTube uploads."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song
    from app.models.user import User


class YouTubeUpload(Base):
    """YouTubeUpload model for tracking YouTube video uploads."""

    __tablename__ = "youtube_uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to song
    song_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # YouTube video information
    video_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Upload status
    upload_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    # Status values: pending, uploading, processing, published, failed

    # Video metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # Comma-separated
    privacy: Mapped[str] = mapped_column(
        String(20), nullable=False, default="private"
    )  # private, unlisted, public

    # Error tracking
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Uploader tracking
    uploaded_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    song: Mapped["Song"] = relationship("Song", back_populates="youtube_uploads")
    uploader: Mapped["User"] = relationship(
        "User", back_populates="youtube_uploads", foreign_keys=[uploaded_by]
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<YouTubeUpload(id={self.id}, song_id={self.song_id}, status={self.upload_status})>"
