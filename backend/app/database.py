"""Database connection and session management."""

import logging
from typing import AsyncGenerator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine for SQLite with WAL mode
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    echo=settings.DEBUG,
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def init_db() -> None:
    """Initialize database with all tables and enable WAL mode."""
    logger.info("Initializing database...")

    # Enable WAL mode and optimize SQLite settings
    async with engine.begin() as conn:
        # Enable WAL mode for better concurrency
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        # Set busy timeout to 5 seconds
        await conn.execute(text("PRAGMA busy_timeout=5000"))
        # Use NORMAL synchronous mode for better performance
        await conn.execute(text("PRAGMA synchronous=NORMAL"))
        # Enable foreign key constraints
        await conn.execute(text("PRAGMA foreign_keys=ON"))

        # Verify WAL mode is enabled
        result = await conn.execute(text("PRAGMA journal_mode"))
        mode = result.scalar()
        logger.info(f"SQLite journal mode: {mode}")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
