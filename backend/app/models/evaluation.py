"""Evaluation model for tracking song quality evaluations."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.song import Song
    from app.models.user import User


class Evaluation(Base):
    """Evaluation model for song quality assessments."""

    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Foreign key to song
    song_id: Mapped[str] = mapped_column(
        String(255), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Evaluation data
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5 stars
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evaluator tracking
    evaluated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    song: Mapped["Song"] = relationship("Song", back_populates="evaluations")
    evaluator: Mapped["User"] = relationship(
        "User", back_populates="evaluations", foreign_keys=[evaluated_by]
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Evaluation(id={self.id}, song_id={self.song_id}, approved={self.approved})>"
