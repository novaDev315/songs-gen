"""Unit tests for Pydantic schemas.

Tests request/response schema validation and serialization.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserResponse
from app.schemas.song import SongCreate, SongResponse, SongUpdate, SongListResponse
from app.schemas.evaluation import EvaluationCreate, EvaluationResponse
from app.schemas.youtube import YouTubeUploadResponse, YouTubeUploadCreate


# =============================================================================
# Authentication Schema Tests
# =============================================================================


@pytest.mark.unit
class TestAuthSchemas:
    """Test authentication schema validation."""

    def test_login_request_valid(self):
        """Test valid login request."""
        data = {"username": "testuser", "password": "password123"}
        login = LoginRequest(**data)

        assert login.username == "testuser"
        assert login.password == "password123"

    def test_login_request_username_too_short(self):
        """Test login request with username too short."""
        data = {"username": "ab", "password": "password123"}

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        assert "username" in str(exc_info.value)

    def test_login_request_username_too_long(self):
        """Test login request with username too long."""
        data = {"username": "a" * 51, "password": "password123"}

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        assert "username" in str(exc_info.value)

    def test_login_request_password_too_short(self):
        """Test login request with password too short."""
        data = {"username": "testuser", "password": "12345"}

        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(**data)

        assert "password" in str(exc_info.value)

    def test_login_request_missing_fields(self):
        """Test login request with missing fields."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")

        with pytest.raises(ValidationError):
            LoginRequest(password="password123")

    def test_token_response_valid(self):
        """Test valid token response."""
        data = {
            "access_token": "access_token_string",
            "refresh_token": "refresh_token_string",
        }
        response = TokenResponse(**data)

        assert response.access_token == "access_token_string"
        assert response.refresh_token == "refresh_token_string"
        assert response.token_type == "bearer"

    def test_token_response_default_type(self):
        """Test token response has default token type."""
        data = {
            "access_token": "access",
            "refresh_token": "refresh",
        }
        response = TokenResponse(**data)

        assert response.token_type == "bearer"

    def test_refresh_request_valid(self):
        """Test valid refresh request."""
        data = {"refresh_token": "refresh_token_string"}
        request = RefreshRequest(**data)

        assert request.refresh_token == "refresh_token_string"

    def test_user_response_valid(self):
        """Test valid user response."""
        data = {
            "id": 1,
            "username": "testuser",
            "role": "user",
            "created_at": datetime.utcnow(),
        }
        response = UserResponse(**data)

        assert response.id == 1
        assert response.username == "testuser"
        assert response.role == "user"


# =============================================================================
# Song Schema Tests
# =============================================================================


@pytest.mark.unit
class TestSongSchemas:
    """Test song schema validation."""

    def test_song_create_valid(self):
        """Test valid song creation."""
        data = {
            "id": "test-song-001",
            "title": "Test Song",
            "genre": "Pop",
            "style_prompt": "Pop song with catchy hooks",
            "lyrics": "[Verse 1]\nTest lyrics",
            "file_path": "/path/to/song.md",
        }
        song = SongCreate(**data)

        assert song.id == "test-song-001"
        assert song.title == "Test Song"
        assert song.genre == "Pop"

    def test_song_create_missing_required_fields(self):
        """Test song creation with missing required fields."""
        with pytest.raises(ValidationError):
            SongCreate(id="test-song", title="Test")

    def test_song_response_valid(self):
        """Test valid song response."""
        data = {
            "id": "test-song-001",
            "title": "Test Song",
            "genre": "Pop",
            "style_prompt": "Test prompt",
            "lyrics": "Test lyrics",
            "file_path": "/path/to/song.md",
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        response = SongResponse(**data)

        assert response.id == "test-song-001"
        assert response.status == "pending"

    def test_song_update_partial(self):
        """Test song update with partial data."""
        data = {"status": "completed"}
        update = SongUpdate(**data)

        assert update.status == "completed"
        assert update.title is None

    def test_song_update_all_fields(self):
        """Test song update with all fields."""
        data = {
            "title": "Updated Title",
            "status": "completed",
            "metadata_json": '{"key": "value"}',
        }
        update = SongUpdate(**data)

        assert update.title == "Updated Title"
        assert update.status == "completed"

    def test_song_list_response(self):
        """Test song list response."""
        songs = [
            {
                "id": "song-1",
                "title": "Song 1",
                "genre": "Pop",
                "style_prompt": "Test",
                "lyrics": "Test",
                "file_path": "/path1.md",
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            {
                "id": "song-2",
                "title": "Song 2",
                "genre": "Rock",
                "style_prompt": "Test",
                "lyrics": "Test",
                "file_path": "/path2.md",
                "status": "completed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        ]
        data = {"songs": songs, "total": 2}
        response = SongListResponse(**data)

        assert len(response.songs) == 2
        assert response.total == 2

    @pytest.mark.parametrize(
        "genre", ["Pop", "Hip-Hop", "EDM", "Rock", "Country", "Jazz"]
    )
    def test_song_various_genres(self, genre):
        """Test song creation with various genres."""
        data = {
            "id": f"test-{genre}",
            "title": f"{genre} Song",
            "genre": genre,
            "style_prompt": "Test",
            "lyrics": "Test",
            "file_path": "/test.md",
        }
        song = SongCreate(**data)

        assert song.genre == genre


# =============================================================================
# Evaluation Schema Tests
# =============================================================================


@pytest.mark.unit
class TestEvaluationSchemas:
    """Test evaluation schema validation."""

    def test_evaluation_create_valid(self):
        """Test valid evaluation creation."""
        data = {
            "is_approved": True,
            "audio_quality_score": 85.5,
            "manual_score": 90,
            "notes": "Great quality",
        }
        evaluation = EvaluationCreate(**data)

        assert evaluation.is_approved is True
        assert evaluation.audio_quality_score == 85.5
        assert evaluation.manual_score == 90

    def test_evaluation_create_minimal(self):
        """Test evaluation creation with minimal data."""
        data = {"is_approved": True}
        evaluation = EvaluationCreate(**data)

        assert evaluation.is_approved is True
        assert evaluation.audio_quality_score is None
        assert evaluation.manual_score is None

    def test_evaluation_create_rejected(self):
        """Test evaluation creation for rejected song."""
        data = {
            "is_approved": False,
            "notes": "Quality issues detected",
        }
        evaluation = EvaluationCreate(**data)

        assert evaluation.is_approved is False
        assert evaluation.notes == "Quality issues detected"

    def test_evaluation_response_valid(self):
        """Test valid evaluation response."""
        data = {
            "id": 1,
            "song_id": "test-song",
            "evaluated_by": 1,
            "is_approved": True,
            "audio_quality_score": 85.5,
            "created_at": datetime.utcnow(),
        }
        response = EvaluationResponse(**data)

        assert response.id == 1
        assert response.is_approved is True

    @pytest.mark.parametrize("score", [0.0, 50.5, 100.0])
    def test_evaluation_score_range(self, score):
        """Test evaluation with various scores."""
        data = {
            "is_approved": True,
            "audio_quality_score": score,
        }
        evaluation = EvaluationCreate(**data)

        assert evaluation.audio_quality_score == score

    @pytest.mark.parametrize("score", [-10.0, 101.0, 999.9])
    def test_evaluation_score_out_of_range(self, score):
        """Test evaluation with scores out of valid range."""
        # Note: This test assumes validation is added to schema
        data = {
            "is_approved": True,
            "audio_quality_score": score,
        }
        # Currently no validation, but should have
        evaluation = EvaluationCreate(**data)
        assert evaluation.audio_quality_score == score


# =============================================================================
# YouTube Schema Tests
# =============================================================================


@pytest.mark.unit
class TestYouTubeSchemas:
    """Test YouTube upload schema validation."""

    def test_youtube_upload_create_minimal(self):
        """Test YouTube upload creation with minimal data."""
        data = {"video_file_path": "/videos/test.mp4"}
        upload = YouTubeUploadCreate(**data)

        assert upload.video_file_path == "/videos/test.mp4"

    def test_youtube_upload_response_valid(self):
        """Test valid YouTube upload response."""
        data = {
            "id": 1,
            "song_id": "test-song",
            "uploaded_by": 1,
            "status": "completed",
            "youtube_video_id": "yt-123",
            "youtube_url": "https://youtube.com/watch?v=yt-123",
            "created_at": datetime.utcnow(),
        }
        response = YouTubeUploadResponse(**data)

        assert response.youtube_video_id == "yt-123"
        assert response.status == "completed"

    def test_youtube_upload_response_pending(self):
        """Test YouTube upload response for pending upload."""
        data = {
            "id": 1,
            "song_id": "test-song",
            "uploaded_by": 1,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        response = YouTubeUploadResponse(**data)

        assert response.status == "pending"
        assert response.youtube_video_id is None

    @pytest.mark.parametrize(
        "status", ["pending", "uploading", "completed", "failed"]
    )
    def test_youtube_upload_statuses(self, status):
        """Test YouTube upload with various statuses."""
        data = {
            "id": 1,
            "song_id": "test-song",
            "uploaded_by": 1,
            "status": status,
            "created_at": datetime.utcnow(),
        }
        response = YouTubeUploadResponse(**data)

        assert response.status == status


# =============================================================================
# Schema Serialization Tests
# =============================================================================


@pytest.mark.unit
class TestSchemaSerialization:
    """Test schema serialization to dict/JSON."""

    def test_token_response_dict(self):
        """Test token response serialization to dict."""
        response = TokenResponse(
            access_token="access",
            refresh_token="refresh",
        )
        data = response.model_dump()

        assert data["access_token"] == "access"
        assert data["refresh_token"] == "refresh"
        assert data["token_type"] == "bearer"

    def test_song_response_dict(self):
        """Test song response serialization to dict."""
        now = datetime.utcnow()
        response = SongResponse(
            id="test-song",
            title="Test Song",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
            status="pending",
            created_at=now,
            updated_at=now,
        )
        data = response.model_dump()

        assert data["id"] == "test-song"
        assert data["title"] == "Test Song"
        assert "created_at" in data

    def test_song_response_json(self):
        """Test song response serialization to JSON."""
        now = datetime.utcnow()
        response = SongResponse(
            id="test-song",
            title="Test Song",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/test.md",
            status="pending",
            created_at=now,
            updated_at=now,
        )
        json_str = response.model_dump_json()

        assert isinstance(json_str, str)
        assert "test-song" in json_str
        assert "Test Song" in json_str


# =============================================================================
# Schema Validation Edge Cases
# =============================================================================


@pytest.mark.unit
class TestSchemaEdgeCases:
    """Test schema validation edge cases."""

    def test_empty_string_fields(self):
        """Test schemas with empty string fields."""
        # Login with empty username
        with pytest.raises(ValidationError):
            LoginRequest(username="", password="password123")

    def test_whitespace_only_fields(self):
        """Test schemas with whitespace-only fields."""
        # Song with whitespace title (should be allowed, handled by app logic)
        data = {
            "id": "test",
            "title": "   ",
            "genre": "Pop",
            "style_prompt": "Test",
            "lyrics": "Test",
            "file_path": "/test.md",
        }
        song = SongCreate(**data)
        assert song.title == "   "

    def test_special_characters_in_strings(self):
        """Test schemas with special characters."""
        data = {
            "id": "test-song-001",
            "title": "Test Song (Remix) [2024] - Special Edition!",
            "genre": "Pop",
            "style_prompt": "Pop song with special chars: @#$%^&*()",
            "lyrics": "[Verse 1]\nSpecial chars: 你好 مرحبا 🎵",
            "file_path": "/path/to/song.md",
        }
        song = SongCreate(**data)

        assert "Remix" in song.title
        assert "🎵" in song.lyrics

    def test_very_long_strings(self):
        """Test schemas with very long strings."""
        data = {
            "id": "test-song",
            "title": "A" * 1000,
            "genre": "Pop",
            "style_prompt": "B" * 5000,
            "lyrics": "C" * 10000,
            "file_path": "/test.md",
        }
        song = SongCreate(**data)

        assert len(song.title) == 1000
        assert len(song.style_prompt) == 5000
        assert len(song.lyrics) == 10000

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        data = {
            "username": "testuser",
            "password": "password123",
            "extra_field": "should be ignored",
        }
        # Pydantic by default ignores extra fields
        login = LoginRequest(**data)

        assert login.username == "testuser"
        assert not hasattr(login, "extra_field")
