"""User model for authentication and authorization."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.models.evaluation import Evaluation
    from app.models.style_template import StyleTemplate
    from app.models.youtube_upload import YouTubeUpload


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # User flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    evaluations: Mapped[list["Evaluation"]] = relationship(
        "Evaluation", back_populates="evaluator", foreign_keys="[Evaluation.evaluated_by]"
    )
    youtube_uploads: Mapped[list["YouTubeUpload"]] = relationship(
        "YouTubeUpload", back_populates="uploader", foreign_keys="[YouTubeUpload.uploaded_by]"
    )
    style_templates: Mapped[list["StyleTemplate"]] = relationship(
        "StyleTemplate", back_populates="created_by", foreign_keys="[StyleTemplate.created_by_id]"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, username={self.username}, is_admin={self.is_admin})>"
