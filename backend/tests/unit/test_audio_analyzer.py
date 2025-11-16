"""Unit tests for audio analyzer service.

Tests audio analysis functionality including quality scoring.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from app.services.audio_analyzer import AudioAnalyzer, get_audio_analyzer


# =============================================================================
# Audio Analyzer Initialization Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.audio
class TestAudioAnalyzerInit:
    """Test AudioAnalyzer initialization."""

    def test_create_analyzer(self):
        """Test creating an AudioAnalyzer instance."""
        analyzer = AudioAnalyzer()
        assert analyzer is not None

    def test_get_audio_analyzer_singleton(self):
        """Test get_audio_analyzer returns singleton."""
        analyzer1 = get_audio_analyzer()
        analyzer2 = get_audio_analyzer()

        assert analyzer1 is analyzer2


# =============================================================================
# Quality Score Calculation Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.audio
class TestQualityScoreCalculation:
    """Test audio quality score calculation logic."""

    def test_calculate_quality_score_perfect(self):
        """Test quality score calculation with ideal parameters."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,  # 3 minutes (ideal range)
            file_size_mb=4.2,
            sample_rate=44100,  # CD quality
            bitrate=256000,  # 256 kbps (high quality)
            rms_energy=0.25,  # Healthy energy level
        )

        # Should get high score with perfect parameters
        assert score >= 80.0
        assert score <= 100.0

    def test_calculate_quality_score_duration_ideal(self):
        """Test duration scoring for ideal range (2-5 minutes)."""
        analyzer = AudioAnalyzer()

        # Test 2 minutes (ideal)
        score_2min = analyzer.calculate_quality_score(
            duration=120.0,
            file_size_mb=3.0,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.25,
        )

        # Test 3 minutes (ideal)
        score_3min = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.5,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.25,
        )

        # Both should contribute 20 points for duration
        assert score_2min >= 70.0
        assert score_3min >= 70.0

    def test_calculate_quality_score_duration_short(self):
        """Test duration scoring for short audio."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=30.0,  # 30 seconds (too short)
            file_size_mb=1.0,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.25,
        )

        # Should get lower score for very short duration
        assert score < 80.0

    def test_calculate_quality_score_sample_rate_high(self):
        """Test sample rate scoring for high quality."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=48000,  # Higher than CD quality
            bitrate=192000,
            rms_energy=0.25,
        )

        assert score >= 70.0

    def test_calculate_quality_score_sample_rate_low(self):
        """Test sample rate scoring for low quality."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=22050,  # Low quality
            bitrate=192000,
            rms_energy=0.25,
        )

        # Should still get reasonable score but not maximum
        assert score < 90.0

    @pytest.mark.parametrize(
        "bitrate,expected_range",
        [
            (320000, (80, 100)),  # Very high quality
            (256000, (75, 100)),  # High quality
            (192000, (70, 95)),  # Good quality
            (128000, (65, 90)),  # Acceptable quality
            (96000, (60, 85)),  # Low quality
        ],
    )
    def test_calculate_quality_score_bitrates(self, bitrate, expected_range):
        """Test quality score for various bitrates."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=44100,
            bitrate=bitrate,
            rms_energy=0.25,
        )

        assert expected_range[0] <= score <= expected_range[1]

    def test_calculate_quality_score_rms_energy_healthy(self):
        """Test RMS energy scoring for healthy range."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.25,  # Healthy range (0.05-0.5)
        )

        assert score >= 70.0

    def test_calculate_quality_score_rms_energy_too_low(self):
        """Test RMS energy scoring when too quiet."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.01,  # Too quiet
        )

        # Should get lower score
        assert score < 90.0

    def test_calculate_quality_score_rms_energy_too_high(self):
        """Test RMS energy scoring when too loud (clipping)."""
        analyzer = AudioAnalyzer()

        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=4.0,
            sample_rate=44100,
            bitrate=192000,
            rms_energy=0.9,  # Likely clipping
        )

        # Should get lower score
        assert score < 90.0

    def test_calculate_quality_score_max_100(self):
        """Test that quality score never exceeds 100."""
        analyzer = AudioAnalyzer()

        # Use unrealistically perfect parameters
        score = analyzer.calculate_quality_score(
            duration=180.0,
            file_size_mb=10.0,
            sample_rate=96000,
            bitrate=320000,
            rms_energy=0.3,
        )

        assert score <= 100.0


# =============================================================================
# Audio Analysis Tests (with Mocks)
# =============================================================================


@pytest.mark.unit
@pytest.mark.audio
class TestAudioAnalysis:
    """Test audio file analysis with mocked librosa."""

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_analyze_audio_success(self, mock_sf, mock_librosa, temp_audio_file):
        """Test successful audio analysis."""
        # Mock librosa functions
        y = np.random.rand(44100 * 3)  # 3 seconds of audio
        sr = 44100
        mock_librosa.load.return_value = (y, sr)
        mock_librosa.get_duration.return_value = 180.5
        mock_librosa.feature.rms.return_value = np.array([[0.25] * 100])
        mock_librosa.feature.spectral_centroid.return_value = np.array(
            [[2500.0] * 100]
        )
        mock_librosa.feature.zero_crossing_rate.return_value = np.array(
            [[0.15] * 100]
        )
        mock_librosa.beat.beat_track.return_value = (120.0, None)

        # Mock soundfile info
        mock_info = Mock()
        mock_info.samplerate = 44100
        mock_info.channels = 2
        mock_sf.info.return_value = mock_info

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_audio(temp_audio_file)

        # Verify result structure
        assert "duration_seconds" in result
        assert "file_size_mb" in result
        assert "sample_rate" in result
        assert "bitrate" in result
        assert "channels" in result
        assert "rms_energy" in result
        assert "spectral_centroid" in result
        assert "zero_crossing_rate" in result
        assert "tempo" in result
        assert "audio_quality_score" in result

        # Verify values
        assert result["duration_seconds"] == 180.5
        assert result["sample_rate"] == 44100
        assert result["channels"] == 2
        assert result["tempo"] == 120.0

    @patch("app.services.audio_analyzer.librosa")
    def test_analyze_audio_file_not_found(self, mock_librosa):
        """Test audio analysis with non-existent file."""
        analyzer = AudioAnalyzer()
        non_existent_file = Path("/nonexistent/audio.mp3")

        mock_librosa.load.side_effect = FileNotFoundError("File not found")

        with pytest.raises(Exception):
            analyzer.analyze_audio(non_existent_file)

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_analyze_audio_mono(self, mock_sf, mock_librosa, temp_audio_file):
        """Test audio analysis with mono audio."""
        y = np.random.rand(44100)
        sr = 44100
        mock_librosa.load.return_value = (y, sr)
        mock_librosa.get_duration.return_value = 60.0
        mock_librosa.feature.rms.return_value = np.array([[0.2]])
        mock_librosa.feature.spectral_centroid.return_value = np.array([[2000.0]])
        mock_librosa.feature.zero_crossing_rate.return_value = np.array([[0.1]])
        mock_librosa.beat.beat_track.return_value = (100.0, None)

        mock_info = Mock()
        mock_info.samplerate = 44100
        mock_info.channels = 1  # Mono
        mock_sf.info.return_value = mock_info

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_audio(temp_audio_file)

        assert result["channels"] == 1

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_analyze_audio_various_sample_rates(
        self, mock_sf, mock_librosa, temp_audio_file
    ):
        """Test audio analysis with various sample rates."""
        for sample_rate in [22050, 32000, 44100, 48000, 96000]:
            y = np.random.rand(sample_rate)
            mock_librosa.load.return_value = (y, sample_rate)
            mock_librosa.get_duration.return_value = 60.0
            mock_librosa.feature.rms.return_value = np.array([[0.2]])
            mock_librosa.feature.spectral_centroid.return_value = np.array([[2000.0]])
            mock_librosa.feature.zero_crossing_rate.return_value = np.array([[0.1]])
            mock_librosa.beat.beat_track.return_value = (120.0, None)

            mock_info = Mock()
            mock_info.samplerate = sample_rate
            mock_info.channels = 2
            mock_sf.info.return_value = mock_info

            analyzer = AudioAnalyzer()
            result = analyzer.analyze_audio(temp_audio_file)

            assert result["sample_rate"] == sample_rate

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_analyze_audio_quality_score_calculated(
        self, mock_sf, mock_librosa, temp_audio_file
    ):
        """Test that quality score is calculated during analysis."""
        y = np.random.rand(44100 * 180)  # 3 minutes
        sr = 44100
        mock_librosa.load.return_value = (y, sr)
        mock_librosa.get_duration.return_value = 180.0
        mock_librosa.feature.rms.return_value = np.array([[0.25]])
        mock_librosa.feature.spectral_centroid.return_value = np.array([[2500.0]])
        mock_librosa.feature.zero_crossing_rate.return_value = np.array([[0.15]])
        mock_librosa.beat.beat_track.return_value = (120.0, None)

        mock_info = Mock()
        mock_info.samplerate = 44100
        mock_info.channels = 2
        mock_sf.info.return_value = mock_info

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_audio(temp_audio_file)

        # Quality score should be present and valid
        assert "audio_quality_score" in result
        assert 0 <= result["audio_quality_score"] <= 100

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_analyze_audio_error_handling(
        self, mock_sf, mock_librosa, temp_audio_file
    ):
        """Test audio analysis error handling."""
        mock_librosa.load.side_effect = Exception("Corrupted audio file")

        analyzer = AudioAnalyzer()

        with pytest.raises(Exception) as exc_info:
            analyzer.analyze_audio(temp_audio_file)

        assert "Corrupted audio file" in str(exc_info.value)


# =============================================================================
# Bitrate Calculation Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.audio
class TestBitrateCalculation:
    """Test bitrate calculation logic."""

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_bitrate_calculation_formula(
        self, mock_sf, mock_librosa, temp_audio_file
    ):
        """Test that bitrate is calculated correctly."""
        # Create 3-minute file (180 seconds)
        # File size: 4.32 MB = 4,536,115 bytes
        # Expected bitrate: (4,536,115 * 8) / 180 ≈ 201,605 bps
        temp_audio_file.write_bytes(b"\x00" * 4_536_115)

        y = np.random.rand(44100 * 180)
        sr = 44100
        mock_librosa.load.return_value = (y, sr)
        mock_librosa.get_duration.return_value = 180.0
        mock_librosa.feature.rms.return_value = np.array([[0.25]])
        mock_librosa.feature.spectral_centroid.return_value = np.array([[2500.0]])
        mock_librosa.feature.zero_crossing_rate.return_value = np.array([[0.15]])
        mock_librosa.beat.beat_track.return_value = (120.0, None)

        mock_info = Mock()
        mock_info.samplerate = 44100
        mock_info.channels = 2
        mock_sf.info.return_value = mock_info

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_audio(temp_audio_file)

        # Bitrate should be approximately 201,605 bps
        expected_bitrate = (4_536_115 * 8) / 180
        assert abs(result["bitrate"] - expected_bitrate) < 100  # Allow small variance


# =============================================================================
# Metric Rounding Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.audio
class TestMetricRounding:
    """Test that metrics are properly rounded."""

    @patch("app.services.audio_analyzer.librosa")
    @patch("app.services.audio_analyzer.sf")
    def test_metrics_rounded_correctly(
        self, mock_sf, mock_librosa, temp_audio_file
    ):
        """Test that all metrics are rounded to appropriate precision."""
        y = np.random.rand(44100 * 180)
        sr = 44100
        mock_librosa.load.return_value = (y, sr)
        mock_librosa.get_duration.return_value = 180.123456
        mock_librosa.feature.rms.return_value = np.array([[0.123456]])
        mock_librosa.feature.spectral_centroid.return_value = np.array(
            [[2543.123456]]
        )
        mock_librosa.feature.zero_crossing_rate.return_value = np.array(
            [[0.123456]]
        )
        mock_librosa.beat.beat_track.return_value = (119.876543, None)

        mock_info = Mock()
        mock_info.samplerate = 44100
        mock_info.channels = 2
        mock_sf.info.return_value = mock_info

        analyzer = AudioAnalyzer()
        result = analyzer.analyze_audio(temp_audio_file)

        # Check rounding
        assert result["duration_seconds"] == 180.12  # 2 decimal places
        assert result["rms_energy"] == 0.1235  # 4 decimal places
        assert result["spectral_centroid"] == 2543.12  # 2 decimal places
        assert result["zero_crossing_rate"] == 0.1235  # 4 decimal places
        assert result["tempo"] == 119.88  # 2 decimal places
        assert result["audio_quality_score"] == round(
            result["audio_quality_score"], 2
        )
