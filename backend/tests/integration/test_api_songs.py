"""Integration tests for songs API endpoints.

Tests complete song management including CRUD operations, filtering, and status tracking.
"""

import pytest
from datetime import datetime


# =============================================================================
# Song List Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListSongs:
    """Test song listing functionality."""

    def test_list_songs_empty(self, client, auth_headers):
        """Test listing songs when database is empty."""
        response = client.get("/api/v1/songs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0
        assert data["meta"]["has_more"] is False

    def test_list_songs_with_data(self, client, auth_headers, song_factory):
        """Test listing songs with existing data."""
        # Create test songs
        song_factory(song_id="song-001", title="First Song", genre="Pop")
        song_factory(song_id="song-002", title="Second Song", genre="Rock")
        song_factory(song_id="song-003", title="Third Song", genre="Pop")

        response = client.get("/api/v1/songs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 3
        assert data["meta"]["has_more"] is False

    def test_list_songs_filter_by_status(self, client, auth_headers, song_factory):
        """Test filtering songs by status."""
        song_factory(song_id="song-001", status="pending")
        song_factory(song_id="song-002", status="generating")
        song_factory(song_id="song-003", status="pending")

        response = client.get(
            "/api/v1/songs",
            params={"status_filter": "pending"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["status"] == "pending" for item in data["items"])

    def test_list_songs_filter_by_genre(self, client, auth_headers, song_factory):
        """Test filtering songs by genre."""
        song_factory(song_id="song-001", genre="Pop")
        song_factory(song_id="song-002", genre="Rock")
        song_factory(song_id="song-003", genre="Pop")

        response = client.get(
            "/api/v1/songs",
            params={"genre": "Pop"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["genre"] == "Pop" for item in data["items"])

    def test_list_songs_pagination(self, client, auth_headers, song_factory):
        """Test pagination of song listing."""
        # Create 10 songs
        for i in range(10):
            song_factory(song_id=f"song-{i:03d}", title=f"Song {i}")

        # First page
        response = client.get(
            "/api/v1/songs",
            params={"skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 10
        assert data["meta"]["skip"] == 0
        assert data["meta"]["limit"] == 3
        assert data["meta"]["has_more"] is True

        # Second page
        response = client.get(
            "/api/v1/songs",
            params={"skip": 3, "limit": 3},
            headers=auth_headers,
        )

        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["skip"] == 3
        assert data["meta"]["has_more"] is True

    def test_list_songs_limit_max_100(self, client, auth_headers, song_factory):
        """Test that limit is capped at 100."""
        song_factory(song_id="song-001")

        response = client.get(
            "/api/v1/songs",
            params={"limit": 200},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["limit"] == 100

    def test_list_songs_unauthorized(self, client):
        """Test listing songs without authentication."""
        response = client.get("/api/v1/songs")
        assert response.status_code == 403


# =============================================================================
# Get Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestGetSong:
    """Test getting individual song details."""

    def test_get_song_success(self, client, auth_headers, song_factory):
        """Test successful song retrieval."""
        song = song_factory(
            song_id="song-001",
            title="Test Song",
            genre="Pop",
            status="pending",
        )

        response = client.get(f"/api/v1/songs/{song.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == song.id
        assert data["title"] == "Test Song"
        assert data["genre"] == "Pop"
        assert data["status"] == "pending"

    def test_get_song_not_found(self, client, auth_headers):
        """Test getting non-existent song."""
        response = client.get("/api/v1/songs/nonexistent-id", headers=auth_headers)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_song_unauthorized(self, client, song_factory):
        """Test getting song without authentication."""
        song = song_factory(song_id="song-001")
        response = client.get(f"/api/v1/songs/{song.id}")
        assert response.status_code == 403


# =============================================================================
# Create Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCreateSong:
    """Test song creation."""

    def test_create_song_success(self, client, auth_headers):
        """Test successful song creation."""
        song_data = {
            "title": "New Song",
            "genre": "Pop",
            "style_prompt": "Upbeat pop song with electronic elements",
            "lyrics": "[Verse 1]\nTest lyrics\n\n[Chorus]\nTest chorus",
            "file_path": "/generated/songs/new-song.md",
        }

        response = client.post(
            "/api/v1/songs",
            json=song_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == song_data["title"]
        assert data["genre"] == song_data["genre"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_song_minimal_data(self, client, auth_headers):
        """Test creating song with minimal required data."""
        song_data = {
            "title": "Minimal Song",
            "genre": "Rock",
            "style_prompt": "Rock song",
            "lyrics": "[Verse]\nLyrics",
        }

        response = client.post(
            "/api/v1/songs",
            json=song_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Song"

    def test_create_song_with_metadata(self, client, auth_headers):
        """Test creating song with metadata JSON."""
        song_data = {
            "title": "Song with Metadata",
            "genre": "Pop",
            "style_prompt": "Pop song",
            "lyrics": "[Verse]\nLyrics",
            "metadata_json": {"bpm": 120, "key": "C major"},
        }

        response = client.post(
            "/api/v1/songs",
            json=song_data,
            headers=auth_headers,
        )

        assert response.status_code == 201

    def test_create_song_missing_required_fields(self, client, auth_headers):
        """Test creating song without required fields."""
        # Missing title
        response = client.post(
            "/api/v1/songs",
            json={"genre": "Pop", "style_prompt": "Test", "lyrics": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 422

        # Missing genre
        response = client.post(
            "/api/v1/songs",
            json={"title": "Test", "style_prompt": "Test", "lyrics": "Test"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_create_song_unauthorized(self, client):
        """Test creating song without authentication."""
        response = client.post(
            "/api/v1/songs",
            json={
                "title": "Test",
                "genre": "Pop",
                "style_prompt": "Test",
                "lyrics": "Test",
            },
        )
        assert response.status_code == 403


# =============================================================================
# Update Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUpdateSong:
    """Test song update functionality."""

    def test_update_song_success(self, client, auth_headers, song_factory):
        """Test successful song update."""
        song = song_factory(song_id="song-001", title="Original Title")

        response = client.put(
            f"/api/v1/songs/{song.id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_update_song_multiple_fields(self, client, auth_headers, song_factory):
        """Test updating multiple song fields."""
        song = song_factory(song_id="song-001", title="Original", genre="Pop")

        response = client.put(
            f"/api/v1/songs/{song.id}",
            json={
                "title": "Updated Title",
                "genre": "Rock",
                "status": "generating",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["genre"] == "Rock"
        assert data["status"] == "generating"

    def test_update_song_not_found(self, client, auth_headers):
        """Test updating non-existent song."""
        response = client.put(
            "/api/v1/songs/nonexistent-id",
            json={"title": "New Title"},
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_song_unauthorized(self, client, song_factory):
        """Test updating song without authentication."""
        song = song_factory(song_id="song-001")
        response = client.put(
            f"/api/v1/songs/{song.id}",
            json={"title": "New Title"},
        )
        assert response.status_code == 403


# =============================================================================
# Delete Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDeleteSong:
    """Test song deletion."""

    def test_delete_song_success(self, client, auth_headers, song_factory):
        """Test successful song deletion."""
        song = song_factory(song_id="song-001", title="To Delete")

        response = client.delete(f"/api/v1/songs/{song.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted_id"] == song.id
        assert "deleted successfully" in data["message"].lower()

        # Verify song is deleted
        get_response = client.get(f"/api/v1/songs/{song.id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_song_not_found(self, client, auth_headers):
        """Test deleting non-existent song."""
        response = client.delete("/api/v1/songs/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_song_unauthorized(self, client, song_factory):
        """Test deleting song without authentication."""
        song = song_factory(song_id="song-001")
        response = client.delete(f"/api/v1/songs/{song.id}")
        assert response.status_code == 403


# =============================================================================
# Song Status Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestSongStatus:
    """Test detailed song status endpoint."""

    def test_get_song_status_basic(self, client, auth_headers, song_factory):
        """Test getting basic song status."""
        song = song_factory(song_id="song-001", title="Test Song", status="pending")

        response = client.get(f"/api/v1/songs/{song.id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == song.id
        assert data["title"] == "Test Song"
        assert data["status"] == "pending"
        assert data["suno_job_count"] == 0
        assert data["evaluation_count"] == 0
        assert data["youtube_upload_count"] == 0
        assert data["is_evaluated"] is False

    def test_get_song_status_with_suno_job(
        self, client, auth_headers, song_factory, suno_job_factory
    ):
        """Test song status with Suno job."""
        song = song_factory(song_id="song-001", status="generating")
        suno_job_factory(song_id=song.id, status="completed")

        response = client.get(f"/api/v1/songs/{song.id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["suno_job_count"] == 1
        assert data["latest_suno_status"] == "completed"

    def test_get_song_status_with_evaluation(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test song status with evaluation."""
        song = song_factory(song_id="song-001", status="evaluated")
        evaluation_factory(song_id=song.id, approved=True, manual_rating=8)

        response = client.get(f"/api/v1/songs/{song.id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["evaluation_count"] == 1
        assert data["is_evaluated"] is True
        assert data["is_approved"] is True
        assert data["manual_rating"] == 8

    def test_get_song_status_with_youtube_upload(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test song status with YouTube upload."""
        song = song_factory(song_id="song-001", status="uploaded")
        youtube_upload_factory(
            song_id=song.id,
            upload_status="published",
            video_url="https://youtube.com/watch?v=abc123",
        )

        response = client.get(f"/api/v1/songs/{song.id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["youtube_upload_count"] == 1
        assert data["latest_youtube_status"] == "published"
        assert data["video_url"] == "https://youtube.com/watch?v=abc123"

    def test_get_song_status_with_tasks(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test song status with tasks."""
        song = song_factory(song_id="song-001", status="generating")
        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_download", status="running")
        task_factory(song_id=song.id, task_type="evaluate", status="failed")

        response = client.get(f"/api/v1/songs/{song.id}/status", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_tasks"] == 1
        assert data["running_tasks"] == 1
        assert data["failed_tasks"] == 1

    def test_get_song_status_not_found(self, client, auth_headers):
        """Test getting status for non-existent song."""
        response = client.get("/api/v1/songs/nonexistent-id/status", headers=auth_headers)
        assert response.status_code == 404


# =============================================================================
# Upload to Suno Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUploadToSuno:
    """Test Suno upload queue endpoint."""

    def test_upload_to_suno_success(self, client, auth_headers, song_factory):
        """Test successful Suno upload queue."""
        song = song_factory(song_id="song-001", status="pending")

        response = client.post(
            f"/api/v1/songs/{song.id}/upload-to-suno",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_id"] == song.id
        assert data["status"] == "uploading"
        assert "task_id" in data

    def test_upload_to_suno_with_priority(self, client, auth_headers, song_factory):
        """Test Suno upload with custom priority."""
        song = song_factory(song_id="song-001", status="pending")

        response = client.post(
            f"/api/v1/songs/{song.id}/upload-to-suno",
            params={"priority": 75},
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_upload_to_suno_already_uploading(self, client, auth_headers, song_factory):
        """Test upload when song is already uploading."""
        song = song_factory(song_id="song-001", status="uploading")

        response = client.post(
            f"/api/v1/songs/{song.id}/upload-to-suno",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already in status" in response.json()["detail"].lower()

    def test_upload_to_suno_already_generating(self, client, auth_headers, song_factory):
        """Test upload when song is already generating."""
        song = song_factory(song_id="song-001", status="generating")

        response = client.post(
            f"/api/v1/songs/{song.id}/upload-to-suno",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_upload_to_suno_not_found(self, client, auth_headers):
        """Test upload for non-existent song."""
        response = client.post(
            "/api/v1/songs/nonexistent-id/upload-to-suno",
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Download Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestDownloadSong:
    """Test song download queue endpoint."""

    def test_download_song_success(self, client, auth_headers, song_factory):
        """Test successful download queue."""
        song = song_factory(song_id="song-001", status="generating")

        response = client.post(
            f"/api/v1/songs/{song.id}/download",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_id"] == song.id
        assert "task_id" in data

    def test_download_song_with_priority(self, client, auth_headers, song_factory):
        """Test download with custom priority."""
        song = song_factory(song_id="song-001", status="generating")

        response = client.post(
            f"/api/v1/songs/{song.id}/download",
            params={"priority": 50},
            headers=auth_headers,
        )

        assert response.status_code == 200

    def test_download_song_not_generating(self, client, auth_headers, song_factory):
        """Test download when song is not in generating status.

        Note: The API allows this but logs a warning.
        """
        song = song_factory(song_id="song-001", status="pending")

        response = client.post(
            f"/api/v1/songs/{song.id}/download",
            headers=auth_headers,
        )

        # Should still succeed but log a warning
        assert response.status_code == 200

    def test_download_song_not_found(self, client, auth_headers):
        """Test download for non-existent song."""
        response = client.post(
            "/api/v1/songs/nonexistent-id/download",
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Combined Filter Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCombinedFilters:
    """Test combining multiple filters."""

    def test_filter_by_status_and_genre(self, client, auth_headers, song_factory):
        """Test filtering by both status and genre."""
        song_factory(song_id="song-001", status="pending", genre="Pop")
        song_factory(song_id="song-002", status="generating", genre="Pop")
        song_factory(song_id="song-003", status="pending", genre="Rock")
        song_factory(song_id="song-004", status="pending", genre="Pop")

        response = client.get(
            "/api/v1/songs",
            params={"status_filter": "pending", "genre": "Pop"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(
            item["status"] == "pending" and item["genre"] == "Pop"
            for item in data["items"]
        )

    def test_filter_with_pagination(self, client, auth_headers, song_factory):
        """Test filtering with pagination."""
        # Create 5 pending Pop songs
        for i in range(5):
            song_factory(song_id=f"song-pop-{i:03d}", status="pending", genre="Pop")

        # Create some other songs
        song_factory(song_id="song-rock-001", status="pending", genre="Rock")

        response = client.get(
            "/api/v1/songs",
            params={"genre": "Pop", "skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 5
        assert data["meta"]["has_more"] is True
