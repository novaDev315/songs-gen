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
from app.database import AsyncSessionLocal
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
            async with AsyncSessionLocal() as db:
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

                logger.info(f"Song created in database: {song.id} ({song.title})")

                # Create task to upload to Suno (if auto-upload enabled)
                if settings.AUTO_UPLOAD_TO_SUNO:
                    task = TaskQueue(
                        task_type="suno_upload",
                        song_id=song.id,
                        priority=0,
                        status="pending",
                    )
                    db.add(task)
                    await db.commit()
                    logger.info(f"Suno upload task created for song: {song.id}")

        except Exception as e:
            logger.error(
                f"Error processing song file {file_path}: {e}",
                exc_info=True,
            )

    def parse_song_file(self, content: str) -> dict[str, Any]:
        """Parse song file content to extract metadata.

        Args:
            content: Full content of the song markdown file

        Returns:
            Dictionary containing extracted metadata
        """
        lines = content.split("\n")
        metadata: dict[str, Any] = {
            "title": "",
            "genre": "",
            "style_prompt": "",
            "lyrics": content,
        }

        # Extract title (first # heading)
        for line in lines:
            if line.startswith("# "):
                metadata["title"] = line[2:].strip()
                break

        # Extract style prompt and lyrics sections
        in_style = False
        style_lines: list[str] = []
        in_lyrics = False
        lyrics_lines: list[str] = []

        for line in lines:
            # Check for section headers
            if line.startswith("## Style Prompt"):
                in_style = True
                in_lyrics = False
                continue
            elif line.startswith("## Lyrics"):
                in_lyrics = True
                in_style = False
                continue
            elif line.startswith("##"):
                in_style = False
                in_lyrics = False
                continue

            # Collect content from active sections
            if in_style and line.strip():
                style_lines.append(line.strip())
            elif in_lyrics and line.strip():
                lyrics_lines.append(line.strip())

        # Join collected lines
        if style_lines:
            metadata["style_prompt"] = " ".join(style_lines)

        if lyrics_lines:
            metadata["lyrics"] = "\n".join(lyrics_lines)

        # Try to extract genre from style prompt or title
        style_lower = metadata["style_prompt"].lower()
        for genre in ["pop", "rock", "jazz", "hip-hop", "edm", "country", "rap"]:
            if genre in style_lower:
                metadata["genre"] = genre.title()
                break

        return metadata


class FileWatcherService:
    """Service to watch for new song files."""

    def __init__(self) -> None:
        """Initialize the file watcher service."""
        self.observer = Observer()
        self.handler = SongFileHandler()
        self.watch_folder = Path(settings.WATCH_FOLDER)

    def start(self) -> None:
        """Start watching the folder."""
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)

        # Start observer
        self.observer.schedule(
            self.handler,
            str(self.watch_folder),
            recursive=True,
        )
        self.observer.start()
        logger.info(f"File watcher started monitoring: {self.watch_folder}")

    def stop(self) -> None:
        """Stop watching the folder."""
        self.observer.stop()
        self.observer.join()
        logger.info("File watcher stopped")


# Global instance
_file_watcher: FileWatcherService | None = None


def get_file_watcher() -> FileWatcherService:
    """Get the global file watcher instance.

    Returns:
        The singleton FileWatcherService instance
    """
    global _file_watcher
    if _file_watcher is None:
        _file_watcher = FileWatcherService()
    return _file_watcher
