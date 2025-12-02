"""Integration tests for system API endpoints."""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.song import Song
from app.models.task_queue import TaskQueue


class TestSystemStatusEndpoint:
    """Tests for /api/v1/system/status endpoint."""

    def test_system_status_requires_authentication(self, client):
        """Test system status endpoint requires authentication."""
        response = client.get("/api/v1/system/status")
        assert response.status_code == 401

    def test_system_status_success(self, client, auth_headers):
        """Test system status returns correct structure."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "operational"

        # Check workers section
        assert "workers" in data
        assert "file_watcher" in data["workers"]
        assert "background_workers" in data["workers"]
        assert "backup_scheduler" in data["workers"]

        # Check songs section
        assert "songs" in data
        assert "total" in data["songs"]
        assert "by_status" in data["songs"]

        # Check tasks section
        assert "tasks" in data
        assert "total" in data["tasks"]
        assert "by_status" in data["tasks"]

    def test_system_status_song_counts_empty_db(self, client, auth_headers):
        """Test system status song counts with empty database."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["songs"]["total"] == 0
        assert data["songs"]["by_status"]["pending"] == 0
        assert data["songs"]["by_status"]["uploading"] == 0
        assert data["songs"]["by_status"]["generating"] == 0

    def test_system_status_with_songs(
        self, client, auth_headers, song_factory
    ):
        """Test system status correctly counts songs by status."""
        # Create songs with different statuses
        song_factory(song_id="song-1", status="pending")
        song_factory(song_id="song-2", status="pending")
        song_factory(song_id="song-3", status="generating")
        song_factory(song_id="song-4", status="uploaded")
        song_factory(song_id="song-5", status="failed")

        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["songs"]["total"] == 5
        assert data["songs"]["by_status"]["pending"] == 2
        assert data["songs"]["by_status"]["generating"] == 1
        assert data["songs"]["by_status"]["uploaded"] == 1
        assert data["songs"]["by_status"]["failed"] == 1

    def test_system_status_with_tasks(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test system status correctly counts tasks by status."""
        # Create a song for task association
        song = song_factory(song_id="song-for-tasks")

        # Create tasks with different statuses
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="running")
        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="failed")

        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["tasks"]["total"] == 5
        assert data["tasks"]["by_status"]["pending"] == 2
        assert data["tasks"]["by_status"]["running"] == 1
        assert data["tasks"]["by_status"]["completed"] == 1
        assert data["tasks"]["by_status"]["failed"] == 1

    def test_system_status_task_counts_empty_db(self, client, auth_headers):
        """Test system status task counts with empty database."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["tasks"]["total"] == 0
        assert data["tasks"]["by_status"]["pending"] == 0
        assert data["tasks"]["by_status"]["running"] == 0
        assert data["tasks"]["by_status"]["completed"] == 0
        assert data["tasks"]["by_status"]["failed"] == 0

    def test_system_status_all_song_statuses(
        self, client, auth_headers, song_factory
    ):
        """Test system status returns all expected song status keys."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        expected_statuses = [
            "pending",
            "uploading",
            "generating",
            "downloaded",
            "evaluated",
            "uploaded",
            "failed",
        ]

        for status in expected_statuses:
            assert status in data["songs"]["by_status"]

    def test_system_status_all_task_statuses(self, client, auth_headers):
        """Test system status returns all expected task status keys."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        expected_statuses = ["pending", "running", "completed", "failed"]

        for status in expected_statuses:
            assert status in data["tasks"]["by_status"]

    def test_system_status_worker_status(self, client, auth_headers):
        """Test system status shows worker statuses."""
        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["workers"]["file_watcher"] == "running"
        assert data["workers"]["background_workers"] == "running"
        assert data["workers"]["backup_scheduler"] == "running"

    def test_system_status_with_admin(self, client, admin_auth_headers):
        """Test system status with admin user."""
        response = client.get("/api/v1/system/status", headers=admin_auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "operational"

    def test_system_status_invalid_token(self, client, expired_token):
        """Test system status with expired token."""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/system/status", headers=headers)
        assert response.status_code == 401


class TestSystemStatusDataIntegrity:
    """Tests for system status data integrity."""

    def test_song_total_matches_sum_of_statuses(
        self, client, auth_headers, song_factory
    ):
        """Test total songs equals sum of all status counts."""
        # Create various songs
        song_factory(song_id="s1", status="pending")
        song_factory(song_id="s2", status="generating")
        song_factory(song_id="s3", status="uploaded")

        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        total = data["songs"]["total"]
        status_sum = sum(data["songs"]["by_status"].values())

        assert total == status_sum

    def test_task_total_matches_sum_of_statuses(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test total tasks equals sum of all status counts."""
        song = song_factory(song_id="task-song")

        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="running")
        task_factory(song_id=song.id, status="completed")

        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        total = data["tasks"]["total"]
        status_sum = sum(data["tasks"]["by_status"].values())

        assert total == status_sum


class TestSystemStatusEdgeCases:
    """Edge case tests for system status endpoint."""

    def test_system_status_large_counts(
        self, client, auth_headers, test_db
    ):
        """Test system status handles large song counts."""
        # Create many songs efficiently using bulk insert
        songs = [
            Song(
                id=f"bulk-song-{i}",
                title=f"Bulk Song {i}",
                genre="Pop",
                style_prompt="Test prompt",
                lyrics="Test lyrics",
                file_path=f"/path/to/song{i}.md",
                status="pending",
            )
            for i in range(50)
        ]
        test_db.add_all(songs)
        test_db.commit()

        response = client.get("/api/v1/system/status", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["songs"]["total"] == 50
        assert data["songs"]["by_status"]["pending"] == 50

    def test_system_status_concurrent_requests(self, client, auth_headers):
        """Test system status handles concurrent requests."""
        import concurrent.futures

        def make_request():
            return client.get("/api/v1/system/status", headers=auth_headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(r.status_code == 200 for r in results)
