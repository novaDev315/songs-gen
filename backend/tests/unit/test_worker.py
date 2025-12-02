"""Unit tests for background worker service.

Tests for background task processing and worker pool management.
"""

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock, PropertyMock

import pytest

from app.services.worker import (
    BackgroundWorker,
    WorkerPool,
    get_worker_pool,
)
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.task_queue import TaskQueue
from app.models.evaluation import Evaluation
from app.models.youtube_upload import YouTubeUpload


@pytest.mark.unit
class TestBackgroundWorker:
    """Test BackgroundWorker class."""

    def test_init_sets_worker_id(self):
        """Test that initialization sets worker ID correctly."""
        worker = BackgroundWorker(worker_id=5)

        assert worker.worker_id == 5
        assert worker.running is False
        assert worker.current_task is None

    def test_init_with_different_ids(self):
        """Test workers can be created with different IDs."""
        worker1 = BackgroundWorker(worker_id=0)
        worker2 = BackgroundWorker(worker_id=1)

        assert worker1.worker_id != worker2.worker_id


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerLifecycle:
    """Test BackgroundWorker lifecycle methods."""

    async def test_start_sets_running_flag(self):
        """Test that start sets running flag."""
        worker = BackgroundWorker(worker_id=0)

        with patch.object(worker, 'process_next_task', new_callable=AsyncMock) as mock_process:
            # Make process_next_task stop the worker after first call
            async def stop_after_first():
                worker.running = False

            mock_process.side_effect = stop_after_first

            with patch('app.services.worker.settings') as mock_settings:
                mock_settings.WORKER_CHECK_INTERVAL = 0.01

                await worker.start()

                assert mock_process.called

    async def test_stop_clears_running_flag(self):
        """Test that stop clears running flag."""
        worker = BackgroundWorker(worker_id=0)
        worker.running = True

        await worker.stop()

        assert worker.running is False

    async def test_start_handles_errors_gracefully(self):
        """Test that start handles errors and continues."""
        worker = BackgroundWorker(worker_id=0)
        call_count = 0

        async def error_then_stop():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            worker.running = False

        with patch.object(worker, 'process_next_task', new_callable=AsyncMock) as mock_process:
            mock_process.side_effect = error_then_stop

            with patch('app.services.worker.settings') as mock_settings:
                mock_settings.WORKER_CHECK_INTERVAL = 0.01

                await worker.start()

                # Should have been called twice (error, then success)
                assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerProcessNextTask:
    """Test BackgroundWorker.process_next_task method."""

    async def test_process_next_task_no_pending_tasks(self):
        """Test processing when no pending tasks exist."""
        worker = BackgroundWorker(worker_id=0)

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # No tasks
        mock_db.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.worker.get_session_local', return_value=mock_session_local):
            await worker.process_next_task()

            # Should query but not execute any task
            mock_db.execute.assert_called_once()
            mock_db.commit.assert_not_called()

    async def test_process_next_task_executes_task(self):
        """Test processing executes a pending task."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.id = 1
        mock_task.task_type = "suno_upload"
        mock_task.song_id = "test-song-001"
        mock_task.status = "pending"
        mock_task.retry_count = 0
        mock_task.max_retries = 3

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.worker.get_session_local', return_value=mock_session_local):
            with patch.object(worker, 'execute_task', new_callable=AsyncMock) as mock_execute:
                await worker.process_next_task()

                # Verify task status was updated to running
                assert mock_task.status == "completed"
                mock_execute.assert_called_once()

    async def test_process_next_task_handles_failure(self):
        """Test processing handles task failure."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.id = 1
        mock_task.task_type = "suno_upload"
        mock_task.song_id = "test-song-001"
        mock_task.status = "pending"
        mock_task.retry_count = 0
        mock_task.max_retries = 3

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.worker.get_session_local', return_value=mock_session_local):
            with patch.object(worker, 'execute_task', new_callable=AsyncMock) as mock_execute:
                mock_execute.side_effect = Exception("Task failed")

                await worker.process_next_task()

                # Task should be marked for retry
                assert mock_task.retry_count == 1
                assert mock_task.status == "pending"
                assert "Task failed" in mock_task.error_message

    async def test_process_next_task_max_retries_reached(self):
        """Test processing marks task as failed after max retries."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.id = 1
        mock_task.task_type = "suno_upload"
        mock_task.song_id = "test-song-001"
        mock_task.status = "pending"
        mock_task.retry_count = 2  # Already at 2 retries
        mock_task.max_retries = 3

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_task
        mock_db.execute.return_value = mock_result

        mock_session_local = MagicMock()
        mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_local.return_value.__aexit__ = AsyncMock(return_value=None)

        with patch('app.services.worker.get_session_local', return_value=mock_session_local):
            with patch.object(worker, 'execute_task', new_callable=AsyncMock) as mock_execute:
                mock_execute.side_effect = Exception("Task failed again")

                await worker.process_next_task()

                # Task should be marked as failed
                assert mock_task.retry_count == 3
                assert mock_task.status == "failed"


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerExecuteTask:
    """Test BackgroundWorker.execute_task method."""

    async def test_execute_task_suno_upload(self):
        """Test execute_task routes to suno_upload handler."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.task_type = "suno_upload"
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()

        with patch.object(worker, 'execute_suno_upload', new_callable=AsyncMock) as mock_handler:
            await worker.execute_task(mock_task, mock_db)

            mock_handler.assert_called_once_with(mock_task, mock_db)

    async def test_execute_task_suno_download(self):
        """Test execute_task routes to suno_download handler."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.task_type = "suno_download"
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()

        with patch.object(worker, 'execute_suno_download', new_callable=AsyncMock) as mock_handler:
            await worker.execute_task(mock_task, mock_db)

            mock_handler.assert_called_once_with(mock_task, mock_db)

    async def test_execute_task_evaluate(self):
        """Test execute_task routes to evaluation handler."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.task_type = "evaluate"
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()

        with patch.object(worker, 'execute_evaluation', new_callable=AsyncMock) as mock_handler:
            await worker.execute_task(mock_task, mock_db)

            mock_handler.assert_called_once_with(mock_task, mock_db)

    async def test_execute_task_youtube_upload(self):
        """Test execute_task routes to youtube_upload handler."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.task_type = "youtube_upload"
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()

        with patch.object(worker, 'execute_youtube_upload', new_callable=AsyncMock) as mock_handler:
            await worker.execute_task(mock_task, mock_db)

            mock_handler.assert_called_once_with(mock_task, mock_db)

    async def test_execute_task_unknown_type(self):
        """Test execute_task raises error for unknown task type."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.task_type = "unknown_task"
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()

        with pytest.raises(ValueError, match="Unknown task type"):
            await worker.execute_task(mock_task, mock_db)


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerSunoUpload:
    """Test BackgroundWorker.execute_suno_upload method."""

    async def test_execute_suno_upload_success(self):
        """Test successful Suno upload execution."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"
        mock_task.priority = 5

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.title = "Test Song"
        mock_song.style_prompt = "Pop, upbeat"
        mock_song.lyrics = "[Verse]\nTest"
        mock_song.status = "pending"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_song
        mock_db.execute.return_value = mock_result

        mock_suno_client = AsyncMock()
        mock_suno_client.upload_song.return_value = {
            "job_id": "suno-job-123",
            "status": "processing",
        }

        with patch('app.services.worker.get_suno_client', new_callable=AsyncMock) as mock_get_client:
            mock_get_client.return_value = mock_suno_client

            await worker.execute_suno_upload(mock_task, mock_db)

            mock_suno_client.upload_song.assert_called_once()
            assert mock_song.status == "generating"

    async def test_execute_suno_upload_song_not_found(self):
        """Test Suno upload with non-existent song."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "nonexistent-song"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Song not found"):
            await worker.execute_suno_upload(mock_task, mock_db)


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerSunoDownload:
    """Test BackgroundWorker.execute_suno_download method."""

    async def test_execute_suno_download_completed(self):
        """Test Suno download when generation is completed."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"
        mock_task.priority = 5

        mock_suno_job = MagicMock(spec=SunoJob)
        mock_suno_job.id = 1
        mock_suno_job.song_id = "test-song-001"
        mock_suno_job.suno_job_id = "suno-123"
        mock_suno_job.status = "processing"

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.title = "Test Song"
        mock_song.genre = "Pop"
        mock_song.status = "generating"

        mock_db = AsyncMock()

        # First call returns suno job, second call returns song
        mock_result_job = MagicMock()
        mock_result_job.scalar_one_or_none.return_value = mock_suno_job
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_db.execute.side_effect = [mock_result_job, mock_result_song]

        mock_suno_client = AsyncMock()
        mock_suno_client.check_status.return_value = {
            "status": "completed",
            "audio_url": "https://cdn.suno.com/audio/test.mp3",
        }

        mock_download_manager = MagicMock()
        mock_download_manager.download_from_suno_job = AsyncMock(
            return_value=Path("/downloads/test.mp3")
        )

        mock_notification_service = MagicMock()
        mock_notification_service.notify_song_complete = AsyncMock()

        with patch('app.services.worker.get_suno_client', new_callable=AsyncMock) as mock_get_client:
            mock_get_client.return_value = mock_suno_client

            with patch('app.services.worker.get_download_manager', return_value=mock_download_manager):
                with patch('app.services.worker.get_notification_service', return_value=mock_notification_service):
                    await worker.execute_suno_download(mock_task, mock_db)

                    mock_suno_client.check_status.assert_called_once_with("suno-123")
                    mock_download_manager.download_from_suno_job.assert_called_once()

    async def test_execute_suno_download_still_processing(self):
        """Test Suno download when still processing."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"

        mock_suno_job = MagicMock(spec=SunoJob)
        mock_suno_job.id = 1
        mock_suno_job.suno_job_id = "suno-123"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suno_job
        mock_db.execute.return_value = mock_result

        mock_suno_client = AsyncMock()
        mock_suno_client.check_status.return_value = {
            "status": "processing",
        }

        with patch('app.services.worker.get_suno_client', new_callable=AsyncMock) as mock_get_client:
            mock_get_client.return_value = mock_suno_client

            # Should raise exception to trigger retry
            with pytest.raises(Exception, match="still processing"):
                await worker.execute_suno_download(mock_task, mock_db)

    async def test_execute_suno_download_no_job_found(self):
        """Test Suno download with no job found."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="No Suno job found"):
            await worker.execute_suno_download(mock_task, mock_db)


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerEvaluation:
    """Test BackgroundWorker.execute_evaluation method."""

    async def test_execute_evaluation_approved(self):
        """Test evaluation execution with approved result."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"
        mock_task.priority = 5

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.title = "Test Song"
        mock_song.genre = "Pop"

        mock_evaluation = MagicMock(spec=Evaluation)
        mock_evaluation.audio_quality_score = 85.0
        mock_evaluation.approved = True

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_song
        mock_db.execute.return_value = mock_result

        mock_evaluator = MagicMock()
        mock_evaluator.evaluate_song = AsyncMock(return_value=mock_evaluation)

        mock_notification_service = MagicMock()
        mock_notification_service.notify_evaluation_complete = AsyncMock()

        with patch('app.services.worker.get_evaluator', return_value=mock_evaluator):
            with patch('app.services.worker.get_notification_service', return_value=mock_notification_service):
                await worker.execute_evaluation(mock_task, mock_db)

                mock_evaluator.evaluate_song.assert_called_once_with("test-song-001")
                # Should create YouTube upload task since approved
                mock_db.add.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
class TestBackgroundWorkerYouTubeUpload:
    """Test BackgroundWorker.execute_youtube_upload method."""

    async def test_execute_youtube_upload_song_not_found(self):
        """Test YouTube upload with non-existent song."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "nonexistent-song"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="Song not found"):
            await worker.execute_youtube_upload(mock_task, mock_db)

    async def test_execute_youtube_upload_not_approved(self):
        """Test YouTube upload with non-approved song."""
        worker = BackgroundWorker(worker_id=0)

        mock_task = MagicMock(spec=TaskQueue)
        mock_task.song_id = "test-song-001"

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"

        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_eval = MagicMock()
        mock_result_eval.scalar_one_or_none.return_value = None  # No approved evaluation
        mock_db.execute.side_effect = [mock_result_song, mock_result_eval]

        with pytest.raises(ValueError, match="not approved"):
            await worker.execute_youtube_upload(mock_task, mock_db)


@pytest.mark.unit
class TestWorkerPool:
    """Test WorkerPool class."""

    def test_init_with_default_workers(self):
        """Test WorkerPool initialization with default workers."""
        pool = WorkerPool()

        assert pool.num_workers == 2
        assert pool.workers == []
        assert pool.tasks == []

    def test_init_with_custom_workers(self):
        """Test WorkerPool initialization with custom worker count."""
        pool = WorkerPool(num_workers=5)

        assert pool.num_workers == 5


@pytest.mark.unit
@pytest.mark.asyncio
class TestWorkerPoolLifecycle:
    """Test WorkerPool lifecycle methods."""

    async def test_start_creates_workers(self):
        """Test that start creates and starts workers."""
        pool = WorkerPool(num_workers=2)

        # Mock BackgroundWorker.start to be a no-op
        with patch.object(BackgroundWorker, 'start', new_callable=AsyncMock):
            # Start in background task to not block
            start_task = asyncio.create_task(pool.start())
            await asyncio.sleep(0.1)

            assert len(pool.workers) == 2
            assert len(pool.tasks) == 2

            # Clean up
            for worker in pool.workers:
                worker.running = False
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass

    async def test_stop_stops_all_workers(self):
        """Test that stop signals all workers to stop."""
        pool = WorkerPool(num_workers=2)

        # Create mock workers
        mock_worker1 = MagicMock()
        mock_worker1.stop = AsyncMock()
        mock_worker2 = MagicMock()
        mock_worker2.stop = AsyncMock()

        pool.workers = [mock_worker1, mock_worker2]
        pool.tasks = [
            asyncio.create_task(asyncio.sleep(10)),
            asyncio.create_task(asyncio.sleep(10)),
        ]

        await pool.stop()

        mock_worker1.stop.assert_called_once()
        mock_worker2.stop.assert_called_once()


@pytest.mark.unit
class TestGetWorkerPool:
    """Test get_worker_pool singleton function."""

    def test_get_worker_pool_creates_singleton(self):
        """Test that get_worker_pool creates a singleton."""
        import app.services.worker as wk
        wk._worker_pool = None

        with patch('app.services.worker.settings') as mock_settings:
            mock_settings.WORKER_COUNT = 3

            pool1 = get_worker_pool()
            pool2 = get_worker_pool()

            assert pool1 is pool2
            assert pool1.num_workers == 3

        # Clean up
        wk._worker_pool = None

    def test_get_worker_pool_returns_existing(self):
        """Test that get_worker_pool returns existing instance."""
        import app.services.worker as wk

        existing_pool = WorkerPool(num_workers=4)
        wk._worker_pool = existing_pool

        result = get_worker_pool()

        assert result is existing_pool

        # Clean up
        wk._worker_pool = None
