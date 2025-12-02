"""Integration tests for queue API endpoints.

Tests task queue management including CRUD, stats, and batch operations.
"""

import pytest
from datetime import datetime


# =============================================================================
# List Tasks Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestListTasks:
    """Test task listing functionality."""

    def test_list_tasks_empty(self, client, auth_headers):
        """Test listing tasks when queue is empty."""
        response = client.get("/api/v1/queue/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["meta"]["total"] == 0

    def test_list_tasks_with_data(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test listing tasks with existing data."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_download", status="running")
        task_factory(song_id=song.id, task_type="youtube_upload", status="completed")

        response = client.get("/api/v1/queue/tasks", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 3

    def test_list_tasks_filter_by_status(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test filtering tasks by status."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_download", status="pending")
        task_factory(song_id=song.id, task_type="youtube_upload", status="completed")

        response = client.get(
            "/api/v1/queue/tasks",
            params={"status_filter": "pending"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["status"] == "pending" for item in data["items"])

    def test_list_tasks_filter_by_type(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test filtering tasks by type."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_upload", status="running")
        task_factory(song_id=song.id, task_type="youtube_upload", status="pending")

        response = client.get(
            "/api/v1/queue/tasks",
            params={"task_type": "suno_upload"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(item["task_type"] == "suno_upload" for item in data["items"])

    def test_list_tasks_pagination(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test pagination of task listing."""
        song = song_factory(song_id="song-001")

        for i in range(10):
            task_factory(song_id=song.id, task_type="suno_upload")

        response = client.get(
            "/api/v1/queue/tasks",
            params={"skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 10
        assert data["meta"]["has_more"] is True

    def test_list_tasks_limit_max_200(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test that limit is capped at 200."""
        song = song_factory(song_id="song-001")
        task_factory(song_id=song.id)

        response = client.get(
            "/api/v1/queue/tasks",
            params={"limit": 500},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["limit"] == 200

    def test_list_tasks_unauthorized(self, client):
        """Test listing tasks without authentication."""
        response = client.get("/api/v1/queue/tasks")
        assert response.status_code == 403


# =============================================================================
# Queue Stats Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestQueueStats:
    """Test queue statistics endpoint."""

    def test_queue_stats_empty(self, client, auth_headers):
        """Test queue stats when queue is empty."""
        response = client.get("/api/v1/queue/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_count"] == 0
        assert data["running_count"] == 0
        assert data["completed_count"] == 0
        assert data["failed_count"] == 0
        assert data["total_count"] == 0

    def test_queue_stats_with_tasks(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test queue stats with existing tasks."""
        song = song_factory(song_id="song-001")

        # Create tasks with different statuses
        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_download", status="running")
        task_factory(song_id=song.id, task_type="youtube_upload", status="completed")
        task_factory(song_id=song.id, task_type="evaluate", status="failed")

        response = client.get("/api/v1/queue/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pending_count"] == 2
        assert data["running_count"] == 1
        assert data["completed_count"] == 1
        assert data["failed_count"] == 1
        assert data["total_count"] == 5

    def test_queue_stats_task_type_counts(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test queue stats shows task type counts."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, task_type="suno_upload")
        task_factory(song_id=song.id, task_type="suno_upload")
        task_factory(song_id=song.id, task_type="suno_download")
        task_factory(song_id=song.id, task_type="youtube_upload")

        response = client.get("/api/v1/queue/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["suno_upload_count"] == 2
        assert data["suno_download_count"] == 1
        assert data["youtube_upload_count"] == 1
        assert data["evaluate_count"] == 0

    def test_queue_stats_unauthorized(self, client):
        """Test queue stats without authentication."""
        response = client.get("/api/v1/queue/stats")
        assert response.status_code == 403


# =============================================================================
# Enqueue Task Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestEnqueueTask:
    """Test task creation endpoint."""

    def test_enqueue_task_success(self, client, auth_headers, song_factory):
        """Test successful task creation."""
        song = song_factory(song_id="song-001")

        task_data = {
            "task_type": "suno_upload",
            "song_id": song.id,
            "priority": 50,
        }

        response = client.post(
            "/api/v1/queue/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "suno_upload"
        assert data["song_id"] == song.id
        assert data["status"] == "pending"
        assert data["priority"] == 50

    def test_enqueue_task_with_payload(self, client, auth_headers, song_factory):
        """Test creating task with payload."""
        song = song_factory(song_id="song-001")

        task_data = {
            "task_type": "suno_upload",
            "song_id": song.id,
            "payload": {"extra_param": "value"},
        }

        response = client.post(
            "/api/v1/queue/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 201

    def test_enqueue_task_invalid_type(self, client, auth_headers, song_factory):
        """Test creating task with invalid type."""
        song = song_factory(song_id="song-001")

        task_data = {
            "task_type": "invalid_type",
            "song_id": song.id,
        }

        response = client.post(
            "/api/v1/queue/tasks",
            json=task_data,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "Invalid task_type" in response.json()["detail"]

    def test_enqueue_task_all_valid_types(self, client, auth_headers, song_factory):
        """Test creating tasks with all valid types."""
        song = song_factory(song_id="song-001")

        valid_types = ["suno_upload", "suno_download", "youtube_upload", "evaluate"]

        for task_type in valid_types:
            response = client.post(
                "/api/v1/queue/tasks",
                json={"task_type": task_type, "song_id": song.id},
                headers=auth_headers,
            )

            assert response.status_code == 201
            assert response.json()["task_type"] == task_type

    def test_enqueue_task_unauthorized(self, client, song_factory):
        """Test creating task without authentication."""
        song = song_factory(song_id="song-001")
        response = client.post(
            "/api/v1/queue/tasks",
            json={"task_type": "suno_upload", "song_id": song.id},
        )
        assert response.status_code == 403


# =============================================================================
# Cancel Task Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCancelTask:
    """Test task cancellation."""

    def test_cancel_task_success(self, client, auth_headers, song_factory, task_factory):
        """Test successful task cancellation."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, task_type="suno_upload", status="pending")

        response = client.delete(
            f"/api/v1/queue/tasks/{task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == task.id
        assert "cancelled successfully" in data["message"].lower()

    def test_cancel_task_not_pending(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test cancelling non-pending task."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, task_type="suno_upload", status="running")

        response = client.delete(
            f"/api/v1/queue/tasks/{task.id}",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "pending" in response.json()["detail"].lower()

    def test_cancel_task_not_found(self, client, auth_headers):
        """Test cancelling non-existent task."""
        response = client.delete("/api/v1/queue/tasks/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_cancel_task_unauthorized(self, client, song_factory, task_factory):
        """Test cancelling task without authentication."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, status="pending")
        response = client.delete(f"/api/v1/queue/tasks/{task.id}")
        assert response.status_code == 403


# =============================================================================
# Retry Task Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestRetryTask:
    """Test task retry functionality."""

    def test_retry_task_failed(self, client, auth_headers, song_factory, task_factory):
        """Test retrying failed task."""
        song = song_factory(song_id="song-001")
        task = task_factory(
            song_id=song.id,
            task_type="suno_upload",
            status="failed",
            error_message="Connection timeout",
        )

        response = client.post(
            f"/api/v1/queue/tasks/{task.id}/retry",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["status"] == "pending"
        assert data["error_message"] is None

    def test_retry_task_completed(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test retrying completed task."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, task_type="suno_upload", status="completed")

        response = client.post(
            f"/api/v1/queue/tasks/{task.id}/retry",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"

    def test_retry_task_pending(self, client, auth_headers, song_factory, task_factory):
        """Test retrying pending task (should fail)."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, task_type="suno_upload", status="pending")

        response = client.post(
            f"/api/v1/queue/tasks/{task.id}/retry",
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "failed" in response.json()["detail"].lower() or "completed" in response.json()["detail"].lower()

    def test_retry_task_running(self, client, auth_headers, song_factory, task_factory):
        """Test retrying running task (should fail)."""
        song = song_factory(song_id="song-001")
        task = task_factory(song_id=song.id, task_type="suno_upload", status="running")

        response = client.post(
            f"/api/v1/queue/tasks/{task.id}/retry",
            headers=auth_headers,
        )

        assert response.status_code == 400

    def test_retry_task_not_found(self, client, auth_headers):
        """Test retrying non-existent task."""
        response = client.post("/api/v1/queue/tasks/99999/retry", headers=auth_headers)
        assert response.status_code == 404


# =============================================================================
# Clear Completed Tasks Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestClearCompletedTasks:
    """Test clearing completed tasks."""

    def test_clear_completed_success(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test clearing completed tasks."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="failed")

        response = client.post("/api/v1/queue/clear-completed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2

        # Verify only completed tasks were deleted
        list_response = client.get("/api/v1/queue/tasks", headers=auth_headers)
        assert list_response.json()["meta"]["total"] == 2

    def test_clear_completed_empty(self, client, auth_headers):
        """Test clearing when no completed tasks exist."""
        response = client.post("/api/v1/queue/clear-completed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0

    def test_clear_completed_unauthorized(self, client):
        """Test clearing without authentication."""
        response = client.post("/api/v1/queue/clear-completed")
        assert response.status_code == 403


# =============================================================================
# Clear Failed Tasks Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestClearFailedTasks:
    """Test clearing failed tasks."""

    def test_clear_failed_success(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test clearing failed tasks."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, status="failed")
        task_factory(song_id=song.id, status="failed")
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="completed")

        response = client.post("/api/v1/queue/clear-failed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 2

        # Verify only failed tasks were deleted
        list_response = client.get("/api/v1/queue/tasks", headers=auth_headers)
        assert list_response.json()["meta"]["total"] == 2

    def test_clear_failed_empty(self, client, auth_headers):
        """Test clearing when no failed tasks exist."""
        response = client.post("/api/v1/queue/clear-failed", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["deleted_count"] == 0

    def test_clear_failed_unauthorized(self, client):
        """Test clearing without authentication."""
        response = client.post("/api/v1/queue/clear-failed")
        assert response.status_code == 403


# =============================================================================
# Combined Filter Tests
# =============================================================================


@pytest.mark.integration
@pytest.mark.api
class TestCombinedFilters:
    """Test combining multiple filters."""

    def test_filter_by_status_and_type(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test filtering by both status and type."""
        song = song_factory(song_id="song-001")

        task_factory(song_id=song.id, task_type="suno_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_upload", status="running")
        task_factory(song_id=song.id, task_type="youtube_upload", status="pending")
        task_factory(song_id=song.id, task_type="suno_upload", status="pending")

        response = client.get(
            "/api/v1/queue/tasks",
            params={"status_filter": "pending", "task_type": "suno_upload"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert all(
            item["status"] == "pending" and item["task_type"] == "suno_upload"
            for item in data["items"]
        )

    def test_filter_with_pagination(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test filtering with pagination."""
        song = song_factory(song_id="song-001")

        # Create 5 pending suno_upload tasks
        for _ in range(5):
            task_factory(song_id=song.id, task_type="suno_upload", status="pending")

        # Create some other tasks
        task_factory(song_id=song.id, task_type="youtube_upload", status="pending")

        response = client.get(
            "/api/v1/queue/tasks",
            params={"task_type": "suno_upload", "skip": 0, "limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["meta"]["total"] == 5
        assert data["meta"]["has_more"] is True
