"""Song model for tracking song metadata and status."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.playlist import PlaylistSong
    from app.models.suno_job import SunoJob
    from app.models.task_queue import TaskQueue
    from app.models.video_project import VideoProject
    from app.models.youtube_upload import YouTubeUpload


class Song(Base):
    """Song model for tracking song metadata and pipeline status."""

    __tablename__ = "songs"

    # Primary key (matches filename)
    id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    style_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    lyrics: Mapped[str] = mapped_column(Text, nullable=False)

    # File path to original .md file
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Audio file path (after download from Suno)
    audio_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )
    # Status values: pending, uploading, generating, downloaded, evaluated, uploaded, failed

    # Additional metadata (JSON string)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    suno_jobs: Mapped[list["SunoJob"]] = relationship(
        "SunoJob", back_populates="song", cascade="all, delete-orphan"
    )
    evaluations: Mapped[list["Evaluation"]] = relationship(
        "Evaluation", back_populates="song", cascade="all, delete-orphan"
    )
    youtube_uploads: Mapped[list["YouTubeUpload"]] = relationship(
        "YouTubeUpload", back_populates="song", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["TaskQueue"]] = relationship(
        "TaskQueue", back_populates="song", cascade="all, delete-orphan"
    )
    playlist_songs: Mapped[list["PlaylistSong"]] = relationship(
        "PlaylistSong", back_populates="song", cascade="all, delete-orphan"
    )
    video_projects: Mapped[list["VideoProject"]] = relationship(
        "VideoProject", back_populates="song", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Song(id={self.id}, title={self.title}, status={self.status})>"
