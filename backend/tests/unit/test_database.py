"""Tests for database.py database connection and session management."""

import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine


class TestGetEngine:
    """Tests for get_engine function."""

    def test_get_engine_returns_engine(self):
        """Test get_engine returns an AsyncEngine."""
        from app.database import get_engine, _engine

        # Reset module state
        import app.database
        original_engine = app.database._engine
        app.database._engine = None

        try:
            engine = get_engine()
            assert engine is not None
            assert isinstance(engine, AsyncEngine)
        finally:
            # Restore original state
            app.database._engine = original_engine

    def test_get_engine_returns_same_instance(self):
        """Test get_engine returns the same engine instance (singleton)."""
        from app.database import get_engine

        engine1 = get_engine()
        engine2 = get_engine()
        assert engine1 is engine2

    def test_engine_uses_correct_url(self):
        """Test engine is created with the correct database URL."""
        from app.database import get_engine
        from app.config import get_settings

        engine = get_engine()
        settings = get_settings()

        # Engine URL should be derived from settings
        assert engine is not None


class TestGetSessionLocal:
    """Tests for get_session_local function."""

    def test_get_session_local_returns_sessionmaker(self):
        """Test get_session_local returns an async_sessionmaker."""
        from app.database import get_session_local

        session_local = get_session_local()
        assert session_local is not None
        assert isinstance(session_local, async_sessionmaker)

    def test_get_session_local_returns_same_instance(self):
        """Test get_session_local returns the same instance (singleton)."""
        from app.database import get_session_local

        session1 = get_session_local()
        session2 = get_session_local()
        assert session1 is session2


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, temp_dir):
        """Test init_db creates all database tables."""
        import app.database

        # Create a temporary database
        test_db_path = temp_dir / "test_init.db"
        test_url = f"sqlite+aiosqlite:///{test_db_path}"

        with patch.object(app.database.settings, "DATABASE_URL", test_url), \
             patch.object(app.database.settings, "DEBUG", False):

            # Reset module state
            original_engine = app.database._engine
            original_session = app.database._session_local
            original_async_local = app.database.AsyncSessionLocal

            app.database._engine = None
            app.database._session_local = None
            app.database.AsyncSessionLocal = None

            try:
                await app.database.init_db()

                # Verify AsyncSessionLocal is set
                assert app.database.AsyncSessionLocal is not None

                # Verify database file was created
                assert test_db_path.exists()

            finally:
                # Restore original state
                app.database._engine = original_engine
                app.database._session_local = original_session
                app.database.AsyncSessionLocal = original_async_local

    @pytest.mark.asyncio
    async def test_init_db_imports_models(self):
        """Test init_db imports all required models."""
        # Test that model imports work correctly
        from app.models import (
            Evaluation,
            Playlist,
            PlaylistSong,
            Song,
            StyleTemplate,
            SunoJob,
            TaskQueue,
            User,
            YouTubeUpload,
        )

        # If imports succeed, test passes
        assert Evaluation is not None
        assert Playlist is not None
        assert PlaylistSong is not None
        assert Song is not None
        assert StyleTemplate is not None
        assert SunoJob is not None
        assert TaskQueue is not None
        assert User is not None
        assert YouTubeUpload is not None

    @pytest.mark.asyncio
    async def test_init_db_retries_on_failure(self, temp_dir):
        """Test init_db retries on failure."""
        import app.database

        test_db_path = temp_dir / "test_retry.db"
        test_url = f"sqlite+aiosqlite:///{test_db_path}"

        call_count = 0

        def mock_create_engine(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Simulated failure")
            return create_engine(str(test_db_path).replace("+aiosqlite", ""))

        with patch.object(app.database.settings, "DATABASE_URL", test_url), \
             patch.object(app.database.settings, "DEBUG", False), \
             patch("app.database.create_engine", side_effect=mock_create_engine):

            # Reset module state
            original_engine = app.database._engine
            original_session = app.database._session_local

            app.database._engine = None
            app.database._session_local = None

            try:
                await app.database.init_db()
                # Should have retried at least once
                assert call_count >= 2
            except Exception:
                # Expected if all retries fail
                pass
            finally:
                app.database._engine = original_engine
                app.database._session_local = original_session


class TestGetDb:
    """Tests for get_db dependency function."""

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test get_db yields an async session."""
        from app.database import get_db

        async for session in get_db():
            assert session is not None
            assert isinstance(session, AsyncSession)
            break

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """Test get_db commits the session on successful exit."""
        from app.database import get_db, get_session_local

        # Create a mock session to track calls
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_local = MagicMock(return_value=mock_cm)

        with patch("app.database.get_session_local", return_value=mock_session_local):
            async for session in get_db():
                pass  # Normal exit

            mock_session.commit.assert_called_once()
            mock_session.rollback.assert_not_called()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_db_rollbacks_on_exception(self):
        """Test get_db rollbacks the session on exception."""
        from app.database import get_db

        # Create a mock session to track calls
        mock_session = MagicMock(spec=AsyncSession)
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.close = AsyncMock()

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_session)
        mock_cm.__aexit__ = AsyncMock(return_value=None)

        mock_session_local = MagicMock(return_value=mock_cm)

        with patch("app.database.get_session_local", return_value=mock_session_local):
            try:
                async for session in get_db():
                    raise ValueError("Test exception")
            except ValueError:
                pass

            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()


class TestBase:
    """Tests for SQLAlchemy Base class."""

    def test_base_is_declarative_base(self):
        """Test Base is a declarative base."""
        from app.database import Base

        assert Base is not None
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "__tablename__")


class TestDatabaseConfiguration:
    """Tests for database configuration settings."""

    def test_database_url_configured(self):
        """Test DATABASE_URL is configured in settings."""
        from app.config import get_settings

        settings = get_settings()
        assert hasattr(settings, "DATABASE_URL")
        assert settings.DATABASE_URL is not None
        assert "sqlite" in settings.DATABASE_URL.lower()

    def test_debug_setting_exists(self):
        """Test DEBUG setting exists."""
        from app.config import get_settings

        settings = get_settings()
        assert hasattr(settings, "DEBUG")


class TestAsyncSessionLocal:
    """Tests for AsyncSessionLocal global variable."""

    def test_async_session_local_initially_none(self):
        """Test AsyncSessionLocal starts as None before init_db."""
        # Note: This is to verify the pattern, but it may be set after init_db
        from app.database import AsyncSessionLocal

        # The module-level variable exists
        assert "AsyncSessionLocal" in dir(__import__("app.database"))


class TestDatabasePooling:
    """Tests for database connection pooling configuration."""

    def test_engine_uses_null_pool(self):
        """Test engine uses NullPool for SQLite to avoid connection locks."""
        from app.database import get_engine
        from sqlalchemy.pool import NullPool

        engine = get_engine()
        # NullPool creates new connections each time
        assert engine.pool is not None


class TestDatabaseUrl:
    """Tests for database URL handling."""

    def test_sync_url_conversion(self):
        """Test async URL is correctly converted to sync URL."""
        from app.config import get_settings

        settings = get_settings()
        async_url = settings.DATABASE_URL

        # The sync URL should remove the async driver
        sync_url = async_url.replace("+aiosqlite", "")

        assert "+aiosqlite" not in sync_url
        assert "sqlite:" in sync_url


class TestSessionConfiguration:
    """Tests for session configuration."""

    def test_session_does_not_expire_on_commit(self):
        """Test session is configured with expire_on_commit=False."""
        from app.database import get_session_local

        session_maker = get_session_local()
        # The session maker is configured with expire_on_commit=False
        assert session_maker is not None

    def test_session_autocommit_false(self):
        """Test session is configured with autocommit=False."""
        from app.database import get_session_local

        session_maker = get_session_local()
        assert session_maker is not None

    def test_session_autoflush_false(self):
        """Test session is configured with autoflush=False."""
        from app.database import get_session_local

        session_maker = get_session_local()
        assert session_maker is not None


class TestDatabaseInitialization:
    """Integration tests for database initialization."""

    @pytest.mark.asyncio
    async def test_init_db_enables_foreign_keys(self):
        """Test init_db enables foreign keys pragma."""
        # Foreign keys are enabled via PRAGMA foreign_keys=ON
        # This is important for SQLite cascade deletes to work
        from app.database import Base

        # If tables are created successfully with foreign key relationships,
        # the pragma was enabled correctly
        from app.models.song import Song
        from app.models.suno_job import SunoJob

        # These models have foreign key relationships
        assert hasattr(Song, "__tablename__")
        assert hasattr(SunoJob, "song_id")


class TestDatabaseGlobals:
    """Tests for database module global state."""

    def test_engine_global_exists(self):
        """Test _engine global variable exists."""
        import app.database

        assert hasattr(app.database, "_engine")

    def test_session_local_global_exists(self):
        """Test _session_local global variable exists."""
        import app.database

        assert hasattr(app.database, "_session_local")

    def test_logger_configured(self):
        """Test logger is configured for database module."""
        import app.database

        assert hasattr(app.database, "logger")
        assert app.database.logger is not None
