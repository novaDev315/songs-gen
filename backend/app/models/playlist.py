"""Playlist model for organizing songs into collections."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song


class Playlist(Base):
    """Playlist model for organizing songs."""

    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Creator (user_id)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Visibility
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Cover image
    cover_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    playlist_songs: Mapped[list["PlaylistSong"]] = relationship(
        "PlaylistSong", back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Playlist(id={self.id}, name={self.name})>"


class PlaylistSong(Base):
    """Association table for playlist-song relationship with ordering."""

    __tablename__ = "playlist_songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    playlist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    song_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Position in playlist (for ordering)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    playlist: Mapped["Playlist"] = relationship("Playlist", back_populates="playlist_songs")
    song: Mapped["Song"] = relationship("Song", back_populates="playlist_songs")

    def __repr__(self) -> str:
        """String representation."""
        return f"<PlaylistSong(playlist_id={self.playlist_id}, song_id={self.song_id}, position={self.position})>"
