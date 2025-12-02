"""Unit tests for evaluator service.

Tests for song evaluation and quality scoring.
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime, timezone

import pytest

from app.services.evaluator import (
    EvaluatorService,
    get_evaluator,
)
from app.models.song import Song
from app.models.evaluation import Evaluation


@pytest.mark.unit
class TestEvaluatorService:
    """Test EvaluatorService class."""

    def test_init_sets_up_analyzer_and_folder(self, temp_dir):
        """Test that initialization sets up analyzer and download folder."""
        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(temp_dir / "downloads")

            with patch('app.services.evaluator.get_audio_analyzer') as mock_get_analyzer:
                mock_analyzer = MagicMock()
                mock_get_analyzer.return_value = mock_analyzer

                evaluator = EvaluatorService()

                assert evaluator.analyzer is mock_analyzer
                assert evaluator.download_folder == Path(temp_dir / "downloads")


@pytest.mark.unit
@pytest.mark.asyncio
class TestEvaluatorServiceEvaluateSong:
    """Test EvaluatorService.evaluate_song method."""

    async def test_evaluate_song_success_new_evaluation(self, temp_dir):
        """Test successful song evaluation creating new evaluation."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        audio_file = download_folder / "test-song-001.mp3"
        audio_file.write_bytes(b"fake audio data")

        # Mock song
        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        # Mock audio analyzer
        mock_analyzer = MagicMock()
        mock_analyzer.analyze_audio.return_value = {
            "audio_quality_score": 85.5,
            "duration_seconds": 180.0,
            "file_size_mb": 4.2,
            "sample_rate": 44100,
            "bitrate": 192000,
        }

        # Mock database session
        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_eval = MagicMock()
        mock_result_eval.scalar_one_or_none.return_value = None  # No existing evaluation
        mock_db.execute.side_effect = [mock_result_song, mock_result_eval]

        mock_evaluation = MagicMock(spec=Evaluation)

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer', return_value=mock_analyzer):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()
                    result = await evaluator.evaluate_song("test-song-001")

                    # Verify analyzer was called
                    mock_analyzer.analyze_audio.assert_called_once_with(audio_file)

                    # Verify evaluation was added to database
                    mock_db.add.assert_called_once()
                    added_eval = mock_db.add.call_args[0][0]
                    assert added_eval.song_id == "test-song-001"
                    assert added_eval.audio_quality_score == 85.5
                    assert added_eval.approved is True  # Score > MIN_QUALITY_SCORE

    async def test_evaluate_song_updates_existing_evaluation(self, temp_dir):
        """Test song evaluation updates existing evaluation."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        audio_file = download_folder / "test-song-001.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        # Existing evaluation
        mock_existing_eval = MagicMock(spec=Evaluation)
        mock_existing_eval.song_id = "test-song-001"
        mock_existing_eval.audio_quality_score = 60.0

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_audio.return_value = {
            "audio_quality_score": 90.0,
            "duration_seconds": 200.0,
            "file_size_mb": 5.0,
            "sample_rate": 48000,
            "bitrate": 256000,
        }

        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_eval = MagicMock()
        mock_result_eval.scalar_one_or_none.return_value = mock_existing_eval
        mock_db.execute.side_effect = [mock_result_song, mock_result_eval]

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer', return_value=mock_analyzer):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()
                    result = await evaluator.evaluate_song("test-song-001")

                    # Should update existing evaluation, not add new
                    mock_db.add.assert_not_called()
                    assert mock_existing_eval.audio_quality_score == 90.0
                    assert mock_existing_eval.duration_seconds == 200.0

    async def test_evaluate_song_not_found(self, temp_dir):
        """Test evaluation of non-existent song."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer'):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()

                    with pytest.raises(ValueError, match="Song not found"):
                        await evaluator.evaluate_song("nonexistent-song")

    async def test_evaluate_song_audio_file_not_found(self, temp_dir):
        """Test evaluation when audio file doesn't exist."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        # Don't create audio file

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_song
        mock_db.execute.return_value = mock_result

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer'):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()

                    with pytest.raises(FileNotFoundError, match="Audio file not found"):
                        await evaluator.evaluate_song("test-song-001")

    async def test_evaluate_song_below_quality_threshold(self, temp_dir):
        """Test evaluation with score below quality threshold."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        audio_file = download_folder / "test-song-001.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_audio.return_value = {
            "audio_quality_score": 50.0,  # Below threshold
            "duration_seconds": 120.0,
            "file_size_mb": 3.0,
            "sample_rate": 44100,
            "bitrate": 128000,
        }

        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_eval = MagicMock()
        mock_result_eval.scalar_one_or_none.return_value = None
        mock_db.execute.side_effect = [mock_result_song, mock_result_eval]

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0  # Score is below this

            with patch('app.services.evaluator.get_audio_analyzer', return_value=mock_analyzer):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()
                    result = await evaluator.evaluate_song("test-song-001")

                    # Evaluation should NOT be auto-approved
                    added_eval = mock_db.add.call_args[0][0]
                    assert added_eval.audio_quality_score == 50.0
                    # approved should not be set to True
                    assert not hasattr(added_eval, 'approved') or added_eval.approved is not True

    async def test_evaluate_song_analyzer_error(self, temp_dir):
        """Test evaluation when analyzer throws error."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        audio_file = download_folder / "test-song-001.mp3"
        audio_file.write_bytes(b"corrupted audio data")

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_audio.side_effect = Exception("Invalid audio format")

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_song
        mock_db.execute.return_value = mock_result

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer', return_value=mock_analyzer):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()

                    with pytest.raises(Exception, match="Invalid audio format"):
                        await evaluator.evaluate_song("test-song-001")


@pytest.mark.unit
class TestGetEvaluator:
    """Test get_evaluator singleton function."""

    def test_get_evaluator_creates_singleton(self, temp_dir):
        """Test that get_evaluator creates a singleton."""
        import app.services.evaluator as ev
        ev._evaluator = None

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(temp_dir / "downloads")

            with patch('app.services.evaluator.get_audio_analyzer'):
                evaluator1 = get_evaluator()
                evaluator2 = get_evaluator()

                assert evaluator1 is evaluator2

        # Clean up
        ev._evaluator = None

    def test_get_evaluator_returns_existing(self, temp_dir):
        """Test that get_evaluator returns existing instance."""
        import app.services.evaluator as ev

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(temp_dir / "downloads")

            with patch('app.services.evaluator.get_audio_analyzer'):
                existing_evaluator = EvaluatorService()
                ev._evaluator = existing_evaluator

                result = get_evaluator()

                assert result is existing_evaluator

        # Clean up
        ev._evaluator = None


@pytest.mark.unit
@pytest.mark.asyncio
class TestEvaluatorServiceEdgeCases:
    """Test edge cases for EvaluatorService."""

    async def test_evaluate_song_updates_song_status(self, temp_dir):
        """Test that evaluation updates song status to 'evaluated'."""
        download_folder = temp_dir / "downloads"
        download_folder.mkdir()
        audio_file = download_folder / "test-song-001.mp3"
        audio_file.write_bytes(b"fake audio data")

        mock_song = MagicMock(spec=Song)
        mock_song.id = "test-song-001"
        mock_song.status = "downloaded"

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_audio.return_value = {
            "audio_quality_score": 75.0,
            "duration_seconds": 180.0,
            "file_size_mb": 4.0,
            "sample_rate": 44100,
            "bitrate": 192000,
        }

        mock_db = AsyncMock()
        mock_result_song = MagicMock()
        mock_result_song.scalar_one_or_none.return_value = mock_song
        mock_result_eval = MagicMock()
        mock_result_eval.scalar_one_or_none.return_value = None
        mock_db.execute.side_effect = [mock_result_song, mock_result_eval]

        with patch('app.services.evaluator.settings') as mock_settings:
            mock_settings.DOWNLOAD_FOLDER = str(download_folder)
            mock_settings.MIN_QUALITY_SCORE = 70.0

            with patch('app.services.evaluator.get_audio_analyzer', return_value=mock_analyzer):
                with patch('app.services.evaluator.AsyncSessionLocal') as mock_session_local:
                    mock_session_local.return_value.__aenter__.return_value = mock_db
                    mock_session_local.return_value.__aexit__.return_value = None

                    evaluator = EvaluatorService()
                    await evaluator.evaluate_song("test-song-001")

                    # Verify song status was updated
                    assert mock_song.status == "evaluated"
                    # Verify commit was called at least twice
                    assert mock_db.commit.call_count >= 2
