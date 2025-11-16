"""Background worker system to process task queue."""

import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.task_queue import TaskQueue
from app.services.download_manager import get_download_manager
from app.services.evaluator import get_evaluator
from app.services.suno_client import get_suno_client, SunoClientError

logger = logging.getLogger(__name__)
settings = get_settings()


class BackgroundWorker:
    """Background worker to process queued tasks."""

    def __init__(self, worker_id: int) -> None:
        """Initialize the worker.

        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id
        self.running = False
        self.current_task: TaskQueue | None = None

    async def start(self) -> None:
        """Start the worker and begin processing tasks."""
        self.running = True
        logger.info(f"Worker {self.worker_id} started")

        while self.running:
            try:
                await self.process_next_task()
                await asyncio.sleep(settings.WORKER_CHECK_INTERVAL)
            except Exception as e:
                logger.error(
                    f"Worker {self.worker_id} encountered error: {e}",
                    exc_info=True,
                )
                # Brief pause on error to prevent tight error loop
                await asyncio.sleep(5)

    async def stop(self) -> None:
        """Stop the worker gracefully."""
        self.running = False
        logger.info(f"Worker {self.worker_id} stopped")

    async def process_next_task(self) -> None:
        """Get and process the next pending task from the queue."""
        async with AsyncSessionLocal() as db:
            # Get highest priority pending task with row lock
            result = await db.execute(
                select(TaskQueue)
                .where(TaskQueue.status == "pending")
                .order_by(
                    TaskQueue.priority.desc(),
                    TaskQueue.created_at.asc(),
                )
                .limit(1)
                .with_for_update(skip_locked=True)  # Lock row, skip if locked
            )
            task = result.scalar_one_or_none()

            if not task:
                return  # No pending tasks available

            # Mark task as running
            task.status = "running"
            task.started_at = datetime.utcnow()
            await db.commit()

            logger.info(
                f"Worker {self.worker_id} processing task {task.id}: {task.task_type}"
            )

            try:
                # Execute the task based on its type
                await self.execute_task(task, db)

                # Mark task as completed
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                await db.commit()

                logger.info(f"Task {task.id} completed successfully")

            except Exception as e:
                # Handle task failure
                task.retry_count += 1
                task.error_message = str(e)

                if task.retry_count >= task.max_retries:
                    # Max retries reached, mark as failed
                    task.status = "failed"
                    task.completed_at = datetime.utcnow()
                    logger.error(
                        f"Task {task.id} failed after {task.retry_count} retries: {e}"
                    )
                else:
                    # Retry the task
                    task.status = "pending"
                    task.started_at = None
                    logger.warning(
                        f"Task {task.id} failed, will retry "
                        f"({task.retry_count}/{task.max_retries}): {e}"
                    )

                await db.commit()

    async def execute_task(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute a task based on its type.

        Args:
            task: The task to execute
            db: Database session for persistence

        Raises:
            ValueError: If task type is unknown
        """
        if task.task_type == "suno_upload":
            await self.execute_suno_upload(task, db)

        elif task.task_type == "suno_download":
            await self.execute_suno_download(task, db)

        elif task.task_type == "evaluate":
            await self.execute_evaluation(task, db)

        elif task.task_type == "youtube_upload":
            await self.execute_youtube_upload(task, db)

        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

    async def execute_suno_upload(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute Suno upload task.

        Uploads song to Suno.com for generation using Playwright automation.

        ⚠️ WARNING: Verify Suno ToS compliance before enabling!
        See backend/SUNO_INTEGRATION_WARNING.md

        Args:
            task: Task containing song_id to upload
            db: Database session

        Raises:
            ValueError: If song not found
            SunoClientError: If upload fails
        """
        logger.info(f"Uploading song {task.song_id} to Suno")

        # Get song
        result = await db.execute(select(Song).where(Song.id == task.song_id))
        song = result.scalar_one_or_none()

        if not song:
            raise ValueError(f"Song not found: {task.song_id}")

        # Update song status to uploading
        song.status = "uploading"
        await db.commit()

        try:
            # Get Suno client (singleton instance)
            suno_client = await get_suno_client()

            # Upload to Suno
            logger.info(
                f"Uploading to Suno: {song.title} (style: {song.style_prompt[:50] if song.style_prompt else 'none'}...)"
            )
            result = await suno_client.upload_song(
                style_prompt=song.style_prompt or "",
                lyrics=song.lyrics or "",
                title=song.title,
            )

            logger.info(f"Suno upload result: {result}")

            # Create or update Suno job record
            suno_result = await db.execute(
                select(SunoJob).where(SunoJob.song_id == task.song_id)
            )
            suno_job = suno_result.scalar_one_or_none()

            if suno_job:
                # Update existing job
                suno_job.suno_job_id = result["job_id"]
                suno_job.status = "processing"
                suno_job.error_message = None
            else:
                # Create new job
                suno_job = SunoJob(
                    song_id=task.song_id,
                    suno_job_id=result["job_id"],
                    status="processing",
                )
                db.add(suno_job)

            await db.commit()

            # Update song status to generating
            song.status = "generating"
            await db.commit()

            # Create task to check status and download
            # Use higher priority to check status soon
            check_task = TaskQueue(
                task_type="suno_download",
                song_id=task.song_id,
                priority=task.priority + 1,  # Higher priority than original
                status="pending",
            )
            db.add(check_task)
            await db.commit()

            logger.info(
                f"Suno upload successful: {task.song_id} -> job {result['job_id']}"
            )

        except SunoClientError as e:
            # Suno-specific error
            logger.error(f"Suno upload failed for {task.song_id}: {e}")
            song.status = "failed"
            await db.commit()
            raise

        except Exception as e:
            # Unexpected error
            logger.error(
                f"Unexpected error during Suno upload for {task.song_id}: {e}",
                exc_info=True,
            )
            song.status = "failed"
            await db.commit()
            raise

    async def execute_suno_download(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute Suno download task.

        Checks Suno job status and downloads audio if ready.
        If still processing, re-queues the task for later retry.

        Args:
            task: Task containing song_id to download
            db: Database session

        Raises:
            ValueError: If no Suno job found for song
            SunoClientError: If status check fails
        """
        logger.info(f"Checking Suno status and downloading song {task.song_id}")

        # Get most recent Suno job for this song
        result = await db.execute(
            select(SunoJob)
            .where(SunoJob.song_id == task.song_id)
            .order_by(SunoJob.created_at.desc())
            .limit(1)
        )
        suno_job = result.scalar_one_or_none()

        if not suno_job:
            raise ValueError(f"No Suno job found for song {task.song_id}")

        # Check status with Suno
        try:
            suno_client = await get_suno_client()
            status_result = await suno_client.check_status(suno_job.suno_job_id)

            logger.info(
                f"Suno job {suno_job.suno_job_id} status: {status_result['status']}"
            )

            if status_result["status"] == "processing":
                # Still processing, re-queue for later
                logger.info(
                    f"Song {task.song_id} still processing, will retry in next worker cycle"
                )
                # Raise exception to trigger retry logic
                raise Exception(
                    "Song still processing in Suno, will retry automatically"
                )

            elif status_result["status"] == "completed":
                # Update Suno job with completion details
                suno_job.status = "completed"
                suno_job.audio_url = status_result.get("audio_url")
                suno_job.completed_at = datetime.utcnow()
                await db.commit()

                logger.info(
                    f"Suno generation completed for {task.song_id}, starting download"
                )

                # Download audio using download manager
                download_manager = get_download_manager()
                file_path = await download_manager.download_from_suno_job(suno_job.id)

                logger.info(f"Download complete: {file_path}")

                # Update song status
                song_result = await db.execute(
                    select(Song).where(Song.id == task.song_id)
                )
                song = song_result.scalar_one_or_none()
                if song:
                    song.status = "downloaded"
                    await db.commit()

                # Create evaluation task
                eval_task = TaskQueue(
                    task_type="evaluate",
                    song_id=task.song_id,
                    priority=task.priority,
                    status="pending",
                )
                db.add(eval_task)
                await db.commit()

                logger.info(f"Evaluation task queued for song {task.song_id}")

            elif status_result["status"] == "failed":
                # Suno generation failed
                error_msg = status_result.get("error", "Unknown error from Suno")
                logger.error(f"Suno generation failed for {task.song_id}: {error_msg}")

                # Update Suno job
                suno_job.status = "failed"
                suno_job.error_message = error_msg
                suno_job.completed_at = datetime.utcnow()
                await db.commit()

                # Update song status
                song_result = await db.execute(
                    select(Song).where(Song.id == task.song_id)
                )
                song = song_result.scalar_one_or_none()
                if song:
                    song.status = "failed"
                    await db.commit()

                raise Exception(f"Suno generation failed: {error_msg}")

            else:
                # Unknown status
                logger.warning(
                    f"Unknown Suno status for {task.song_id}: {status_result['status']}"
                )
                raise Exception(f"Unknown Suno status: {status_result['status']}")

        except SunoClientError as e:
            logger.error(f"Suno client error for {task.song_id}: {e}")
            raise

        except Exception as e:
            # Let worker retry logic handle it
            logger.warning(f"Error checking/downloading {task.song_id}: {e}")
            raise

    async def execute_evaluation(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute evaluation task.

        Args:
            task: Task containing song_id to evaluate
            db: Database session
        """
        logger.info(f"Evaluating song {task.song_id}")

        # Evaluate using evaluator service
        evaluator = get_evaluator()
        evaluation = await evaluator.evaluate_song(task.song_id)

        logger.info(
            f"Evaluation complete: {task.song_id} (score: {evaluation.audio_quality_score})"
        )

        # If auto-approved, create YouTube upload task
        if evaluation.approved:
            youtube_task = TaskQueue(
                task_type="youtube_upload",
                song_id=task.song_id,
                priority=task.priority,
                status="pending",
            )
            db.add(youtube_task)
            await db.commit()
            logger.info(f"Song approved, YouTube upload task created: {task.song_id}")

    async def execute_youtube_upload(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute YouTube upload task (Phase 5 placeholder).

        Args:
            task: Task containing song_id to upload
            db: Database session
        """
        logger.info(f"[PLACEHOLDER] YouTube upload for song {task.song_id}")

        # Simulate work
        await asyncio.sleep(2)

        # Real implementation will be added in Phase 5:
        # - Get OAuth2 credentials
        # - Prepare video from audio + static image
        # - Upload to YouTube with metadata
        # - Get video URL
        # - Create YouTubeUpload record
        # - Update song status to 'uploaded'


class WorkerPool:
    """Pool of background workers to process tasks concurrently."""

    def __init__(self, num_workers: int = 2) -> None:
        """Initialize the worker pool.

        Args:
            num_workers: Number of concurrent workers to run
        """
        self.num_workers = num_workers
        self.workers: list[BackgroundWorker] = []
        self.tasks: list[asyncio.Task[Any]] = []

    async def start(self) -> None:
        """Start all workers in the pool."""
        for i in range(self.num_workers):
            worker = BackgroundWorker(worker_id=i)
            self.workers.append(worker)
            task = asyncio.create_task(worker.start())
            self.tasks.append(task)

        logger.info(f"Worker pool started with {self.num_workers} workers")

    async def stop(self) -> None:
        """Stop all workers gracefully."""
        # Signal all workers to stop
        for worker in self.workers:
            await worker.stop()

        # Wait for all worker tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)

        logger.info("Worker pool stopped")


# Global instance
_worker_pool: WorkerPool | None = None


def get_worker_pool() -> WorkerPool:
    """Get the global worker pool instance.

    Returns:
        The singleton WorkerPool instance
    """
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool(num_workers=settings.WORKER_COUNT)
    return _worker_pool
