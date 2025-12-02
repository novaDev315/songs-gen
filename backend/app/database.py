"""Database connection and session management."""

import asyncio
import fcntl
import logging
from pathlib import Path
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool, StaticPool

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Base class for models - must be defined before model imports
Base = declarative_base()

# Lazy engine initialization to avoid SQLite locking issues
_engine: Optional[AsyncEngine] = None
_session_local: Optional[async_sessionmaker] = None
_db_initialized: bool = False


def get_engine() -> AsyncEngine:
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.DATABASE_URL,
            connect_args={
                "check_same_thread": False,
                "timeout": 30,  # SQLite busy timeout
            },
            echo=False,  # Disable SQL echo to reduce log noise
            future=True,
            poolclass=NullPool,  # Use NullPool for SQLite to avoid connection locks
        )
    return _engine


def get_session_local() -> async_sessionmaker:
    """Get or create the session factory."""
    global _session_local
    if _session_local is None:
        _session_local = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _session_local


# For backwards compatibility with direct imports
# AsyncSessionLocal will be set after init_db
AsyncSessionLocal = None


async def init_db() -> None:
    """Initialize database with all tables.

    Uses synchronous engine for table creation to avoid SQLite async locking issues.
    """
    global AsyncSessionLocal, _db_initialized

    # Skip if already initialized
    if _db_initialized:
        logger.info("Database already initialized, skipping")
        return

    logger.info("Initializing database...")

    # Import all models to ensure they're registered with Base.metadata
    # These imports must happen before create_all is called
    from app.models import (  # noqa: F401
        Evaluation,
        Playlist,
        PlaylistSong,
        Song,
        StyleTemplate,
        SunoJob,
        SunoVariation,
        TaskQueue,
        User,
        VideoProject,
        YouTubeUpload,
    )

    # Convert async URL to sync URL for table creation
    # sqlite+aiosqlite:///... -> sqlite:///...
    sync_url = settings.DATABASE_URL.replace("+aiosqlite", "")

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            # Use a fresh synchronous engine for table creation
            # This avoids async SQLite locking issues
            sync_engine = create_engine(
                sync_url,
                connect_args={"check_same_thread": False, "timeout": 30},
                echo=False,  # Disable SQL echo to reduce log noise
            )

            with sync_engine.begin() as conn:
                # Set journal mode to WAL for better concurrency
                conn.execute(text("PRAGMA journal_mode=WAL"))
                # Enable foreign keys
                conn.execute(text("PRAGMA foreign_keys=ON"))
                # Increase busy timeout
                conn.execute(text("PRAGMA busy_timeout=60000"))
                # Create all tables
                Base.metadata.create_all(bind=conn)

            # Dispose sync engine immediately after use
            sync_engine.dispose()

            # Now set up async session local for the rest of the application
            AsyncSessionLocal = get_session_local()

            # Mark as initialized
            _db_initialized = True

            logger.info("Database initialized successfully")
            return  # Success, exit the retry loop

        except Exception as e:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("Database initialization failed after all retries")
                raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    session_local = get_session_local()
    async with session_local() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
