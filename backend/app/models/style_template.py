"""StyleTemplate model for reusable song generation templates."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class StyleTemplate(Base):
    """StyleTemplate model for storing reusable style prompts and configurations."""

    __tablename__ = "style_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Template identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Style configuration
    style_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    sub_genre: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Mood and energy
    mood: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # happy, sad, energetic, calm
    energy: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # low, medium, high

    # Searchable tags (comma-separated)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Visibility and featuring
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Creator tracking
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    created_by: Mapped[Optional["User"]] = relationship(
        "User", back_populates="style_templates", foreign_keys=[created_by_id]
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<StyleTemplate(id={self.id}, name='{self.name}', genre='{self.genre}')>"

    def increment_usage(self) -> None:
        """Increment usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()

    @property
    def tags_list(self) -> list[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]

    @tags_list.setter
    def tags_list(self, value: list[str]) -> None:
        """Set tags from a list."""
        self.tags = ",".join(value) if value else None
