"""Unit tests for database models.

Tests model creation, relationships, and constraints.
"""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.evaluation import Evaluation
from app.models.youtube_upload import YouTubeUpload
from app.models.task_queue import TaskQueue


# =============================================================================
# User Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestUserModel:
    """Test User model functionality."""

    def test_create_user(self, test_db):
        """Test creating a user."""
        user = User(
            username="testuser",
            password_hash="hashed_password",
            role="user",
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.role == "user"
        assert user.created_at is not None

    def test_user_unique_username(self, test_db):
        """Test username uniqueness constraint."""
        user1 = User(username="testuser", password_hash="hash1", role="user")
        user2 = User(username="testuser", password_hash="hash2", role="user")

        test_db.add(user1)
        test_db.commit()

        test_db.add(user2)
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_user_default_role(self, test_db):
        """Test user has default role."""
        user = User(username="testuser", password_hash="hashed_password")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.role == "user"

    def test_user_repr(self, test_db):
        """Test user string representation."""
        user = User(username="testuser", password_hash="hash", role="admin")
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        repr_str = repr(user)
        assert "testuser" in repr_str
        assert "admin" in repr_str
        assert str(user.id) in repr_str

    def test_user_refresh_token_fields(self, test_db):
        """Test user refresh token management fields."""
        user = User(
            username="testuser",
            password_hash="hash",
            refresh_token_hash="refresh_hash",
            refresh_token_expires_at=datetime.utcnow(),
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.refresh_token_hash == "refresh_hash"
        assert user.refresh_token_expires_at is not None

    def test_user_last_login(self, test_db):
        """Test user last login tracking."""
        user = User(username="testuser", password_hash="hash")
        test_db.add(user)
        test_db.commit()

        assert user.last_login is None

        user.last_login = datetime.utcnow()
        test_db.commit()
        test_db.refresh(user)

        assert user.last_login is not None


# =============================================================================
# Song Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestSongModel:
    """Test Song model functionality."""

    def test_create_song(self, test_db):
        """Test creating a song."""
        song = Song(
            id="test-song-001",
            title="Test Song",
            genre="Pop",
            style_prompt="Pop song with catchy hooks",
            lyrics="[Verse 1]\nTest lyrics",
            file_path="/path/to/song.md",
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)

        assert song.id == "test-song-001"
        assert song.title == "Test Song"
        assert song.genre == "Pop"
        assert song.status == "pending"
        assert song.created_at is not None
        assert song.updated_at is not None

    def test_song_default_status(self, test_db):
        """Test song has default pending status."""
        song = Song(
            id="test-song",
            title="Test",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)

        assert song.status == "pending"

    def test_song_custom_status(self, test_db):
        """Test song with custom status."""
        song = Song(
            id="test-song",
            title="Test",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
            status="completed",
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)

        assert song.status == "completed"

    def test_song_metadata_json(self, test_db):
        """Test song with metadata JSON."""
        import json

        metadata = {"key": "value", "number": 42}
        song = Song(
            id="test-song",
            title="Test",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
            metadata_json=json.dumps(metadata),
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)

        assert song.metadata_json is not None
        parsed = json.loads(song.metadata_json)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42

    def test_song_repr(self, test_db):
        """Test song string representation."""
        song = Song(
            id="test-song-001",
            title="Test Song",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
            status="generating",
        )
        test_db.add(song)
        test_db.commit()

        repr_str = repr(song)
        assert "test-song-001" in repr_str
        assert "Test Song" in repr_str
        assert "generating" in repr_str

    @pytest.mark.parametrize(
        "genre", ["Pop", "Hip-Hop", "EDM", "Rock", "Country", "Jazz", "Electronic"]
    )
    def test_song_various_genres(self, test_db, genre):
        """Test songs with various genres."""
        song = Song(
            id=f"test-{genre.lower()}",
            title=f"{genre} Song",
            genre=genre,
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
        )
        test_db.add(song)
        test_db.commit()
        test_db.refresh(song)

        assert song.genre == genre


# =============================================================================
# SunoJob Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestSunoJobModel:
    """Test SunoJob model functionality."""

    def test_create_suno_job(self, test_db, song_factory):
        """Test creating a Suno job."""
        song = song_factory()

        job = SunoJob(
            id="suno-job-001",
            song_id=song.id,
            status="pending",
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        assert job.id == "suno-job-001"
        assert job.song_id == song.id
        assert job.status == "pending"
        assert job.created_at is not None

    def test_suno_job_relationship(self, test_db, song_factory):
        """Test Suno job relationship with song."""
        song = song_factory()

        job = SunoJob(
            id="suno-job-001",
            song_id=song.id,
            status="completed",
            suno_song_id="suno-123",
        )
        test_db.add(job)
        test_db.commit()

        # Test relationship
        test_db.refresh(song)
        assert len(song.suno_jobs) == 1
        assert song.suno_jobs[0].id == "suno-job-001"

    def test_suno_job_cascade_delete(self, test_db, song_factory):
        """Test Suno job is deleted when song is deleted."""
        song = song_factory()

        job = SunoJob(
            id="suno-job-001",
            song_id=song.id,
            status="completed",
        )
        test_db.add(job)
        test_db.commit()

        # Delete song
        test_db.delete(song)
        test_db.commit()

        # Job should be deleted
        deleted_job = test_db.query(SunoJob).filter_by(id="suno-job-001").first()
        assert deleted_job is None

    @pytest.mark.parametrize(
        "status", ["pending", "uploading", "generating", "completed", "failed"]
    )
    def test_suno_job_statuses(self, test_db, song_factory, status):
        """Test Suno job with various statuses."""
        song = song_factory()

        job = SunoJob(
            id=f"job-{status}",
            song_id=song.id,
            status=status,
        )
        test_db.add(job)
        test_db.commit()
        test_db.refresh(job)

        assert job.status == status


# =============================================================================
# Evaluation Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestEvaluationModel:
    """Test Evaluation model functionality."""

    def test_create_evaluation(self, test_db, song_factory, test_user):
        """Test creating an evaluation."""
        song = song_factory()

        evaluation = Evaluation(
            song_id=song.id,
            evaluated_by=test_user.id,
            is_approved=True,
            audio_quality_score=85.5,
            notes="Great quality",
        )
        test_db.add(evaluation)
        test_db.commit()
        test_db.refresh(evaluation)

        assert evaluation.song_id == song.id
        assert evaluation.evaluated_by == test_user.id
        assert evaluation.is_approved is True
        assert evaluation.audio_quality_score == 85.5

    def test_evaluation_relationships(self, test_db, song_factory, test_user):
        """Test evaluation relationships."""
        song = song_factory()

        evaluation = Evaluation(
            song_id=song.id,
            evaluated_by=test_user.id,
            is_approved=True,
        )
        test_db.add(evaluation)
        test_db.commit()

        # Test song relationship
        test_db.refresh(song)
        assert len(song.evaluations) == 1
        assert song.evaluations[0].song_id == song.id

        # Test evaluator relationship
        test_db.refresh(test_user)
        assert len(test_user.evaluations) == 1

    def test_evaluation_optional_fields(self, test_db, song_factory, test_user):
        """Test evaluation with optional fields."""
        song = song_factory()

        evaluation = Evaluation(
            song_id=song.id,
            evaluated_by=test_user.id,
            is_approved=False,
            manual_score=75,
            notes="Needs improvement",
        )
        test_db.add(evaluation)
        test_db.commit()
        test_db.refresh(evaluation)

        assert evaluation.manual_score == 75
        assert evaluation.notes == "Needs improvement"


# =============================================================================
# YouTubeUpload Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestYouTubeUploadModel:
    """Test YouTubeUpload model functionality."""

    def test_create_youtube_upload(self, test_db, song_factory, test_user):
        """Test creating a YouTube upload."""
        song = song_factory()

        upload = YouTubeUpload(
            song_id=song.id,
            uploaded_by=test_user.id,
            status="pending",
            video_file_path="/videos/test.mp4",
        )
        test_db.add(upload)
        test_db.commit()
        test_db.refresh(upload)

        assert upload.song_id == song.id
        assert upload.uploaded_by == test_user.id
        assert upload.status == "pending"

    def test_youtube_upload_completed(self, test_db, song_factory, test_user):
        """Test completed YouTube upload."""
        song = song_factory()

        upload = YouTubeUpload(
            song_id=song.id,
            uploaded_by=test_user.id,
            status="completed",
            youtube_video_id="yt-123",
            youtube_url="https://youtube.com/watch?v=yt-123",
        )
        test_db.add(upload)
        test_db.commit()
        test_db.refresh(upload)

        assert upload.youtube_video_id == "yt-123"
        assert upload.youtube_url == "https://youtube.com/watch?v=yt-123"

    def test_youtube_upload_relationships(self, test_db, song_factory, test_user):
        """Test YouTube upload relationships."""
        song = song_factory()

        upload = YouTubeUpload(
            song_id=song.id,
            uploaded_by=test_user.id,
            status="completed",
        )
        test_db.add(upload)
        test_db.commit()

        # Test song relationship
        test_db.refresh(song)
        assert len(song.youtube_uploads) == 1

        # Test uploader relationship
        test_db.refresh(test_user)
        assert len(test_user.youtube_uploads) == 1


# =============================================================================
# TaskQueue Model Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.database
class TestTaskQueueModel:
    """Test TaskQueue model functionality."""

    def test_create_task(self, test_db, song_factory):
        """Test creating a task."""
        song = song_factory()

        task = TaskQueue(
            song_id=song.id,
            task_type="generate",
            status="pending",
            priority=5,
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)

        assert task.song_id == song.id
        assert task.task_type == "generate"
        assert task.status == "pending"
        assert task.priority == 5

    def test_task_relationship(self, test_db, song_factory):
        """Test task relationship with song."""
        song = song_factory()

        task = TaskQueue(
            song_id=song.id,
            task_type="upload",
            status="pending",
        )
        test_db.add(task)
        test_db.commit()

        # Test relationship
        test_db.refresh(song)
        assert len(song.tasks) == 1
        assert song.tasks[0].task_type == "upload"

    @pytest.mark.parametrize(
        "task_type,priority",
        [
            ("generate", 10),
            ("download", 5),
            ("evaluate", 3),
            ("upload", 1),
        ],
    )
    def test_task_types_and_priorities(self, test_db, song_factory, task_type, priority):
        """Test tasks with various types and priorities."""
        song = song_factory()

        task = TaskQueue(
            song_id=song.id,
            task_type=task_type,
            status="pending",
            priority=priority,
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)

        assert task.task_type == task_type
        assert task.priority == priority

    def test_task_error_message(self, test_db, song_factory):
        """Test task with error message."""
        song = song_factory()

        task = TaskQueue(
            song_id=song.id,
            task_type="generate",
            status="failed",
            error_message="Connection timeout",
        )
        test_db.add(task)
        test_db.commit()
        test_db.refresh(task)

        assert task.status == "failed"
        assert task.error_message == "Connection timeout"
