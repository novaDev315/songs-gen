"""Integration tests for YouTube API endpoints.

Tests YouTube upload management, OAuth flow, and upload operations.
"""

import pytest
from unittest.mock import patch, MagicMock


# =============================================================================
# List YouTube Uploads Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListYouTubeUploads:
    """Test YouTube upload listing functionality."""

    def test_list_uploads_empty(self, client, auth_headers):
        """Test listing uploads when database is empty."""
        response = client.get("/api/v1/youtube/uploads", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0

    def test_list_uploads_with_data(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test listing uploads with existing data."""
        song1 = song_factory(song_id="song-001")
        song2 = song_factory(song_id="song-002")
        song3 = song_factory(song_id="song-003")

        youtube_upload_factory(song_id=song1.id, upload_status="published")
        youtube_upload_factory(song_id=song2.id, upload_status="pending")
        youtube_upload_factory(song_id=song3.id, upload_status="published")

        response = client.get("/api/v1/youtube/uploads", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 3

    def test_list_uploads_filter_by_status(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test filtering uploads by status."""
        song1 = song_factory(song_id="song-001")
        song2 = song_factory(song_id="song-002")
        song3 = song_factory(song_id="song-003")

        youtube_upload_factory(song_id=song1.id, upload_status="published")
        youtube_upload_factory(song_id=song2.id, upload_status="pending")
        youtube_upload_factory(song_id=song3.id, upload_status="published")

        response = client.get(
            "/api/v1/youtube/uploads",
            params={"upload_status": "published"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["upload_status"] == "published" for item in data["items"])

    def test_list_uploads_pagination(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test pagination of upload listing."""
        for i in range(10):
            song = song_factory(song_id=f"song-{i:03d}")
            youtube_upload_factory(song_id=song.id)

        response = client.get(
            "/api/v1/youtube/uploads",
            params={"skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 10
        assert data["meta"]["has_more"] is True

    def test_list_uploads_unauthorized(self, client):
        """Test listing uploads without authentication."""
        response = client.get("/api/v1/youtube/uploads")
        assert response.status_code == 403


# =============================================================================
# Get YouTube Upload Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestGetYouTubeUpload:
    """Test getting individual upload details."""

    def test_get_upload_success(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test successful upload retrieval."""
        song = song_factory(song_id="song-001", title="Test Song", genre="Pop")
        upload = youtube_upload_factory(
            song_id=song.id,
            title="Test Video",
            upload_status="published",
            video_url="https://youtube.com/watch?v=abc123",
        )

        response = client.get(
            f"/api/v1/youtube/uploads/{upload.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == upload.id
        assert data["title"] == "Test Video"
        assert data["upload_status"] == "published"
        assert data["video_url"] == "https://youtube.com/watch?v=abc123"
        assert data["song_title"] == "Test Song"
        assert data["song_genre"] == "Pop"

    def test_get_upload_not_found(self, client, auth_headers):
        """Test getting non-existent upload."""
        response = client.get("/api/v1/youtube/uploads/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_upload_unauthorized(
        self, client, song_factory, youtube_upload_factory
    ):
        """Test getting upload without authentication."""
        song = song_factory(song_id="song-001")
        upload = youtube_upload_factory(song_id=song.id)
        response = client.get(f"/api/v1/youtube/uploads/{upload.id}")
        assert response.status_code == 403


# =============================================================================
# Upload to YouTube Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUploadToYouTube:
    """Test YouTube upload creation."""

    def test_upload_to_youtube_success(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test successful YouTube upload creation."""
        song = song_factory(song_id="song-001", title="Test Song", status="evaluated")
        evaluation_factory(song_id=song.id, approved=True)

        upload_data = {
            "song_id": song.id,
            "title": "My YouTube Video",
            "description": "A great song",
            "tags": "music,pop,test",
            "privacy": "private",
        }

        response = client.post(
            "/api/v1/youtube/upload",
            json=upload_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["song_id"] == song.id
        assert data["title"] == "My YouTube Video"
        assert data["upload_status"] == "pending"
        assert data["privacy"] == "private"

    def test_upload_to_youtube_song_not_found(self, client, auth_headers):
        """Test upload with non-existent song."""
        upload_data = {
            "song_id": "nonexistent-song",
            "title": "Test Video",
        }

        response = client.post(
            "/api/v1/youtube/upload",
            json=upload_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_upload_to_youtube_song_not_evaluated(
        self, client, auth_headers, song_factory
    ):
        """Test upload when song is not evaluated."""
        song = song_factory(song_id="song-001", status="pending")

        upload_data = {
            "song_id": song.id,
            "title": "Test Video",
        }

        response = client.post(
            "/api/v1/youtube/upload",
            json=upload_data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "evaluated" in response.json()["detail"].lower()

    def test_upload_to_youtube_song_not_approved(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test upload when song is not approved."""
        song = song_factory(song_id="song-001", status="evaluated")
        evaluation_factory(song_id=song.id, approved=False)

        upload_data = {
            "song_id": song.id,
            "title": "Test Video",
        }

        response = client.post(
            "/api/v1/youtube/upload",
            json=upload_data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "approved" in response.json()["detail"].lower()

    def test_upload_to_youtube_unauthorized(self, client, song_factory):
        """Test upload without authentication."""
        song = song_factory(song_id="song-001", status="evaluated")
        response = client.post(
            "/api/v1/youtube/upload",
            json={"song_id": song.id, "title": "Test"},
        )
        assert response.status_code == 403


# =============================================================================
# OAuth URL Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestOAuthURL:
    """Test OAuth URL generation."""

    def test_get_oauth_url_success(self, client, auth_headers):
        """Test successful OAuth URL generation."""
        with patch("app.api.youtube.get_youtube_uploader") as mock_uploader:
            mock_instance = MagicMock()
            mock_instance.get_auth_url.return_value = "https://accounts.google.com/o/oauth2/auth?client_id=..."
            mock_uploader.return_value = mock_instance

            response = client.get("/api/v1/youtube/oauth-url", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert "authorization_url" in data
            assert data["authorization_url"].startswith("https://accounts.google.com")

    def test_get_oauth_url_error(self, client, auth_headers):
        """Test OAuth URL generation error handling."""
        with patch("app.api.youtube.get_youtube_uploader") as mock_uploader:
            mock_instance = MagicMock()
            mock_instance.get_auth_url.side_effect = ValueError("OAuth credentials not configured")
            mock_uploader.return_value = mock_instance

            response = client.get("/api/v1/youtube/oauth-url", headers=auth_headers)

            assert response.status_code == 500
            assert "OAuth" in response.json()["detail"]

    def test_get_oauth_url_unauthorized(self, client):
        """Test OAuth URL without authentication."""
        response = client.get("/api/v1/youtube/oauth-url")
        assert response.status_code == 403


# =============================================================================
# OAuth Callback Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestOAuthCallback:
    """Test OAuth callback handling."""

    def test_oauth_callback_success(self, client, auth_headers):
        """Test successful OAuth callback."""
        with patch("app.api.youtube.get_youtube_uploader") as mock_uploader:
            mock_instance = MagicMock()
            mock_instance.handle_oauth_callback.return_value = True
            mock_uploader.return_value = mock_instance

            response = client.post(
                "/api/v1/youtube/oauth-callback",
                json={"code": "auth_code_123"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "authenticated"

    def test_oauth_callback_invalid_code(self, client, auth_headers):
        """Test OAuth callback with invalid code."""
        with patch("app.api.youtube.get_youtube_uploader") as mock_uploader:
            mock_instance = MagicMock()
            mock_instance.handle_oauth_callback.return_value = False
            mock_uploader.return_value = mock_instance

            response = client.post(
                "/api/v1/youtube/oauth-callback",
                json={"code": "invalid_code"},
                headers=auth_headers,
            )

            assert response.status_code == 400
            assert "invalid authorization code" in response.json()["detail"].lower()

    def test_oauth_callback_error(self, client, auth_headers):
        """Test OAuth callback error handling."""
        with patch("app.api.youtube.get_youtube_uploader") as mock_uploader:
            mock_instance = MagicMock()
            mock_instance.handle_oauth_callback.side_effect = Exception("Token exchange failed")
            mock_uploader.return_value = mock_instance

            response = client.post(
                "/api/v1/youtube/oauth-callback",
                json={"code": "test_code"},
                headers=auth_headers,
            )

            assert response.status_code == 500

    def test_oauth_callback_unauthorized(self, client):
        """Test OAuth callback without authentication."""
        response = client.post(
            "/api/v1/youtube/oauth-callback",
            json={"code": "test_code"},
        )
        assert response.status_code == 403


# =============================================================================
# Delete Upload Record Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDeleteUploadRecord:
    """Test YouTube upload record deletion."""

    def test_delete_upload_success(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test successful upload record deletion."""
        song = song_factory(song_id="song-001")
        upload = youtube_upload_factory(
            song_id=song.id,
            video_id="yt-video-123",
        )

        response = client.delete(
            f"/api/v1/youtube/uploads/{upload.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["upload_id"] == upload.id
        assert data["song_id"] == song.id
        assert data["video_id"] == "yt-video-123"
        assert "note" in data  # Warning about video still on YouTube

        # Verify record is deleted
        get_response = client.get(
            f"/api/v1/youtube/uploads/{upload.id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    def test_delete_upload_not_found(self, client, auth_headers):
        """Test deleting non-existent upload record."""
        response = client.delete("/api/v1/youtube/uploads/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_upload_unauthorized(
        self, client, song_factory, youtube_upload_factory
    ):
        """Test deleting upload without authentication."""
        song = song_factory(song_id="song-001")
        upload = youtube_upload_factory(song_id=song.id)
        response = client.delete(f"/api/v1/youtube/uploads/{upload.id}")
        assert response.status_code == 403


# =============================================================================
# Upload with Song Details Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUploadSongDetails:
    """Test that uploads include song details."""

    def test_upload_includes_song_details(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test that upload response includes song details."""
        song = song_factory(
            song_id="song-001",
            title="Amazing Song",
            genre="Rock",
        )
        upload = youtube_upload_factory(song_id=song.id)

        response = client.get(
            f"/api/v1/youtube/uploads/{upload.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_title"] == "Amazing Song"
        assert data["song_genre"] == "Rock"

    def test_upload_list_includes_song_details(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test that upload list includes song details."""
        song = song_factory(song_id="song-001", title="Test Song", genre="Pop")
        youtube_upload_factory(song_id=song.id)

        response = client.get("/api/v1/youtube/uploads", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["song_title"] == "Test Song"
        assert data["items"][0]["song_genre"] == "Pop"
