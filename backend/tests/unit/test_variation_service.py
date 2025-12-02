"""Unit tests for variation service.

Tests for managing Suno variations.
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.variation_service import (
    VariationService,
    get_variation_service,
)
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.suno_variation import SunoVariation


@pytest.mark.unit
class TestVariationService:
    """Test VariationService class."""

    def test_init_sets_up_download_folder(self, temp_dir):
        """Test that initialization sets up download folder."""
        download_folder = temp_dir / "downloads"
        service = VariationService(download_folder=download_folder)

        assert service.download_folder == download_folder

    def test_init_uses_settings_default(self):
        """Test that initialization uses settings default."""
        with patch("app.services.variation_service.settings") as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = "/default/path"

            service = VariationService()

            assert service.download_folder == Path("/default/path")


@pytest.mark.unit
@pytest.mark.asyncio
class TestVariationServiceGetPendingReviewSongs:
    """Test VariationService.get_pending_review_songs method."""

    async def test_get_pending_review_songs_success(self):
        """Test successful retrieval of pending review songs."""
        # Mock songs
        mock_song1 = MagicMock(spec=Song)
        mock_song1.id = "song-001"
        mock_song1.status = "downloaded"
        mock_song1.selected_variation_id = None

        mock_song2 = MagicMock(spec=Song)
        mock_song2.id = "song-002"
        mock_song2.status = "reviewing"
        mock_song2.selected_variation_id = None

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_song1, mock_song2]
        mock_db.execute.return_value = mock_result

        service = VariationService()
        songs = await service.get_pending_review_songs(mock_db, limit=50)

        assert len(songs) == 2
        assert songs[0].id == "song-001"
        assert songs[1].id == "song-002"

    async def test_get_pending_review_songs_empty(self):
        """Test retrieval with no pending songs."""
        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result

        service = VariationService()
        songs = await service.get_pending_review_songs(mock_db, limit=50)

        assert len(songs) == 0

    async def test_get_pending_review_songs_respects_limit(self):
        """Test that limit parameter is respected."""
        # Create more songs than limit
        mock_songs = [
            MagicMock(spec=Song, id=f"song-{i:03d}", status="downloaded", selected_variation_id=None)
            for i in range(100)
        ]

        # Mock database session - will return only first 10
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_songs[:10]
        mock_db.execute.return_value = mock_result

        service = VariationService()
        songs = await service.get_pending_review_songs(mock_db, limit=10)

        assert len(songs) == 10


@pytest.mark.unit
@pytest.mark.asyncio
class TestVariationServiceGetVariations:
    """Test VariationService.get_variations method."""

    async def test_get_variations_success(self):
        """Test successful retrieval of variations."""
        # Mock variations
        mock_var1 = MagicMock(spec=SunoVariation)
        mock_var1.id = 1
        mock_var1.variation_index = 1
        mock_var1.is_selected = False

        mock_var2 = MagicMock(spec=SunoVariation)
        mock_var2.id = 2
        mock_var2.variation_index = 2
        mock_var2.is_selected = False

        # Mock SunoJob
        mock_job = MagicMock(spec=SunoJob)
        mock_job.id = 100
        mock_job.song_id = "test-song-001"
        mock_job.variations = [mock_var2, mock_var1]  # Unsorted

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_job
        mock_db.execute.return_value = mock_result

        service = VariationService()
        variations = await service.get_variations(mock_db, "test-song-001")

        assert len(variations) == 2
        assert variations[0].variation_index == 1  # Sorted by index
        assert variations[1].variation_index == 2

    async def test_get_variations_no_suno_job(self):
        """Test error when no SunoJob found."""
        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = VariationService()

        with pytest.raises(ValueError, match="No SunoJob found"):
            await service.get_variations(mock_db, "nonexistent-song")


@pytest.mark.unit
@pytest.mark.asyncio
class TestVariationServiceSelectVariation:
    """Test VariationService.select_variation method."""

    async def test_select_variation_success(self):
        """Test successful variation selection."""
        # Mock song
        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        # Mock variations
        mock_var1 = MagicMock(spec=SunoVariation)
        mock_var1.id = 1
        mock_var1.variation_index = 1
        mock_var1.is_selected = False
        mock_var1.audio_path = "/downloads/test-song-001/test-song-001_v1.mp3"

        mock_var2 = MagicMock(spec=SunoVariation)
        mock_var2.id = 2
        mock_var2.variation_index = 2
        mock_var2.is_selected = False
        mock_var2.audio_path = "/downloads/test-song-001/test-song-001_v2.mp3"

        # Mock SunoJob
        mock_job = MagicMock(spec=SunoJob)
        mock_job.id = 100
        mock_job.song_id = "test-song-001"

        # Mock database session
        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_var = MagicMock()
        mock_result_var.scalar_one_or_none.return_value = mock_var1
        mock_result_job = MagicMock()
        mock_result_job.scalar_one_or_none.return_value = mock_job
        mock_result_all = MagicMock()
        mock_result_all.scalars.return_value.all.return_value = [mock_var1, mock_var2]

        mock_db.execute.side_effect = [
            mock_result_song,
            mock_result_var,
            mock_result_job,
            mock_result_all,
        ]

        service = VariationService()
        result = await service.select_variation(
            mock_db, "test-song-001", 1, delete_other=False
        )

        # Verify variation 1 is selected
        assert mock_var1.is_selected is True
        assert mock_var1.selected_at is not None

        # Verify variation 2 is not selected
        assert mock_var2.is_selected is False
        assert mock_var2.selected_at is None

        # Verify song is updated
        assert mock_song.selected_variation_id == 1
        assert mock_song.audio_path == mock_var1.audio_path
        assert mock_song.status == "evaluated"

        # Verify database operations
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called_once_with(mock_song)

    async def test_select_variation_with_delete_other(self, temp_dir):
        """Test variation selection with delete_other=True."""
        download_folder = temp_dir / "downloads"
        song_folder = download_folder / "test-song-001"
        song_folder.mkdir(parents=True)

        # Create dummy files
        file1 = song_folder / "test-song-001_v1.mp3"
        file2 = song_folder / "test-song-001_v2.mp3"
        file1.write_bytes(b"audio data 1")
        file2.write_bytes(b"audio data 2")

        # Mock song
        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        # Mock variations
        mock_var1 = MagicMock(spec=SunoVariation)
        mock_var1.id = 1
        mock_var1.variation_index = 1
        mock_var1.is_selected = False
        mock_var1.audio_path = str(file1)

        mock_var2 = MagicMock(spec=SunoVariation)
        mock_var2.id = 2
        mock_var2.variation_index = 2
        mock_var2.is_selected = False
        mock_var2.audio_path = str(file2)

        # Mock SunoJob
        mock_job = MagicMock(spec=SunoJob)
        mock_job.id = 100
        mock_job.song_id = "test-song-001"

        # Mock database session
        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_var = MagicMock()
        mock_result_var.scalar_one_or_none.return_value = mock_var1
        mock_result_job = MagicMock()
        mock_result_job.scalar_one_or_none.return_value = mock_job
        mock_result_all = MagicMock()
        mock_result_all.scalars.return_value.all.return_value = [mock_var1, mock_var2]

        mock_db.execute.side_effect = [
            mock_result_song,
            mock_result_var,
            mock_result_job,
            mock_result_all,
        ]

        service = VariationService(download_folder=download_folder)
        result = await service.select_variation(
            mock_db, "test-song-001", 1, delete_other=True
        )

        # Verify variation 2 is soft deleted
        assert mock_var2.is_deleted is True

        # Verify file 2 is deleted
        assert file1.exists()  # Selected file remains
        assert not file2.exists()  # Other file deleted

    async def test_select_variation_song_not_found(self):
        """Test error when song not found."""
        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = VariationService()

        with pytest.raises(ValueError, match="Song not found"):
            await service.select_variation(
                mock_db, "nonexistent-song", 1, delete_other=False
            )

    async def test_select_variation_variation_not_found(self):
        """Test error when variation not found."""
        # Mock song
        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"

        # Mock database session
        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_var = MagicMock()
        mock_result_var.scalar_one_or_none.return_value = None

        mock_db.execute.side_effect = [mock_result_song, mock_result_var]

        service = VariationService()

        with pytest.raises(ValueError, match="Variation not found"):
            await service.select_variation(
                mock_db, "test-song-001", 999, delete_other=False
            )


@pytest.mark.unit
@pytest.mark.asyncio
class TestVariationServiceDeleteVariation:
    """Test VariationService.delete_variation method."""

    async def test_delete_variation_soft_delete(self):
        """Test soft delete of variation."""
        # Mock variation
        mock_var = MagicMock(spec=SunoVariation)
        mock_var.id = 1
        mock_var.is_deleted = False
        mock_var.variation_index = 1

        # Mock SunoJob
        mock_job = MagicMock(spec=SunoJob)
        mock_job.song_id = "test-song-001"
        mock_var.suno_job = mock_job

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_var
        mock_db.execute.return_value = mock_result

        service = VariationService()
        result = await service.delete_variation(mock_db, 1, hard_delete=False)

        assert result is True
        assert mock_var.is_deleted is True
        mock_db.commit.assert_called_once()
        mock_db.delete.assert_not_called()

    async def test_delete_variation_hard_delete(self, temp_dir):
        """Test hard delete of variation."""
        download_folder = temp_dir / "downloads"
        song_folder = download_folder / "test-song-001"
        song_folder.mkdir(parents=True)

        # Create dummy file
        file_path = song_folder / "test-song-001_v1.mp3"
        file_path.write_bytes(b"audio data")

        # Mock variation
        mock_var = MagicMock(spec=SunoVariation)
        mock_var.id = 1
        mock_var.variation_index = 1
        mock_var.audio_path = str(file_path)

        # Mock SunoJob
        mock_job = MagicMock(spec=SunoJob)
        mock_job.song_id = "test-song-001"
        mock_var.suno_job = mock_job

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_var
        mock_db.execute.return_value = mock_result

        service = VariationService(download_folder=download_folder)
        result = await service.delete_variation(mock_db, 1, hard_delete=True)

        assert result is True
        mock_db.delete.assert_called_once_with(mock_var)
        mock_db.commit.assert_called_once()
        assert not file_path.exists()  # File deleted

    async def test_delete_variation_not_found(self):
        """Test error when variation not found."""
        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = VariationService()

        with pytest.raises(ValueError, match="Variation not found"):
            await service.delete_variation(mock_db, 999, hard_delete=False)


@pytest.mark.unit
@pytest.mark.asyncio
class TestVariationServiceGetVariationById:
    """Test VariationService.get_variation_by_id method."""

    async def test_get_variation_by_id_success(self):
        """Test successful retrieval of variation by ID."""
        # Mock variation
        mock_var = MagicMock(spec=SunoVariation)
        mock_var.id = 1
        mock_var.variation_index = 1

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_var
        mock_db.execute.return_value = mock_result

        service = VariationService()
        variation = await service.get_variation_by_id(mock_db, 1)

        assert variation is not None
        assert variation.id == 1

    async def test_get_variation_by_id_not_found(self):
        """Test retrieval when variation not found."""
        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = VariationService()
        variation = await service.get_variation_by_id(mock_db, 999)

        assert variation is None


@pytest.mark.unit
def test_get_variation_service_singleton():
    """Test that get_variation_service returns singleton."""
    service1 = get_variation_service()
    service2 = get_variation_service()

    assert service1 is service2
