"""FastAPI main application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, evaluation, queue, songs, system, youtube
from app.config import get_settings
from app.database import init_db
from app.services.backup import schedule_backups
from app.services.file_watcher import get_file_watcher
from app.services.init_admin import create_admin_user
from app.services.worker import get_worker_pool

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Song Automation API...")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Create admin user if not exists
    create_admin_user()

    # Schedule backups
    schedule_backups()

    # Start file watcher
    file_watcher = get_file_watcher()
    file_watcher.start()
    logger.info("File watcher started")

    # Start background workers
    worker_pool = get_worker_pool()
    await worker_pool.start()
    logger.info("Background workers started")

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Song Automation API...")

    # Stop file watcher
    file_watcher.stop()
    logger.info("File watcher stopped")

    # Stop background workers
    await worker_pool.stop()
    logger.info("Background workers stopped")


app = FastAPI(
    title="Song Automation API",
    version="1.0.0",
    description="Backend API for song generation automation pipeline",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit frontend
        "http://frontend:8501",  # Docker network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(songs.router, prefix="/api/v1", tags=["Songs"])
app.include_router(queue.router, prefix="/api/v1", tags=["Queue"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["Evaluation"])
app.include_router(youtube.router, prefix="/api/v1", tags=["YouTube"])
app.include_router(system.router, prefix="/api/v1", tags=["System"])

logger.info("Routes registered successfully")
