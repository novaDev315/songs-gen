"""Background worker for processing async tasks."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session_local
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.models.task_queue import TaskQueue
from app.models.youtube_upload import YouTubeUpload

logger = logging.getLogger(__name__)
settings = get_settings()


class BackgroundWorker:
    """Background worker for processing tasks from the queue."""

    def __init__(self, worker_id: int) -> None:
        """Initialize the worker.

        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id
        self.running = False
        self.current_task: Optional[TaskQueue] = None

    async def start(self) -> None:
        """Start the worker loop."""
        self.running = True
        logger.info(f"Worker {self.worker_id} starting")

        while self.running:
            try:
                await self.process_next_task()
            except Exception as e:
                logger.error(f"Worker {self.worker_id} error: {e}")

            # Wait before checking for next task
            await asyncio.sleep(settings.WORKER_CHECK_INTERVAL)

    async def stop(self) -> None:
        """Stop the worker."""
        self.running = False
        logger.info(f"Worker {self.worker_id} stopped")

    async def process_next_task(self) -> None:
        """Process the next pending task from the queue."""
        session_local = get_session_local()
        async with session_local() as db:
            # Get next pending task (ordered by priority desc, created_at asc)
            result = await db.execute(
                select(TaskQueue)
                .where(TaskQueue.status == "pending")
                .order_by(TaskQueue.priority.desc(), TaskQueue.created_at.asc())
                .limit(1)
            )
            task = result.scalar_one_or_none()

            if not task:
                return

            # Mark as running
            task.status = "running"
            task.started_at = datetime.utcnow()
            self.current_task = task
            await db.commit()

            logger.info(
                f"Worker {self.worker_id} processing task {task.id} "
                f"(type: {task.task_type}, song: {task.song_id})"
            )

            try:
                await self.execute_task(task, db)

                # Mark as completed
                task.status = "completed"
                task.completed_at = datetime.utcnow()
                await db.commit()

                logger.info(f"Worker {self.worker_id} completed task {task.id}")

            except Exception as e:
                logger.error(
                    f"Worker {self.worker_id} task {task.id} failed: {e}"
                )

                # Handle retry logic
                task.retry_count = (task.retry_count or 0) + 1
                task.error_message = str(e)

                if task.retry_count >= task.max_retries:
                    task.status = "failed"
                    task.completed_at = datetime.utcnow()
                    logger.error(
                        f"Task {task.id} failed after {task.retry_count} retries"
                    )
                else:
                    task.status = "pending"
                    logger.info(
                        f"Task {task.id} will be retried "
                        f"(attempt {task.retry_count}/{task.max_retries})"
                    )

                await db.commit()

            finally:
                self.current_task = None

    async def execute_task(
        self, task: TaskQueue, db: AsyncSession
    ) -> None:
        """Execute a task based on its type.

        Args:
            task: The task to execute
            db: Database session

        Raises:
            ValueError: If task type is unknown
        """
        # Suno tasks are handled by external tools (tools/suno_worker.py)
        if task.task_type in ("suno_upload", "suno_download"):
            logger.info(f"Task {task.id} ({task.task_type}) is handled by external tools")
            # Reset to pending so external worker can pick it up
            task.status = "pending"
            task.started_at = None
            await db.commit()
            return
        elif task.task_type == "evaluate":
            await self.execute_evaluation(task, db)
        elif task.task_type == "youtube_upload":
            await self.execute_youtube_upload(task, db)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")

    async def execute_evaluation(
        self, task: TaskQueue, db: AsyncSession
    ) -> None:
        """Execute evaluation task.

        Args:
            task: The task to execute
            db: Database session
        """
        from app.services.evaluator import get_evaluator
        from app.services.notification import get_notification_service

        logger.info(f"Evaluating song {task.song_id}")

        # Get song
        result = await db.execute(
            select(Song).where(Song.id == task.song_id)
        )
        song = result.scalar_one_or_none()

        if not song:
            raise ValueError(f"Song not found: {task.song_id}")

        # Run evaluation
        evaluator = get_evaluator()
        evaluation = await evaluator.evaluate_song(task.song_id)

        # Send notification
        notification_service = get_notification_service()
        await notification_service.notify_evaluation_complete(song, evaluation)

        # If approved, create YouTube upload task
        if evaluation.approved:
            youtube_task = TaskQueue(
                task_type="youtube_upload",
                song_id=task.song_id,
                status="pending",
                priority=task.priority,
            )
            db.add(youtube_task)
            await db.commit()
            logger.info(
                f"Song {task.song_id} approved - YouTube upload task created"
            )

        logger.info(f"Evaluation complete for song {task.song_id}")

    async def execute_youtube_upload(
        self, task: TaskQueue, db: AsyncSession
    ) -> None:
        """Execute YouTube upload task.

        Args:
            task: The task to execute
            db: Database session

        Raises:
            ValueError: If song not found or not approved
        """
        from app.services.notification import get_notification_service
        from app.services.video_generator import get_video_generator
        from app.services.youtube_uploader import get_youtube_uploader

        logger.info(f"Uploading song {task.song_id} to YouTube")

        # Get song
        result = await db.execute(
            select(Song).where(Song.id == task.song_id)
        )
        song = result.scalar_one_or_none()

        if not song:
            raise ValueError(f"Song not found: {task.song_id}")

        # Check if approved
        eval_result = await db.execute(
            select(Evaluation)
            .where(Evaluation.song_id == task.song_id, Evaluation.approved == True)
        )
        evaluation = eval_result.scalar_one_or_none()

        if not evaluation:
            raise ValueError(f"Song {task.song_id} is not approved for YouTube upload")

        # Generate video
        video_generator = get_video_generator()
        audio_path = Path(settings.DOWNLOAD_FOLDER) / f"{song.id}.mp3"
        video_path = Path(settings.VIDEO_OUTPUT_PATH) / f"{song.id}.mp4"

        video_generator.generate_video(
            audio_file=audio_path,
            output_file=video_path,
            title=song.title,
        )

        # Upload to YouTube
        youtube_uploader = get_youtube_uploader()
        upload_result = await youtube_uploader.upload(
            video_path=video_path,
            title=song.title,
            description=f"AI-generated song: {song.title}\n\nGenre: {song.genre}",
            tags=[song.genre, "AI Music", "Suno AI"],
        )

        # Create YouTubeUpload record
        youtube_upload = YouTubeUpload(
            song_id=song.id,
            video_id=upload_result.get("video_id"),
            upload_status="published",
            title=song.title,
            scheduled_time=None,
        )
        db.add(youtube_upload)

        # Update song status
        song.status = "published"
        await db.commit()

        # Send notification
        notification_service = get_notification_service()
        await notification_service.notify_youtube_upload_complete(song, youtube_upload)

        logger.info(f"YouTube upload complete for song {task.song_id}")


class WorkerPool:
    """Pool of background workers."""

    def __init__(self, num_workers: int = 2) -> None:
        """Initialize the worker pool.

        Args:
            num_workers: Number of workers to create
        """
        self.num_workers = num_workers
        self.workers: list[BackgroundWorker] = []
        self.tasks: list[asyncio.Task] = []

    async def start(self) -> None:
        """Start all workers in the pool.

        Workers run as background tasks and don't block startup.
        """
        logger.info(f"Starting worker pool with {self.num_workers} workers")

        for i in range(self.num_workers):
            worker = BackgroundWorker(worker_id=i)
            self.workers.append(worker)

            # Create task but don't await it - let it run in background
            task = asyncio.create_task(worker.start())
            self.tasks.append(task)

        logger.info(f"Worker pool started with {self.num_workers} workers running in background")

    async def stop(self) -> None:
        """Stop all workers in the pool."""
        logger.info("Stopping worker pool")

        for worker in self.workers:
            await worker.stop()

        # Cancel all tasks
        for task in self.tasks:
            task.cancel()

        # Wait for cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        self.workers.clear()
        self.tasks.clear()

        logger.info("Worker pool stopped")


# Global instance
_worker_pool: Optional[WorkerPool] = None


def get_worker_pool() -> WorkerPool:
    """Get the global worker pool instance.

    Returns:
        The singleton WorkerPool instance
    """
    global _worker_pool
    if _worker_pool is None:
        _worker_pool = WorkerPool(num_workers=settings.WORKER_COUNT)
    return _worker_pool
