"""FastAPI main application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import (
    analytics,
    auth,
    evaluation,
    notifications,
    playlists,
    queue,
    songs,
    studio,
    system,
    templates,
    youtube,
)
from app.config import get_settings
from app.database import init_db
from app.middleware.security import SecurityHeadersMiddleware
from app.services.backup import schedule_backups
from app.services.init_admin import create_admin_user
from app.services.worker import get_worker_pool

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Song Automation API...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Create admin user if not exists
    await create_admin_user()

    # Schedule backups
    schedule_backups()

    # Start background workers (evaluate, youtube_upload tasks only)
    # Note: file watcher and suno tasks are handled by external tools
    worker_pool = get_worker_pool()
    await worker_pool.start()
    logger.info("Background workers started")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Song Automation API...")

    # Stop background workers
    await worker_pool.stop()
    logger.info("Background workers stopped")


app = FastAPI(
    title="Song Automation API",
    description="AI-powered song generation and publishing platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Song Automation API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Register routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(songs.router, prefix="/api/v1", tags=["Songs"])
app.include_router(queue.router, prefix="/api/v1", tags=["Queue"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["Evaluation"])
app.include_router(youtube.router, prefix="/api/v1", tags=["YouTube"])
app.include_router(studio.router, prefix="/api/v1", tags=["Studio"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(templates.router, prefix="/api/v1", tags=["Style Templates"])
app.include_router(playlists.router, prefix="/api/v1", tags=["Playlists"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(system.router, prefix="/api/v1", tags=["System"])

# Mount static files for covers
covers_path = Path(settings.COVER_ART_PATH)
covers_path.mkdir(parents=True, exist_ok=True)
app.mount("/api/v1/covers", StaticFiles(directory=str(covers_path)), name="covers")

logger.info("Routes registered successfully")
