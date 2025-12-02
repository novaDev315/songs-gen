"""Integration tests for evaluation API endpoints.

Tests evaluation management including CRUD, approval/rejection, and batch operations.
"""

import pytest
from datetime import datetime


# =============================================================================
# List Evaluations Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListEvaluations:
    """Test evaluation listing functionality."""

    def test_list_evaluations_empty(self, client, auth_headers):
        """Test listing evaluations when database is empty."""
        response = client.get("/api/v1/evaluations", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0

    def test_list_evaluations_with_data(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test listing evaluations with existing data."""
        song1 = song_factory(song_id="song-001")
        song2 = song_factory(song_id="song-002")
        song3 = song_factory(song_id="song-003")

        evaluation_factory(song_id=song1.id, approved=True)
        evaluation_factory(song_id=song2.id, approved=False)
        evaluation_factory(song_id=song3.id, approved=True)

        response = client.get("/api/v1/evaluations", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 3

    def test_list_evaluations_filter_by_approved(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test filtering evaluations by approval status."""
        song1 = song_factory(song_id="song-001")
        song2 = song_factory(song_id="song-002")
        song3 = song_factory(song_id="song-003")

        evaluation_factory(song_id=song1.id, approved=True)
        evaluation_factory(song_id=song2.id, approved=False)
        evaluation_factory(song_id=song3.id, approved=True)

        response = client.get(
            "/api/v1/evaluations",
            params={"approved": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["approved"] is True for item in data["items"])

    def test_list_evaluations_filter_by_min_rating(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test filtering evaluations by minimum rating."""
        song1 = song_factory(song_id="song-001")
        song2 = song_factory(song_id="song-002")
        song3 = song_factory(song_id="song-003")

        evaluation_factory(song_id=song1.id, manual_rating=5)
        evaluation_factory(song_id=song2.id, manual_rating=8)
        evaluation_factory(song_id=song3.id, manual_rating=9)

        response = client.get(
            "/api/v1/evaluations",
            params={"min_rating": 7},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_evaluations_pagination(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test pagination of evaluation listing."""
        # Create 10 evaluations
        for i in range(10):
            song = song_factory(song_id=f"song-{i:03d}")
            evaluation_factory(song_id=song.id)

        response = client.get(
            "/api/v1/evaluations",
            params={"skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 10
        assert data["meta"]["has_more"] is True

    def test_list_evaluations_unauthorized(self, client):
        """Test listing evaluations without authentication."""
        response = client.get("/api/v1/evaluations")
        assert response.status_code == 403


# =============================================================================
# Get Evaluation Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestGetEvaluation:
    """Test getting individual evaluation details."""

    def test_get_evaluation_success(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test successful evaluation retrieval."""
        song = song_factory(song_id="song-001", title="Test Song")
        evaluation = evaluation_factory(
            song_id=song.id,
            approved=True,
            audio_quality_score=90.0,
            manual_rating=8,
        )

        response = client.get(
            f"/api/v1/evaluations/{evaluation.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == evaluation.id
        assert data["approved"] is True
        assert data["audio_quality_score"] == 90.0
        assert data["manual_rating"] == 8
        assert data["song_title"] == "Test Song"

    def test_get_evaluation_not_found(self, client, auth_headers):
        """Test getting non-existent evaluation."""
        response = client.get("/api/v1/evaluations/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_evaluation_unauthorized(
        self, client, song_factory, evaluation_factory
    ):
        """Test getting evaluation without authentication."""
        song = song_factory(song_id="song-001")
        evaluation = evaluation_factory(song_id=song.id)
        response = client.get(f"/api/v1/evaluations/{evaluation.id}")
        assert response.status_code == 403


# =============================================================================
# Create Evaluation Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCreateEvaluation:
    """Test evaluation creation."""

    def test_create_evaluation_success(self, client, auth_headers, song_factory):
        """Test successful evaluation creation."""
        song = song_factory(song_id="song-001", title="Test Song")

        evaluation_data = {
            "song_id": song.id,
            "audio_quality_score": 85.5,
            "duration_seconds": 180.0,
            "file_size_mb": 4.2,
            "sample_rate": 44100,
            "bitrate": 192000,
        }

        response = client.post(
            "/api/v1/evaluations",
            json=evaluation_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["song_id"] == song.id
        assert data["audio_quality_score"] == 85.5
        assert data["duration_seconds"] == 180.0
        assert "id" in data
        assert "evaluated_at" in data

    def test_create_evaluation_minimal_data(self, client, auth_headers, song_factory):
        """Test creating evaluation with minimal data."""
        song = song_factory(song_id="song-001")

        evaluation_data = {"song_id": song.id}

        response = client.post(
            "/api/v1/evaluations",
            json=evaluation_data,
            headers=auth_headers,
        )

        assert response.status_code == 201

    def test_create_evaluation_song_not_found(self, client, auth_headers):
        """Test creating evaluation for non-existent song."""
        evaluation_data = {
            "song_id": "nonexistent-song",
            "audio_quality_score": 85.5,
        }

        response = client.post(
            "/api/v1/evaluations",
            json=evaluation_data,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_create_evaluation_unauthorized(self, client, song_factory):
        """Test creating evaluation without authentication."""
        song = song_factory(song_id="song-001")
        response = client.post(
            "/api/v1/evaluations",
            json={"song_id": song.id},
        )
        assert response.status_code == 403


# =============================================================================
# Update Evaluation Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestUpdateEvaluation:
    """Test evaluation update functionality."""

    def test_update_evaluation_success(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test successful evaluation update."""
        song = song_factory(song_id="song-001")
        evaluation = evaluation_factory(song_id=song.id)

        response = client.put(
            f"/api/v1/evaluations/{evaluation.id}",
            json={"manual_rating": 9, "approved": True, "notes": "Great song!"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["manual_rating"] == 9
        assert data["approved"] is True
        assert data["notes"] == "Great song!"

    def test_update_evaluation_partial(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test partial evaluation update."""
        song = song_factory(song_id="song-001")
        evaluation = evaluation_factory(song_id=song.id, notes="Original notes")

        response = client.put(
            f"/api/v1/evaluations/{evaluation.id}",
            json={"manual_rating": 7},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["manual_rating"] == 7

    def test_update_evaluation_not_found(self, client, auth_headers):
        """Test updating non-existent evaluation."""
        response = client.put(
            "/api/v1/evaluations/99999",
            json={"manual_rating": 5},
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Approve Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestApproveSong:
    """Test song approval endpoint."""

    def test_approve_song_success(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test successful song approval."""
        song = song_factory(song_id="song-001", title="Test Song", status="downloaded")
        evaluation = evaluation_factory(song_id=song.id, approved=None)

        response = client.post(
            f"/api/v1/evaluations/{evaluation.id}/approve",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "approved for YouTube upload" in data["message"].lower()
        assert data["song_id"] == song.id
        assert "task_id" in data

    def test_approve_song_already_approved(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test approving already approved song."""
        song = song_factory(song_id="song-001", status="downloaded")
        evaluation = evaluation_factory(song_id=song.id, approved=True)

        response = client.post(
            f"/api/v1/evaluations/{evaluation.id}/approve",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "already approved" in response.json()["detail"].lower()

    def test_approve_song_not_found(self, client, auth_headers):
        """Test approving non-existent evaluation."""
        response = client.post(
            "/api/v1/evaluations/99999/approve",
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Reject Song Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestRejectSong:
    """Test song rejection endpoint."""

    def test_reject_song_success(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test successful song rejection."""
        song = song_factory(song_id="song-001", title="Test Song", status="downloaded")
        evaluation = evaluation_factory(song_id=song.id, approved=None)

        response = client.post(
            f"/api/v1/evaluations/{evaluation.id}/reject",
            params={"notes": "Quality issues"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "rejected" in data["message"].lower()
        assert data["song_id"] == song.id
        assert data["notes"] == "Quality issues"

    def test_reject_song_not_found(self, client, auth_headers):
        """Test rejecting non-existent evaluation."""
        response = client.post(
            "/api/v1/evaluations/99999/reject",
            params={"notes": "Test rejection"},
            headers=auth_headers,
        )
        assert response.status_code == 404


# =============================================================================
# Batch Approve Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestBatchApprove:
    """Test batch approval endpoint."""

    def test_batch_approve_success(self, client, auth_headers, song_factory):
        """Test successful batch approval."""
        song1 = song_factory(song_id="song-001", status="downloaded")
        song2 = song_factory(song_id="song-002", status="downloaded")
        song3 = song_factory(song_id="song-003", status="downloaded")

        response = client.post(
            "/api/v1/evaluations/batch-approve",
            json={
                "song_ids": [song1.id, song2.id, song3.id],
                "notes": "Batch approved",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved_count"] == 3
        assert data["failed_count"] == 0
        assert len(data["approved_song_ids"]) == 3

    def test_batch_approve_partial_failure(self, client, auth_headers, song_factory):
        """Test batch approval with some failures."""
        song1 = song_factory(song_id="song-001", status="downloaded")
        song2 = song_factory(song_id="song-002", status="downloaded")

        response = client.post(
            "/api/v1/evaluations/batch-approve",
            json={
                "song_ids": [song1.id, song2.id, "nonexistent-song"],
                "notes": "Batch approved",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved_count"] == 2
        assert data["failed_count"] == 1
        assert "nonexistent-song" in data["failed_song_ids"]
        assert "nonexistent-song" in data["errors"]

    def test_batch_approve_all_fail(self, client, auth_headers):
        """Test batch approval when all songs fail."""
        response = client.post(
            "/api/v1/evaluations/batch-approve",
            json={
                "song_ids": ["nonexistent-1", "nonexistent-2"],
                "notes": "Batch approved",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved_count"] == 0
        assert data["failed_count"] == 2

    def test_batch_approve_empty_list(self, client, auth_headers):
        """Test batch approval with empty list."""
        response = client.post(
            "/api/v1/evaluations/batch-approve",
            json={"song_ids": []},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["approved_count"] == 0
        assert data["failed_count"] == 0


# =============================================================================
# Pending Evaluations Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestPendingEvaluations:
    """Test pending evaluations endpoint."""

    def test_pending_evaluations_empty(self, client, auth_headers):
        """Test pending evaluations when none exist."""
        response = client.get("/api/v1/evaluations/pending", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_pending_evaluations_with_downloaded_songs(
        self, client, auth_headers, song_factory
    ):
        """Test pending evaluations with downloaded songs."""
        # Create downloaded songs without evaluations
        song1 = song_factory(song_id="song-001", title="Song 1", status="downloaded")
        song2 = song_factory(song_id="song-002", title="Song 2", status="downloaded")

        # Create a song that is not downloaded
        song_factory(song_id="song-003", title="Song 3", status="pending")

        response = client.get("/api/v1/evaluations/pending", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        song_ids = [item["song_id"] for item in data]
        assert song1.id in song_ids
        assert song2.id in song_ids

    def test_pending_evaluations_with_unapproved_evaluation(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test pending evaluations includes songs with unapproved evaluations."""
        song = song_factory(song_id="song-001", title="Test Song", status="downloaded")
        evaluation_factory(song_id=song.id, approved=None)  # Not yet approved/rejected

        response = client.get("/api/v1/evaluations/pending", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["song_id"] == song.id
        assert data[0]["has_evaluation"] is True

    def test_pending_evaluations_excludes_approved(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test pending evaluations excludes approved songs."""
        song = song_factory(song_id="song-001", status="downloaded")
        evaluation_factory(song_id=song.id, approved=True)

        response = client.get("/api/v1/evaluations/pending", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_pending_evaluations_with_limit(
        self, client, auth_headers, song_factory
    ):
        """Test pending evaluations with limit parameter."""
        # Create 10 downloaded songs
        for i in range(10):
            song_factory(song_id=f"song-{i:03d}", status="downloaded")

        response = client.get(
            "/api/v1/evaluations/pending",
            params={"limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_pending_evaluations_limit_max_100(
        self, client, auth_headers, song_factory
    ):
        """Test that pending evaluations limit is capped at 100."""
        song_factory(song_id="song-001", status="downloaded")

        response = client.get(
            "/api/v1/evaluations/pending",
            params={"limit": 200},
            headers=auth_headers,
        )

        # Should not fail, limit will be capped internally
        assert response.status_code == 200


# =============================================================================
# Evaluation with Song Details Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestEvaluationSongDetails:
    """Test that evaluations include song details."""

    def test_evaluation_includes_song_title(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test that evaluation response includes song title."""
        song = song_factory(
            song_id="song-001",
            title="My Amazing Song",
            genre="Pop",
            status="downloaded",
        )
        evaluation = evaluation_factory(song_id=song.id)

        response = client.get(
            f"/api/v1/evaluations/{evaluation.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["song_title"] == "My Amazing Song"
        assert data["song_genre"] == "Pop"
        assert data["song_status"] == "downloaded"

    def test_evaluation_list_includes_song_details(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test that evaluation list includes song details."""
        song = song_factory(song_id="song-001", title="Test Song", genre="Rock")
        evaluation_factory(song_id=song.id)

        response = client.get("/api/v1/evaluations", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["song_title"] == "Test Song"
        assert data["items"][0]["song_genre"] == "Rock"
