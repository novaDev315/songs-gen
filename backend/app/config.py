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

    # Suno (session-based authentication via saved browser session)
    SUNO_SESSION_FILE: str = "./data/suno_session.json"  # Saved browser session
    SUNO_EMAIL: str = ""  # Deprecated: Only for fallback email/password login
    SUNO_PASSWORD: str = ""  # Deprecated: Only for fallback email/password login

    # YouTube (Phase 5)
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REDIRECT_URI: str = "http://localhost:8501/oauth/callback"
    YOUTUBE_DEFAULT_PRIVACY: str = "public"  # public, unlisted, private

    # OpenRouter for AI cover generation
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "stabilityai/stable-diffusion-xl"  # Default model for image gen
    OPENROUTER_SITE_URL: str = "https://songflow.app"  # For HTTP-Referer header

    # Cover art storage
    COVER_ART_PATH: str = "./data/covers"
    COVER_TEMPLATES_PATH: str = "./data/templates/covers"

    # Video generation
    VIDEO_PREVIEW_DURATION: int = 30  # Seconds for preview video
    VIDEO_CACHE_PATH: str = "./data/cache/videos"
    VIDEO_OUTPUT_PATH: str = "./data/videos"

    # Workers
    WORKER_COUNT: int = 2  # Number of background workers
    WORKER_CHECK_INTERVAL: int = 60  # Seconds between task checks
    WORKER_MAX_RETRIES: int = 3
    AUTO_UPLOAD_TO_SUNO: bool = False  # Auto-queue new songs for Suno upload

    # Evaluation
    MIN_QUALITY_SCORE: float = 70.0  # Auto-approve threshold for quality score

    # Notifications (Discord/Slack webhooks)
    DISCORD_WEBHOOK_URL: str = ""  # Discord webhook URL for notifications
    SLACK_WEBHOOK_URL: str = ""  # Slack webhook URL for notifications
    NOTIFICATIONS_ENABLED: bool = True  # Enable/disable all notifications
    NOTIFY_ON_SONG_COMPLETE: bool = True  # Notify when song generation completes
    NOTIFY_ON_SONG_FAILED: bool = True  # Notify when song generation fails
    NOTIFY_ON_YOUTUBE_UPLOAD: bool = True  # Notify when YouTube upload completes
    NOTIFY_ON_EVALUATION: bool = False  # Notify when evaluation completes

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme"  # Will be hashed on first run

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:8501", "http://localhost:3000"]

    # Backup settings
    BACKUP_PATH: str = "./data/backups"
    ENABLE_BACKUPS: bool = True
    BACKUP_GENERATED_FILES: bool = False  # Set true for full backups

    # Generated files path
    GENERATED_PATH: str = "./generated"
    GENERATED_SONGS_PATH: str = "./generated/songs"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
