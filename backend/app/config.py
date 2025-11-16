"""Application configuration settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:////app/data/songs.db"

    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15  # Short-lived access token
    JWT_REFRESH_EXPIRE_DAYS: int = 7  # Long-lived refresh token

    # File Paths
    WATCH_FOLDER: str = "./generated/songs"
    DOWNLOAD_FOLDER: str = "./downloads"
    DATA_FOLDER: str = "./data"

    # Suno (placeholders for Phase 3)
    SUNO_EMAIL: str = ""
    SUNO_PASSWORD: str = ""

    # YouTube (placeholders for Phase 5)
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REDIRECT_URI: str = "http://localhost:8501/oauth/callback"

    # Workers
    WORKER_COUNT: int = 2  # Number of background workers
    WORKER_CHECK_INTERVAL: int = 60  # Seconds between task checks
    WORKER_MAX_RETRIES: int = 3
    AUTO_UPLOAD_TO_SUNO: bool = False  # Auto-queue new songs for Suno upload

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"  # Will be hashed on first run

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
