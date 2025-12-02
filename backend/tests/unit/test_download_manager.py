"""Unit tests for download manager service.

Tests for downloading audio files from Suno.
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime

import pytest
import aiohttp

from app.services.download_manager import (
    DownloadManager,
    get_download_manager,
    _download_manager,
)
from app.models.song import Song
from app.models.suno_job import SunoJob


@pytest.mark.unit
class TestDownloadManager:
    """Test DownloadManager class."""

    def test_init_creates_download_folder(self, temp_dir):
        """Test that initialization creates download folder."""
        download_folder = temp_dir / "downloads"
        assert not download_folder.exists()

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            manager = DownloadManager()

            assert download_folder.exists()
            assert manager.download_folder == download_folder

    def test_init_with_existing_folder(self, temp_dir):
        """Test initialization with existing download folder."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            manager = DownloadManager()

            assert manager.download_folder == download_folder


@pytest.mark.unit
@pytest.mark.asyncio
class TestDownloadManagerDownloadSong:
    """Test DownloadManager.download_song method."""

    async def test_download_song_already_exists(self, temp_dir):
        """Test that existing downloads are skipped."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        existing_file = download_folder / "test-song-001.mp3"
        existing_file.write_bytes(b"existing audio")

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            manager = DownloadManager()

            with patch('aiohttp.ClientSession') as mock_client:
                result = await manager.download_song(
                    song_id="test-song-001",
                    audio_url="https://cdn.suno.com/audio/test.mp3",
                )

                # Should return existing file without downloading
                assert result == existing_file
                mock_client.assert_not_called()

    async def test_download_song_validates_file(self, temp_dir):
        """Test download validates that file was created properly."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            manager = DownloadManager()

            # Mock the download to create an empty file
            async def mock_download(*args, **kwargs):
                file_path = download_folder / "test-empty.mp3"
                file_path.write_bytes(b"")  # Empty file
                return file_path

            with patch.object(manager, 'download_song', side_effect=ValueError("Downloaded file is empty or missing")):
                with pytest.raises(ValueError, match="empty or missing"):
                    await manager.download_song(
                        song_id="test-empty",
                        audio_url="https://cdn.suno.com/audio/empty.mp3",
                    )


@pytest.mark.unit
@pytest.mark.asyncio
class TestDownloadManagerDownloadFromSunoJob:
    """Test DownloadManager.download_from_suno_job method."""

    async def test_download_from_suno_job_success(self, temp_dir):
        """Test successful download from Suno job."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        # Create mock Suno job
        mock_suno_job = MagicMock(spec=SunoJob)
        mock_suno_job.id = 1
        mock_suno_job.song_id = "test-song-001"
        mock_suno_job.audio_url = "https://cdn.suno.com/audio/test.mp3"

        # Create mock song
        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloading"

        # Mock database session
        mock_db = AsyncMock()
        mock_result_job = MagicMock()
        mock_result_job.scalar_one_or_none.return_value = mock_suno_job
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_db.execute.side_effect = [mock_result_job, mock_result_song]

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)

            with patch('app.services.download_manager.AsyncSessionLocal') as mock_session_local:
                mock_session_local.return_value.__aenter__.return_value = mock_db
                mock_session_local.return_value.__aexit__.return_value = None

                manager = DownloadManager()

                # Mock download_song method
                expected_path = download_folder / "test-song-001.mp3"
                with patch.object(
                    manager, 'download_song', new_callable=AsyncMock
                ) as mock_download:
                    mock_download.return_value = expected_path

                    result = await manager.download_from_suno_job(1)

                    assert result == expected_path
                    mock_download.assert_called_once_with(
                        "test-song-001",
                        "https://cdn.suno.com/audio/test.mp3",
                    )

    async def test_download_from_suno_job_not_found(self, temp_dir):
        """Test download from non-existent Suno job."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)

            with patch('app.services.download_manager.AsyncSessionLocal') as mock_session_local:
                mock_session_local.return_value.__aenter__.return_value = mock_db
                mock_session_local.return_value.__aexit__.return_value = None

                manager = DownloadManager()

                with pytest.raises(ValueError, match="Suno job not found"):
                    await manager.download_from_suno_job(999)

    async def test_download_from_suno_job_no_audio_url(self, temp_dir):
        """Test download from Suno job with no audio URL."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        mock_suno_job = MagicMock(spec=SunoJob)
        mock_suno_job.id = 1
        mock_suno_job.song_id = "test-song-001"
        mock_suno_job.audio_url = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_suno_job
        mock_db.execute.return_value = mock_result

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)

            with patch('app.services.download_manager.AsyncSessionLocal') as mock_session_local:
                mock_session_local.return_value.__aenter__.return_value = mock_db
                mock_session_local.return_value.__aexit__.return_value = None

                manager = DownloadManager()

                with pytest.raises(ValueError, match="no audio URL"):
                    await manager.download_from_suno_job(1)


@pytest.mark.unit
class TestGetDownloadManager:
    """Test get_download_manager singleton function."""

    def test_get_download_manager_creates_singleton(self, temp_dir):
        """Test that get_download_manager creates a singleton."""
        # Reset global instance
        import app.services.download_manager as dm
        dm._download_manager = None

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(temp_dir / "downloads")

            manager1 = get_download_manager()
            manager2 = get_download_manager()

            assert manager1 is manager2

        # Clean up
        dm._download_manager = None

    def test_get_download_manager_returns_existing(self, temp_dir):
        """Test that get_download_manager returns existing instance."""
        import app.services.download_manager as dm

        with patch('app.services.download_manager.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(temp_dir / "downloads")

            existing_manager = DownloadManager()
            dm._download_manager = existing_manager

            result = get_download_manager()

            assert result is existing_manager

        # Clean up
        dm._download_manager = None
