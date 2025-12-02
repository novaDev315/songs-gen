"""Integration tests for analytics API endpoints."""

import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.song import Song
from app.models.evaluation import Evaluation
from app.models.task_queue import TaskQueue
from app.models.youtube_upload import YouTubeUpload


class TestOverviewStatsEndpoint:
    """Tests for /api/v1/analytics/overview endpoint."""

    def test_overview_requires_authentication(self, client):
        """Test overview endpoint requires authentication."""
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 401

    def test_overview_success_empty_db(self, client, auth_headers):
        """Test overview returns correct structure with empty database."""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_songs"] == 0
        assert data["songs_pending"] == 0
        assert data["songs_uploaded"] == 0
        assert data["songs_failed"] == 0
        assert data["total_youtube_uploads"] == 0
        assert data["youtube_success_rate"] == 0
        assert data["average_quality_score"] == 0
        assert data["songs_created_today"] == 0
        assert data["songs_created_this_week"] == 0

    def test_overview_with_songs(self, client, auth_headers, song_factory):
        """Test overview correctly counts songs."""
        # Create songs with different statuses
        song_factory(song_id="song-1", status="pending")
        song_factory(song_id="song-2", status="uploaded")
        song_factory(song_id="song-3", status="uploaded")
        song_factory(song_id="song-4", status="failed")

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_songs"] == 4
        assert data["songs_pending"] == 1
        assert data["songs_uploaded"] == 2
        assert data["songs_failed"] == 1

    def test_overview_youtube_success_rate(
        self, client, auth_headers, song_factory, youtube_upload_factory
    ):
        """Test overview calculates YouTube success rate correctly."""
        song = song_factory(song_id="yt-song")

        # Create YouTube uploads with different statuses
        youtube_upload_factory(song_id=song.id, upload_status="completed")
        youtube_upload_factory(song_id=song.id, upload_status="completed")
        youtube_upload_factory(song_id=song.id, upload_status="failed")
        youtube_upload_factory(song_id=song.id, upload_status="pending")

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["total_youtube_uploads"] == 4
        # 2 completed out of 4 = 50%
        assert data["youtube_success_rate"] == 50.0

    def test_overview_average_quality_score(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test overview calculates average quality score correctly."""
        song1 = song_factory(song_id="eval-song-1")
        song2 = song_factory(song_id="eval-song-2")

        # Create evaluations with different scores
        evaluation_factory(song_id=song1.id, audio_quality_score=80.0)
        evaluation_factory(song_id=song2.id, audio_quality_score=90.0)

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        # Average of 80 and 90 = 85
        assert data["average_quality_score"] == 85.0

    def test_overview_songs_created_today(
        self, client, auth_headers, test_db
    ):
        """Test overview counts songs created today."""
        now = datetime.now(timezone.utc)

        # Create a song with today's date
        song = Song(
            id="today-song",
            title="Today Song",
            genre="Pop",
            style_prompt="Test",
            lyrics="Test",
            file_path="/path/to/song.md",
            status="pending",
            created_at=now,
        )
        test_db.add(song)
        test_db.commit()

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["songs_created_today"] >= 1

    def test_overview_songs_created_this_week(
        self, client, auth_headers, test_db
    ):
        """Test overview counts songs created this week."""
        now = datetime.now(timezone.utc)

        # Create songs within the week
        for i in range(3):
            song = Song(
                id=f"week-song-{i}",
                title=f"Week Song {i}",
                genre="Pop",
                style_prompt="Test",
                lyrics="Test",
                file_path=f"/path/to/song{i}.md",
                status="pending",
                created_at=now - timedelta(days=i),
            )
            test_db.add(song)
        test_db.commit()

        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["songs_created_this_week"] >= 3


class TestSongsOverTimeEndpoint:
    """Tests for /api/v1/analytics/songs-over-time endpoint."""

    def test_songs_over_time_requires_authentication(self, client):
        """Test songs-over-time endpoint requires authentication."""
        response = client.get("/api/v1/analytics/songs-over-time")
        assert response.status_code == 401

    def test_songs_over_time_default_period(self, client, auth_headers):
        """Test songs-over-time returns 30 days by default."""
        response = client.get(
            "/api/v1/analytics/songs-over-time", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "period" in data
        assert "30 days" in data["period"]
        # Should have 31 days of data (including today)
        assert len(data["data"]) == 31

    def test_songs_over_time_custom_days(self, client, auth_headers):
        """Test songs-over-time with custom days parameter."""
        response = client.get(
            "/api/v1/analytics/songs-over-time?days=7", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "7 days" in data["period"]
        assert len(data["data"]) == 8  # 7 days + today

    def test_songs_over_time_with_data(
        self, client, auth_headers, test_db
    ):
        """Test songs-over-time returns correct counts."""
        now = datetime.now(timezone.utc)

        # Create songs on different days
        for i in range(5):
            song = Song(
                id=f"time-song-{i}",
                title=f"Time Song {i}",
                genre="Pop",
                style_prompt="Test",
                lyrics="Test",
                file_path=f"/path/to/song{i}.md",
                status="pending",
                created_at=now - timedelta(days=i),
            )
            test_db.add(song)
        test_db.commit()

        response = client.get(
            "/api/v1/analytics/songs-over-time?days=7", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 5

    def test_songs_over_time_fills_missing_dates(self, client, auth_headers):
        """Test songs-over-time fills in dates with zero counts."""
        response = client.get(
            "/api/v1/analytics/songs-over-time?days=7", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # All dates should be present, even with zero counts
        for item in data["data"]:
            assert "date" in item
            assert "count" in item
            assert isinstance(item["count"], int)

    def test_songs_over_time_invalid_days(self, client, auth_headers):
        """Test songs-over-time rejects invalid days parameter."""
        # Too few days
        response = client.get(
            "/api/v1/analytics/songs-over-time?days=0", headers=auth_headers
        )
        assert response.status_code == 422

        # Too many days
        response = client.get(
            "/api/v1/analytics/songs-over-time?days=400", headers=auth_headers
        )
        assert response.status_code == 422


class TestGenreStatsEndpoint:
    """Tests for /api/v1/analytics/genre-stats endpoint."""

    def test_genre_stats_requires_authentication(self, client):
        """Test genre-stats endpoint requires authentication."""
        response = client.get("/api/v1/analytics/genre-stats")
        assert response.status_code == 401

    def test_genre_stats_empty_db(self, client, auth_headers):
        """Test genre-stats returns empty list with empty database."""
        response = client.get("/api/v1/analytics/genre-stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "genres" in data
        assert data["genres"] == []

    def test_genre_stats_with_songs(
        self, client, auth_headers, song_factory
    ):
        """Test genre-stats returns correct counts per genre."""
        # Create songs with different genres
        song_factory(song_id="pop-1", genre="Pop")
        song_factory(song_id="pop-2", genre="Pop")
        song_factory(song_id="rock-1", genre="Rock")
        song_factory(song_id="jazz-1", genre="Jazz")

        response = client.get("/api/v1/analytics/genre-stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        genres = {g["genre"]: g for g in data["genres"]}

        assert "Pop" in genres
        assert genres["Pop"]["count"] == 2
        assert "Rock" in genres
        assert genres["Rock"]["count"] == 1
        assert "Jazz" in genres
        assert genres["Jazz"]["count"] == 1

    def test_genre_stats_average_score(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test genre-stats calculates average scores correctly."""
        song1 = song_factory(song_id="pop-scored-1", genre="Pop")
        song2 = song_factory(song_id="pop-scored-2", genre="Pop")

        evaluation_factory(song_id=song1.id, audio_quality_score=80.0)
        evaluation_factory(song_id=song2.id, audio_quality_score=90.0)

        response = client.get("/api/v1/analytics/genre-stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        pop_stats = next((g for g in data["genres"] if g["genre"] == "Pop"), None)

        assert pop_stats is not None
        assert pop_stats["average_score"] == 85.0

    def test_genre_stats_success_rate(
        self, client, auth_headers, song_factory
    ):
        """Test genre-stats calculates success rate correctly."""
        # Create Pop songs with different statuses
        song_factory(song_id="pop-uploaded", genre="Pop", status="uploaded")
        song_factory(song_id="pop-pending", genre="Pop", status="pending")

        response = client.get("/api/v1/analytics/genre-stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        pop_stats = next((g for g in data["genres"] if g["genre"] == "Pop"), None)

        assert pop_stats is not None
        # 1 uploaded out of 2 = 50%
        assert pop_stats["success_rate"] == 50.0


class TestStatusDistributionEndpoint:
    """Tests for /api/v1/analytics/status-distribution endpoint."""

    def test_status_distribution_requires_authentication(self, client):
        """Test status-distribution endpoint requires authentication."""
        response = client.get("/api/v1/analytics/status-distribution")
        assert response.status_code == 401

    def test_status_distribution_empty_db(self, client, auth_headers):
        """Test status-distribution returns empty with empty database."""
        response = client.get(
            "/api/v1/analytics/status-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert data["statuses"] == []

    def test_status_distribution_with_songs(
        self, client, auth_headers, song_factory
    ):
        """Test status-distribution returns correct distribution."""
        # Create songs with different statuses
        song_factory(song_id="s1", status="pending")
        song_factory(song_id="s2", status="pending")
        song_factory(song_id="s3", status="uploaded")
        song_factory(song_id="s4", status="failed")

        response = client.get(
            "/api/v1/analytics/status-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 4

        status_map = {s["status"]: s for s in data["statuses"]}

        assert status_map["pending"]["count"] == 2
        assert status_map["pending"]["percentage"] == 50.0
        assert status_map["uploaded"]["count"] == 1
        assert status_map["uploaded"]["percentage"] == 25.0


class TestQualityDistributionEndpoint:
    """Tests for /api/v1/analytics/quality-distribution endpoint."""

    def test_quality_distribution_requires_authentication(self, client):
        """Test quality-distribution endpoint requires authentication."""
        response = client.get("/api/v1/analytics/quality-distribution")
        assert response.status_code == 401

    def test_quality_distribution_empty_db(self, client, auth_headers):
        """Test quality-distribution returns zeros with empty database."""
        response = client.get(
            "/api/v1/analytics/quality-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["distribution"] == []
        assert data["average"] == 0
        assert data["median"] == 0

    def test_quality_distribution_with_evaluations(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test quality-distribution returns correct distribution."""
        # Create songs with various quality scores
        scores = [15, 35, 55, 75, 85, 95]
        for i, score in enumerate(scores):
            song = song_factory(song_id=f"quality-song-{i}")
            evaluation_factory(song_id=song.id, audio_quality_score=score)

        response = client.get(
            "/api/v1/analytics/quality-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["distribution"]) == 5  # 5 ranges

        # Check ranges exist
        ranges = [d["range"] for d in data["distribution"]]
        assert "0-20" in ranges
        assert "20-40" in ranges
        assert "40-60" in ranges
        assert "60-80" in ranges
        assert "80-100" in ranges

    def test_quality_distribution_average_and_median(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test quality-distribution calculates average and median correctly."""
        # Create evaluations with known scores
        scores = [60, 70, 80, 90, 100]
        for i, score in enumerate(scores):
            song = song_factory(song_id=f"avg-song-{i}")
            evaluation_factory(song_id=song.id, audio_quality_score=score)

        response = client.get(
            "/api/v1/analytics/quality-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # Average of 60, 70, 80, 90, 100 = 80
        assert data["average"] == 80.0
        # Median of 5 sorted values = middle value = 80
        assert data["median"] == 80.0


class TestPipelineMetricsEndpoint:
    """Tests for /api/v1/analytics/pipeline-metrics endpoint."""

    def test_pipeline_metrics_requires_authentication(self, client):
        """Test pipeline-metrics endpoint requires authentication."""
        response = client.get("/api/v1/analytics/pipeline-metrics")
        assert response.status_code == 401

    def test_pipeline_metrics_empty_db(self, client, auth_headers):
        """Test pipeline-metrics returns zeros with empty database."""
        response = client.get(
            "/api/v1/analytics/pipeline-metrics", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["average_processing_time_minutes"] == 0
        assert data["success_rate"] == 0
        assert data["retry_rate"] == 0
        assert data["tasks_in_queue"] == 0
        assert data["tasks_running"] == 0
        assert data["tasks_failed_today"] == 0

    def test_pipeline_metrics_task_counts(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test pipeline-metrics counts tasks correctly."""
        song = song_factory(song_id="pipeline-song")

        # Create tasks with different statuses
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="pending")
        task_factory(song_id=song.id, status="running")

        response = client.get(
            "/api/v1/analytics/pipeline-metrics", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["tasks_in_queue"] == 2
        assert data["tasks_running"] == 1

    def test_pipeline_metrics_success_rate(
        self, client, auth_headers, song_factory, task_factory
    ):
        """Test pipeline-metrics calculates success rate correctly."""
        song = song_factory(song_id="success-song")

        # Create completed and failed tasks
        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="completed")
        task_factory(song_id=song.id, status="failed")

        response = client.get(
            "/api/v1/analytics/pipeline-metrics", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # 3 completed out of 4 = 75%
        assert data["success_rate"] == 75.0

    def test_pipeline_metrics_retry_rate(
        self, client, auth_headers, song_factory, test_db
    ):
        """Test pipeline-metrics calculates retry rate correctly."""
        song = song_factory(song_id="retry-song")

        # Create tasks with and without retries
        task_no_retry = TaskQueue(
            song_id=song.id,
            task_type="generate",
            status="completed",
            retry_count=0,
        )
        task_with_retry = TaskQueue(
            song_id=song.id,
            task_type="generate",
            status="completed",
            retry_count=2,
        )
        test_db.add_all([task_no_retry, task_with_retry])
        test_db.commit()

        response = client.get(
            "/api/v1/analytics/pipeline-metrics", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        # 1 task with retries out of 2 = 50%
        assert data["retry_rate"] == 50.0


class TestDashboardSummaryEndpoint:
    """Tests for /api/v1/analytics/dashboard endpoint."""

    def test_dashboard_requires_authentication(self, client):
        """Test dashboard endpoint requires authentication."""
        response = client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 401

    def test_dashboard_success(self, client, auth_headers):
        """Test dashboard returns all data in single request."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert "overview" in data
        assert "songs_by_day" in data
        assert "status_distribution" in data
        assert "genre_stats" in data
        assert "pipeline_metrics" in data

    def test_dashboard_overview_structure(self, client, auth_headers):
        """Test dashboard overview has correct structure."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200

        overview = response.json()["overview"]
        assert "total_songs" in overview
        assert "songs_pending" in overview
        assert "songs_uploaded" in overview
        assert "songs_failed" in overview
        assert "total_youtube_uploads" in overview
        assert "youtube_success_rate" in overview
        assert "average_quality_score" in overview

    def test_dashboard_songs_by_day_structure(self, client, auth_headers):
        """Test dashboard songs_by_day has correct structure."""
        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200

        songs_by_day = response.json()["songs_by_day"]
        assert isinstance(songs_by_day, list)
        # Should have 14 days of data (dashboard uses 14 days)
        # Each item should have date and count
        for item in songs_by_day:
            assert "date" in item
            assert "count" in item

    def test_dashboard_with_data(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test dashboard returns correct data."""
        # Create some test data
        song1 = song_factory(song_id="dash-song-1", genre="Pop", status="uploaded")
        song2 = song_factory(song_id="dash-song-2", genre="Rock", status="pending")
        evaluation_factory(song_id=song1.id, audio_quality_score=80.0)

        response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["overview"]["total_songs"] == 2
        assert data["overview"]["songs_uploaded"] == 1
        assert data["overview"]["songs_pending"] == 1
        assert len(data["genre_stats"]) == 2


class TestAnalyticsEdgeCases:
    """Edge case tests for analytics endpoints."""

    def test_overview_with_zero_youtube_uploads(
        self, client, auth_headers
    ):
        """Test overview handles division by zero for YouTube success rate."""
        response = client.get("/api/v1/analytics/overview", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        assert data["youtube_success_rate"] == 0

    def test_quality_distribution_single_score(
        self, client, auth_headers, song_factory, evaluation_factory
    ):
        """Test quality-distribution handles single data point."""
        song = song_factory(song_id="single-song")
        evaluation_factory(song_id=song.id, audio_quality_score=75.0)

        response = client.get(
            "/api/v1/analytics/quality-distribution", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["average"] == 75.0
        assert data["median"] == 75.0

    def test_genre_stats_no_evaluations(
        self, client, auth_headers, song_factory
    ):
        """Test genre-stats handles songs with no evaluations."""
        song_factory(song_id="no-eval-song", genre="Pop")

        response = client.get("/api/v1/analytics/genre-stats", headers=auth_headers)
        assert response.status_code == 200

        data = response.json()
        pop_stats = next((g for g in data["genres"] if g["genre"] == "Pop"), None)
        assert pop_stats is not None
        assert pop_stats["average_score"] == 0
