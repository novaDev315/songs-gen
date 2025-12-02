"""VideoProject model for Mini YouTube Studio video creation."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class VideoProject(Base):
    """VideoProject model for tracking video creation projects."""

    __tablename__ = "video_projects"

    # Primary key (UUID)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign key to Song
    song_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("songs.id"), nullable=False, index=True
    )

    # Cover art settings
    cover_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # template, ai, upload
    cover_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_prompt: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # For AI generation

    # Video settings
    video_style: Mapped[str] = mapped_column(
        String(20), default="lyric"
    )  # lyric, waveform, static, text_overlay
    lyric_style: Mapped[str] = mapped_column(
        String(20), default="fade"
    )  # fade, karaoke, scroll
    background_color: Mapped[str] = mapped_column(String(20), default="#000000")
    text_color: Mapped[str] = mapped_column(String(20), default="#ffffff")
    highlight_color: Mapped[str] = mapped_column(String(20), default="#ffff00")

    # Metadata for YouTube
    custom_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    custom_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    custom_tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    privacy: Mapped[str] = mapped_column(
        String(20), default="private"
    )  # public, unlisted, private

    # Lyric timing (JSON with beat-synced timing data)
    lyric_timing_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Output files
    preview_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    output_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default="draft", index=True
    )  # draft, generating, preview_ready, rendering, complete, failed
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationship to Song
    song: Mapped["Song"] = relationship("Song", back_populates="video_projects")

    def __repr__(self) -> str:
        """String representation."""
        return f"<VideoProject(id={self.id}, song_id={self.song_id}, status={self.status})>"
