"""Download manager for Suno-generated audio files."""

import logging
import asyncio
from pathlib import Path
from typing import Optional
import aiohttp
import aiofiles
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()


class DownloadManager:
    """Manages downloading audio files from Suno."""

    def __init__(self):
        self.download_folder = Path(settings.DOWNLOAD_FOLDER)
        self.download_folder.mkdir(parents=True, exist_ok=True)

    async def download_song(self, song_id: str, audio_url: str) -> Optional[Path]:
        """Download song audio from URL.

        Args:
            song_id: Unique song identifier
            audio_url: URL to download audio from

        Returns:
            Path to downloaded file, or None if download failed

        Raises:
            ValueError: If downloaded file is invalid
            aiohttp.ClientError: If HTTP request fails
        """
        try:
            # Generate filename
            filename = f"{song_id}.mp3"
            file_path = self.download_folder / filename

            # Skip if already downloaded
            if file_path.exists():
                logger.info(f"Song already downloaded: {file_path}")
                return file_path

            logger.info(f"Downloading song {song_id} from {audio_url}")

            # Download with streaming
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    audio_url, timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    response.raise_for_status()

                    # Stream to file
                    async with aiofiles.open(file_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)

            # Verify file exists and has content
            if not file_path.exists() or file_path.stat().st_size == 0:
                raise ValueError(f"Downloaded file is empty or missing: {file_path}")

            logger.info(
                f"Song downloaded successfully: {file_path} ({file_path.stat().st_size} bytes)"
            )
            return file_path

        except Exception as e:
            logger.error(f"Error downloading song {song_id}: {e}", exc_info=True)
            raise

    async def download_from_suno_job(self, suno_job_id: int) -> Optional[Path]:
        """Download song from SunoJob record.
