"""Pytest configuration and fixtures."""

import asyncio
import json
import os
import tempfile
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator, AsyncIterator, Callable, Generator
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.auth import create_access_token, create_refresh_token, hash_password
from app.database import Base, get_db  # Note: app.main is not imported directly to avoid lifespan issues
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.youtube_upload import YouTubeUpload

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
TEST_DATABASE_URL_SYNC = "sqlite:///./test.db"


# =============================================================================
# Test Application Factory
# =============================================================================

def create_test_app() -> FastAPI:
    """Create a test version of the FastAPI app without lifespan services.

    This creates a fresh app instance for each test to avoid state leakage.
    The app has a minimal lifespan that doesn't start background workers,
    file watchers, or backup schedulers. Rate limiting is disabled for tests.
    """
    from fastapi.middleware.cors import CORSMiddleware
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from app.api import analytics, auth, evaluation, notifications, playlists, queue, songs, system, templates, youtube
    from app.middleware.security import SecurityHeadersMiddleware

    @asynccontextmanager
    async def test_lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Minimal test lifespan - no background services."""
        yield

    test_app = FastAPI(
        title="Song Automation API (Test)",
        version="1.0.0",
        description="Backend API for song generation automation pipeline",
        lifespan=test_lifespan,
    )

    # Disable rate limiting for tests by using a very high limit
    limiter = Limiter(key_func=get_remote_address, enabled=False)
    test_app.state.limiter = limiter

    # Security headers middleware
    test_app.add_middleware(SecurityHeadersMiddleware)

    # CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @test_app.get("/health")
    async def health_check() -> dict:
        return {"status": "healthy", "version": "1.0.0", "environment": "test"}

    # Include routers
    test_app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
    test_app.include_router(songs.router, prefix="/api/v1", tags=["Songs"])
    test_app.include_router(queue.router, prefix="/api/v1", tags=["Queue"])
    test_app.include_router(evaluation.router, prefix="/api/v1", tags=["Evaluation"])
    test_app.include_router(youtube.router, prefix="/api/v1", tags=["YouTube"])
    test_app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
    test_app.include_router(templates.router, prefix="/api/v1", tags=["Style Templates"])
    test_app.include_router(playlists.router, prefix="/api/v1", tags=["Playlists"])
    test_app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    test_app.include_router(system.router, prefix="/api/v1", tags=["System"])

    return test_app


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(TEST_DATABASE_URL_SYNC, connect_args={"check_same_thread": False})

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Drop all tables after test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
async def async_test_engine():
    """Create an async test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture(scope="function")
async def async_test_db(async_test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async test database session."""
    AsyncTestingSessionLocal = async_sessionmaker(
        async_test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def client(test_engine) -> Generator[TestClient, None, None]:
    """Create a test client with database override.

    Uses async session to match the application's async API endpoints.
    The test_engine creates tables synchronously, then we use an async
    engine pointing to the same database file for the API requests.

    Creates a fresh test app for each test to ensure isolation.
    """
    # Create a fresh test app for this test
    test_app = create_test_app()

    # Create async engine pointing to same test database file
    async_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    AsyncTestingSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async def override_get_db():
        """Override get_db with async session for API compatibility."""
        async with AsyncTestingSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()

    # Dispose the async engine synchronously
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(async_engine.dispose())
        else:
            loop.run_until_complete(async_engine.dispose())
    except RuntimeError:
        asyncio.run(async_engine.dispose())


# =============================================================================
# Authentication Fixtures
# =============================================================================


@pytest.fixture
def test_user(test_db: Session) -> User:
    """Create a test user attached to test_db session.

    The user remains attached to test_db so tests can call test_db.refresh(test_user).
    """
    user = User(
        username="testuser",
        password_hash=hash_password("testpassword123"),
        role="user",
        created_at=datetime.utcnow(),
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db: Session) -> User:
    """Create a test admin user attached to test_db session.

    The user remains attached to test_db so tests can call test_db.refresh(test_admin).
    """
    admin = User(
        username="admin",
        password_hash=hash_password("adminpassword123"),
        role="admin",
        created_at=datetime.utcnow(),
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers with valid access token."""
    access_token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(test_admin: User) -> dict:
    """Create authentication headers with admin access token."""
    access_token = create_access_token(data={"sub": test_admin.username})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def expired_token() -> str:
    """Create an expired access token."""
    # Create token that expired 1 hour ago
    from jose import jwt
    from app.config import get_settings

    settings = get_settings()
    payload = {
        "sub": "testuser",
        "exp": datetime.utcnow() - timedelta(hours=1),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


# =============================================================================
# Model Factory Fixtures
# =============================================================================


@pytest.fixture
def song_factory(test_db: Session) -> Callable:
    """Factory for creating test songs attached to test_db session."""

    def create_song(
        song_id: str = "test-song-001",
        title: str = "Test Song",
        genre: str = "Pop",
        status: str = "pending",
        **kwargs,
    ) -> Song:
        song = Song(
            id=song_id,
            title=title,
            genre=genre,
            style_prompt=kwargs.get(
                "style_prompt",
                "Pop song with upbeat energy, catchy hooks, modern production",
            ),
            lyrics=kwargs.get("lyrics", "[Verse 1]\nTest lyrics\n\n[Chorus]\nTest chorus"),
            file_path=kwargs.get("file_path", f"/generated/songs/{song_id}.md"),
            status=status,
            metadata_json=kwargs.get("metadata_json"),
            created_at=kwargs.get("created_at", datetime.utcnow()),
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)
        return song

    return create_song


@pytest.fixture
def suno_job_factory(test_db: Session) -> Callable:
    """Factory for creating test Suno jobs attached to test_db session."""

    def create_suno_job(
        song_id: str,
        status: str = "pending",
        **kwargs,
    ) -> SunoJob:
        job = SunoJob(
            song_id=song_id,
            status=status,
            suno_job_id=kwargs.get("suno_job_id"),
            audio_url=kwargs.get("audio_url"),
            downloaded_path=kwargs.get("downloaded_path"),
            error_message=kwargs.get("error_message"),
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)
        return job

    return create_suno_job


@pytest.fixture
def evaluation_factory(test_db: Session, test_user: User) -> Callable:
    """Factory for creating test evaluations attached to test_db session."""

    def create_evaluation(
        song_id: str,
        approved: bool = True,
        **kwargs,
    ) -> Evaluation:
        evaluation = Evaluation(
            song_id=song_id,
            evaluated_by=test_user.id,
            approved=approved,
            audio_quality_score=kwargs.get("audio_quality_score", 85.5),
            duration_seconds=kwargs.get("duration_seconds", 180.0),
            file_size_mb=kwargs.get("file_size_mb", 4.2),
            sample_rate=kwargs.get("sample_rate", 44100),
            bitrate=kwargs.get("bitrate", 192000),
            manual_rating=kwargs.get("manual_rating"),
            notes=kwargs.get("notes", "Test evaluation"),
        )
        test_db.add(evaluation)
        test_db.commit()
        test_db.refresh(evaluation)
        return evaluation

    return create_evaluation


@pytest.fixture
def youtube_upload_factory(test_db: Session, test_user: User) -> Callable:
    """Factory for creating test YouTube uploads attached to test_db session."""

    def create_youtube_upload(
        song_id: str,
        upload_status: str = "pending",
        **kwargs,
    ) -> YouTubeUpload:
        upload = YouTubeUpload(
            song_id=song_id,
            uploaded_by=test_user.id,
            upload_status=upload_status,
            title=kwargs.get("title", "Test Song Video"),
            description=kwargs.get("description"),
            tags=kwargs.get("tags"),
            privacy=kwargs.get("privacy", "private"),
            video_id=kwargs.get("video_id"),
            video_url=kwargs.get("video_url"),
            error_message=kwargs.get("error_message"),
        )
        test_db.add(upload)
        test_db.commit()
        test_db.refresh(upload)
        return upload

    return create_youtube_upload


@pytest.fixture
def task_factory(test_db: Session) -> Callable:
    """Factory for creating test tasks attached to test_db session."""

    def create_task(
        song_id: str,
        task_type: str = "generate",
        status: str = "pending",
        **kwargs,
    ) -> TaskQueue:
        task = TaskQueue(
            song_id=song_id,
            task_type=task_type,
            status=status,
            priority=kwargs.get("priority", 5),
            error_message=kwargs.get("error_message"),
            created_at=kwargs.get("created_at", datetime.utcnow()),
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)
        return task

    return create_task


# =============================================================================
# File System Fixtures
# =============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_audio_file(temp_dir: Path) -> Path:
    """Create a temporary audio file for testing."""
    audio_file = temp_dir / "test_audio.mp3"
    # Create a minimal MP3 file (just for path testing, not actual audio)
    audio_file.write_bytes(b"ID3" + b"\x00" * 100)
    return audio_file


@pytest.fixture
def temp_video_file(temp_dir: Path) -> Path:
    """Create a temporary video file for testing."""
    video_file = temp_dir / "test_video.mp4"
    # Create a minimal MP4 file (just for path testing)
    video_file.write_bytes(b"\x00\x00\x00\x20ftypisom" + b"\x00" * 100)
    return video_file


@pytest.fixture
def sample_song_file(temp_dir: Path) -> Path:
    """Create a sample song .md file for testing."""
    song_content = """# Test Song

## Style Prompt
Pop song, upbeat, catchy hooks, 120 BPM, modern production

## Lyrics
[Verse 1]
This is a test song
Testing all day long

[Chorus]
TEST TEST TEST
This is just a test

[Outro]
*fade out*
"""
    song_file = temp_dir / "test-song-001.md"
    song_file.write_text(song_content)

    # Create metadata file
    metadata = {
        "id": "test-song-001",
        "title": "Test Song",
        "genre": "Pop",
        "created_at": datetime.utcnow().isoformat(),
    }
    meta_file = temp_dir / "test-song-001.meta.json"
    meta_file.write_text(json.dumps(metadata, indent=2))

    return song_file


# =============================================================================
# Mock Service Fixtures
# =============================================================================


@pytest.fixture
def mock_suno_client():
    """Mock Suno client for testing."""
    mock = MagicMock()
    mock.upload_song = AsyncMock(
        return_value={
            "song_id": "suno-123",
            "url": "https://suno.com/song/suno-123",
        }
    )
    mock.check_status = AsyncMock(
        return_value={
            "status": "completed",
            "audio_url": "https://cdn.suno.com/audio/suno-123.mp3",
        }
    )
    mock.download_audio = AsyncMock(return_value="/downloads/suno-123.mp3")
    return mock


@pytest.fixture
def mock_youtube_client():
    """Mock YouTube client for testing."""
    mock = MagicMock()
    mock.upload_video = AsyncMock(
        return_value={
            "video_id": "yt-123",
            "url": "https://youtube.com/watch?v=yt-123",
        }
    )
    mock.update_metadata = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_audio_analyzer():
    """Mock audio analyzer for testing."""
    mock = MagicMock()
    mock.analyze_audio = Mock(
        return_value={
            "duration_seconds": 180.5,
            "file_size_mb": 4.2,
            "sample_rate": 44100,
            "bitrate": 192000,
            "channels": 2,
            "rms_energy": 0.25,
            "spectral_centroid": 2500.0,
            "zero_crossing_rate": 0.15,
            "tempo": 120.0,
            "audio_quality_score": 85.5,
        }
    )
    return mock


@pytest.fixture
def mock_video_generator():
    """Mock video generator for testing."""
    mock = MagicMock()
    mock.generate_video = Mock(return_value=Path("/videos/test.mp4"))
    mock.generate_video_with_text_overlay = Mock(return_value=Path("/videos/test_text.mp4"))
    return mock


@pytest.fixture
def mock_file_watcher():
    """Mock file watcher for testing."""
    mock = MagicMock()
    mock.start = Mock()
    mock.stop = Mock()
    mock.is_running = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_worker():
    """Mock background worker for testing."""
    mock = MagicMock()
    mock.start = Mock()
    mock.stop = Mock()
    mock.is_running = Mock(return_value=True)
    mock.queue_size = Mock(return_value=0)
    return mock


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def sample_song_data() -> dict:
    """Sample song data for testing."""
    return {
        "id": "test-song-001",
        "title": "Test Song",
        "genre": "Pop",
        "style_prompt": "Pop song with upbeat energy, catchy hooks, modern production",
        "lyrics": "[Verse 1]\nTest lyrics\n\n[Chorus]\nTest chorus",
        "file_path": "/generated/songs/test-song-001.md",
        "status": "pending",
    }


@pytest.fixture
def sample_evaluation_data() -> dict:
    """Sample evaluation data for testing."""
    return {
        "song_id": "test-song-001",
        "audio_quality_score": 85.5,
        "duration_seconds": 180.0,
        "file_size_mb": 4.2,
    }
