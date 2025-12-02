"""Tests for database models and relationships."""

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.task_queue import TaskQueue
from app.models.user import User
from app.models.youtube_upload import YouTubeUpload


def test_database_tables_exist(test_db: Session):
    """Test that all required tables exist."""
    inspector = inspect(test_db.get_bind())
    tables = inspector.get_table_names()

    required_tables = [
        "users",
        "songs",
        "suno_jobs",
        "evaluations",
        "youtube_uploads",
        "task_queue",
    ]

    for table in required_tables:
        assert table in tables, f"Table '{table}' not found in database"


def test_create_user(test_db: Session):
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


def test_create_song(test_db: Session):
    """Test creating a song."""
    song = Song(
        id="test-song-001",
        title="Test Song",
        genre="pop",
        style_prompt="upbeat pop song",
        lyrics="Test lyrics here",
        file_path="/path/to/song.md",
        status="pending",
    )

    test_db.add(song)
    test_db.commit()
    test_db.refresh(song)

    assert song.id == "test-song-001"
    assert song.title == "Test Song"
    assert song.status == "pending"
    assert song.created_at is not None


def test_song_suno_job_relationship(test_db: Session):
    """Test relationship between Song and SunoJob."""
    # Create song
    song = Song(
        id="test-song-002",
        title="Test Song 2",
        genre="rock",
        style_prompt="rock song",
        lyrics="Rock lyrics",
        file_path="/path/to/song2.md",
    )
    test_db.add(song)
    test_db.commit()

    # Create suno job
    suno_job = SunoJob(
        song_id=song.id,
        suno_job_id="suno-123",
        status="pending",
    )
    test_db.add(suno_job)
    test_db.commit()
    test_db.refresh(song)

    assert len(song.suno_jobs) == 1
    assert song.suno_jobs[0].suno_job_id == "suno-123"
    assert song.suno_jobs[0].song == song


def test_song_evaluation_relationship(test_db: Session):
    """Test relationship between Song, Evaluation, and User."""
    # Create user
    user = User(
        username="evaluator",
        password_hash="hashed_password",
        role="admin",
    )
    test_db.add(user)
    test_db.commit()

    # Create song
    song = Song(
        id="test-song-003",
        title="Test Song 3",
        genre="jazz",
        style_prompt="smooth jazz",
        lyrics="Jazz lyrics",
        file_path="/path/to/song3.md",
    )
    test_db.add(song)
    test_db.commit()

    # Create evaluation
    evaluation = Evaluation(
        song_id=song.id,
        audio_quality_score=8.5,
        manual_rating=9,
        approved=True,
        evaluated_by=user.id,
    )
    test_db.add(evaluation)
    test_db.commit()
    test_db.refresh(song)
    test_db.refresh(user)

    assert len(song.evaluations) == 1
    assert song.evaluations[0].approved is True
    assert song.evaluations[0].evaluator == user
    assert len(user.evaluations) == 1


def test_song_youtube_upload_relationship(test_db: Session):
    """Test relationship between Song, YouTubeUpload, and User."""
    # Create user
    user = User(
        username="uploader",
        password_hash="hashed_password",
        role="admin",
    )
    test_db.add(user)
    test_db.commit()

    # Create song
    song = Song(
        id="test-song-004",
        title="Test Song 4",
        genre="edm",
        style_prompt="electronic dance music",
        lyrics="EDM lyrics",
        file_path="/path/to/song4.md",
    )
    test_db.add(song)
    test_db.commit()

    # Create YouTube upload
    upload = YouTubeUpload(
        song_id=song.id,
        video_id="youtube-123",
        video_url="https://youtube.com/watch?v=youtube-123",
        upload_status="published",
        title="Test Song 4",
        privacy="public",
        uploaded_by=user.id,
    )
    test_db.add(upload)
    test_db.commit()
    test_db.refresh(song)
    test_db.refresh(user)

    assert len(song.youtube_uploads) == 1
    assert song.youtube_uploads[0].video_id == "youtube-123"
    assert song.youtube_uploads[0].uploader == user
    assert len(user.youtube_uploads) == 1


def test_task_queue_creation(test_db: Session):
    """Test creating a task in the task queue."""
    # Create song
    song = Song(
        id="test-song-005",
        title="Test Song 5",
        genre="hip-hop",
        style_prompt="hip-hop beat",
        lyrics="Hip-hop lyrics",
        file_path="/path/to/song5.md",
    )
    test_db.add(song)
    test_db.commit()

    # Create task
    task = TaskQueue(
        task_type="suno_upload",
        song_id=song.id,
        payload='{"prompt": "test"}',
        status="pending",
        priority=1,
    )
    test_db.add(task)
    test_db.commit()
    test_db.refresh(task)
    test_db.refresh(song)

    assert task.id is not None
    assert task.task_type == "suno_upload"
    assert task.status == "pending"
    assert task.priority == 1
    assert len(song.tasks) == 1
    assert song.tasks[0] == task


def test_task_queue_index(test_db: Session):
    """Test that composite index exists on task_queue table."""
    inspector = inspect(test_db.get_bind())
    indexes = inspector.get_indexes("task_queue")

    # Check if composite index exists
    index_names = [idx["name"] for idx in indexes]
    assert "idx_task_queue_status_priority_created" in index_names


def test_cascade_delete_song(test_db: Session):
    """Test that deleting a song cascades to related records."""
    # Create song
    song = Song(
        id="test-song-006",
        title="Test Song 6",
        genre="country",
        style_prompt="country music",
        lyrics="Country lyrics",
        file_path="/path/to/song6.md",
    )
    test_db.add(song)
    test_db.commit()

    # Create related records
    suno_job = SunoJob(song_id=song.id, status="pending")
    task = TaskQueue(task_type="suno_upload", song_id=song.id, status="pending")

    test_db.add(suno_job)
    test_db.add(task)
    test_db.commit()

    # Verify related records exist
    assert test_db.query(SunoJob).filter_by(song_id=song.id).count() == 1
    assert test_db.query(TaskQueue).filter_by(song_id=song.id).count() == 1

    # Delete song
    test_db.delete(song)
    test_db.commit()

    # Verify related records were deleted
    assert test_db.query(SunoJob).filter_by(song_id="test-song-006").count() == 0
    assert test_db.query(TaskQueue).filter_by(song_id="test-song-006").count() == 0
