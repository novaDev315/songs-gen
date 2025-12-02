"""File watcher service to monitor generated/songs folder for new songs."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from app.config import get_settings
from app.database import get_session_local
from app.models.song import Song
from app.models.task_queue import TaskQueue

logger = logging.getLogger(__name__)
settings = get_settings()


class SongFileHandler(FileSystemEventHandler):
    """Handler for new song files in the generated folder."""

    def __init__(self) -> None:
        """Initialize the file handler."""
        super().__init__()
        self.loop = asyncio.get_event_loop()

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle new file creation.

        Args:
            event: File creation event from watchdog
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .md files
        if file_path.suffix != ".md":
            return

        logger.info(f"New song file detected: {file_path}")

        # Schedule async processing
        asyncio.run_coroutine_threadsafe(
            self.process_song_file(file_path),
            self.loop,
        )

    async def process_song_file(self, file_path: Path) -> None:
        """Process new song file and add to database.

        Args:
            file_path: Path to the new song file
        """
        try:
            # Wait for file to be fully written
            await asyncio.sleep(1)

            # Read song file content
            content = file_path.read_text(encoding="utf-8")

            # Extract metadata from file content
            metadata = self.parse_song_file(content)

            # Check for accompanying .meta.json file
            meta_file = file_path.with_suffix(".meta.json")
            metadata_json = None
            if meta_file.exists():
                with open(meta_file, "r") as f:
                    metadata_json = json.dumps(json.load(f))

            # Create database session
            session_local = get_session_local()
            async with session_local() as db:
                # Check if song already exists (by file_path)
                result = await db.execute(
                    select(Song).where(Song.file_path == str(file_path))
                )
                existing = result.scalar_one_or_none()

                if existing:
                    logger.info(f"Song already exists in database: {file_path}")
                    return

                # Create new song record
                song = Song(
                    id=file_path.stem,  # Use filename (without .md) as ID
                    title=metadata.get("title", file_path.stem),
                    genre=metadata.get("genre", "Unknown"),
                    style_prompt=metadata.get("style_prompt", ""),
                    lyrics=metadata.get("lyrics", content),
                    file_path=str(file_path),
                    status="pending",
                    metadata_json=metadata_json,
                )
                db.add(song)
                await db.commit()
                await db.refresh(song)

                logger.info(f"Song added to database: {song.id}")

                # Create suno_upload task in queue
                task = TaskQueue(
                    task_type="suno_upload",
                    song_id=song.id,
                    status="pending",
                    priority=0,
                )
                db.add(task)
                await db.commit()

                logger.info(f"Created suno_upload task for song: {song.id}")

        except Exception as e:
            logger.error(f"Error processing song file {file_path}: {e}")

    def parse_song_file(self, content: str) -> dict:
        """Parse song file content to extract metadata.

        Args:
            content: Raw file content

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        lines = content.split("\n")

        in_frontmatter = False
        frontmatter_lines = []
        lyrics_lines = []

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    in_frontmatter = False
                    continue

            if in_frontmatter:
                frontmatter_lines.append(line)
            else:
                lyrics_lines.append(line)

        # Parse frontmatter (YAML-like format)
        for line in frontmatter_lines:
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip().strip('"\'')

        # Get lyrics (everything after frontmatter)
        metadata["lyrics"] = "\n".join(lyrics_lines).strip()

        return metadata


class FileWatcher:
    """Watches the generated/songs folder for new song files."""

    def __init__(self) -> None:
        """Initialize the file watcher."""
        self.observer = Observer()
        self.handler = SongFileHandler()
        self.watch_path = Path(settings.GENERATED_SONGS_PATH)
        self.watch_path.mkdir(parents=True, exist_ok=True)
        self._started = False

    def start(self) -> None:
        """Start watching the folder."""
        if self._started:
            logger.warning("File watcher already started")
            return

        logger.info(f"Starting file watcher on: {self.watch_path}")
        self.observer.schedule(self.handler, str(self.watch_path), recursive=False)
        self.observer.start()
        self._started = True

    def stop(self) -> None:
        """Stop watching the folder."""
        if not self._started:
            return

        logger.info("Stopping file watcher")
        self.observer.stop()
        self.observer.join()
        self._started = False


# Global instance
_file_watcher: FileWatcher | None = None


def get_file_watcher() -> FileWatcher:
    """Get the global file watcher instance.

    Returns:
        The singleton FileWatcher instance
    """
    global _file_watcher
    if _file_watcher is None:
        _file_watcher = FileWatcher()
    return _file_watcher
