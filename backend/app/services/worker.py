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
from app.models.task_queue import TaskQueue

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
        """Execute Suno upload task (Phase 3 placeholder).

        Args:
            task: Task containing song_id to upload
            db: Database session
        """
        logger.info(f"[PLACEHOLDER] Suno upload for song {task.song_id}")

        # Update song status
        if task.song_id:
            result = await db.execute(select(Song).where(Song.id == task.song_id))
            song = result.scalar_one_or_none()
            if song:
                song.status = "uploading"
                await db.commit()
                logger.info(f"Updated song {song.id} status to 'uploading'")

        # Simulate work
        await asyncio.sleep(2)

        # Real implementation will be added in Phase 3:
        # - Initialize Playwright browser
        # - Login to Suno
        # - Upload style prompt and lyrics
        # - Get job ID
        # - Create SunoJob record
        # - Queue suno_download task

    async def execute_suno_download(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute Suno download task (Phase 3 placeholder).

        Args:
            task: Task containing song_id to download
            db: Database session
        """
        logger.info(f"[PLACEHOLDER] Suno download for song {task.song_id}")

        # Simulate work
        await asyncio.sleep(2)

        # Real implementation will be added in Phase 3:
        # - Poll Suno for generation status
        # - When ready, download audio file
        # - Save to downloads folder
        # - Update SunoJob record
        # - Update song status to 'downloaded'
        # - Queue evaluation task

    async def execute_evaluation(self, task: TaskQueue, db: AsyncSession) -> None:
        """Execute evaluation task (Phase 4 placeholder).

        Args:
            task: Task containing song_id to evaluate
            db: Database session
        """
        logger.info(f"[PLACEHOLDER] Evaluation for song {task.song_id}")

        # Simulate work
        await asyncio.sleep(1)

        # Real implementation will be added in Phase 4:
        # - Load audio file
        # - Check audio quality metrics
        # - Verify lyrics match (if possible)
        # - Calculate quality score
        # - Create Evaluation record
        # - Update song status to 'evaluated'
        # - If score is high enough, queue YouTube upload

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
