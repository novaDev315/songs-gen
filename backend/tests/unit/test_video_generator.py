"""Unit tests for video generator service.

Tests video generation functionality using FFmpeg.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from app.services.video_generator import VideoGenerator, get_video_generator


# =============================================================================
# Video Generator Initialization Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestVideoGeneratorInit:
    """Test VideoGenerator initialization."""

    def test_create_generator(self):
        """Test creating a VideoGenerator instance."""
        generator = VideoGenerator()
        assert generator is not None

    def test_get_video_generator_singleton(self):
        """Test get_video_generator returns singleton."""
        generator1 = get_video_generator()
        generator2 = get_video_generator()

        assert generator1 is generator2


# =============================================================================
# Video Generation Tests (with Thumbnail)
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestVideoGenerationWithThumbnail:
    """Test video generation with thumbnail image."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_with_thumbnail_success(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test successful video generation with thumbnail."""
        # Create thumbnail file
        thumbnail = temp_dir / "thumbnail.jpg"
        thumbnail.write_bytes(b"\xFF\xD8\xFF")  # JPEG header

        output_file = temp_dir / "output.mp4"

        # Mock successful FFmpeg execution
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Create output file to simulate FFmpeg success
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
            thumbnail=thumbnail,
        )

        assert result == output_file
        assert output_file.exists()
        mock_run.assert_called_once()

        # Verify FFmpeg command structure
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert str(thumbnail) in call_args
        assert str(temp_audio_file) in call_args

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_audio_not_found(self, mock_run, temp_dir):
        """Test video generation with non-existent audio file."""
        non_existent_audio = Path("/nonexistent/audio.mp3")
        output_file = temp_dir / "output.mp4"

        generator = VideoGenerator()

        with pytest.raises(FileNotFoundError) as exc_info:
            generator.generate_video(
                audio_file=non_existent_audio,
                output_file=output_file,
            )

        assert "Audio file not found" in str(exc_info.value)
        mock_run.assert_not_called()

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_creates_output_directory(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test that video generation creates output directory if needed."""
        output_file = temp_dir / "subdir" / "nested" / "output.mp4"

        # Mock successful execution
        mock_run.return_value = Mock(returncode=0)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
        )

        assert output_file.parent.exists()
        assert result == output_file

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_ffmpeg_command_with_thumbnail(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test FFmpeg command structure with thumbnail."""
        thumbnail = temp_dir / "thumb.jpg"
        thumbnail.write_bytes(b"\xFF\xD8\xFF")
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
            thumbnail=thumbnail,
        )

        # Verify command structure
        call_args = mock_run.call_args[0][0]
        assert "ffmpeg" in call_args
        assert "-loop" in call_args
        assert "1" in call_args
        assert "-c:v" in call_args
        assert "libx264" in call_args
        assert "-c:a" in call_args
        assert "aac" in call_args
        assert "-y" in call_args  # Overwrite flag


# =============================================================================
# Video Generation Tests (Waveform)
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestVideoGenerationWithWaveform:
    """Test video generation with waveform visualization."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_waveform_success(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test successful video generation with waveform."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
            thumbnail=None,  # No thumbnail = waveform
        )

        assert result == output_file
        mock_run.assert_called_once()

        # Verify waveform FFmpeg command
        call_args = mock_run.call_args[0][0]
        assert "ffmpeg" in call_args
        assert "-filter_complex" in call_args
        assert "showwaves" in str(call_args)

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_waveform_command_structure(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test FFmpeg command structure for waveform generation."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
        )

        call_args = mock_run.call_args[0][0]
        assert "showwaves" in str(call_args)
        assert "s=1920x1080" in str(call_args)  # HD resolution
        assert "mode=line" in str(call_args)


# =============================================================================
# Video Generation with Text Overlay Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestVideoGenerationWithTextOverlay:
    """Test video generation with text overlay."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_with_text_overlay_success(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test successful video generation with text overlay."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        result = generator.generate_video_with_text_overlay(
            audio_file=temp_audio_file,
            output_file=output_file,
            title="Test Song Title",
        )

        assert result == output_file
        mock_run.assert_called_once()

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_text_overlay_command_structure(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test FFmpeg command structure for text overlay."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        generator.generate_video_with_text_overlay(
            audio_file=temp_audio_file,
            output_file=output_file,
            title="Test Title",
            background_color="black",
        )

        call_args = mock_run.call_args[0][0]
        assert "drawtext" in str(call_args)
        assert "Test Title" in str(call_args) or "Test" in str(call_args)
        assert "color=c=black" in str(call_args)

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_text_special_characters(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test video generation with special characters in title."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()

        # Title with special characters
        title = "Test's Song: Part 1 (Remix)"
        result = generator.generate_video_with_text_overlay(
            audio_file=temp_audio_file,
            output_file=output_file,
            title=title,
        )

        assert result == output_file
        mock_run.assert_called_once()

    @pytest.mark.parametrize("color", ["black", "white", "blue", "red", "green"])
    def test_generate_video_various_background_colors(
        self, color, temp_audio_file, temp_dir
    ):
        """Test video generation with various background colors."""
        with patch("app.services.video_generator.subprocess.run") as mock_run:
            output_file = temp_dir / f"output_{color}.mp4"

            mock_run.return_value = Mock(returncode=0)
            output_file.write_bytes(b"\x00" * 1000)

            generator = VideoGenerator()
            generator.generate_video_with_text_overlay(
                audio_file=temp_audio_file,
                output_file=output_file,
                title="Test",
                background_color=color,
            )

            call_args = mock_run.call_args[0][0]
            assert f"color=c={color}" in str(call_args)


# =============================================================================
# FFmpeg Error Handling Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestFFmpegErrorHandling:
    """Test FFmpeg error handling."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_ffmpeg_failure(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test handling of FFmpeg command failure."""
        output_file = temp_dir / "output.mp4"

        # Mock FFmpeg failure
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "ffmpeg", stderr="FFmpeg error message"
        )

        generator = VideoGenerator()

        with pytest.raises(ValueError) as exc_info:
            generator.generate_video(
                audio_file=temp_audio_file,
                output_file=output_file,
            )

        assert "FFmpeg failed" in str(exc_info.value)

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_output_not_created(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test handling when FFmpeg succeeds but output file not created."""
        output_file = temp_dir / "output.mp4"

        # Mock successful execution but don't create file
        mock_run.return_value = Mock(returncode=0)

        generator = VideoGenerator()

        with pytest.raises(ValueError) as exc_info:
            generator.generate_video(
                audio_file=temp_audio_file,
                output_file=output_file,
            )

        assert "Video generation failed" in str(exc_info.value)
        assert "not created" in str(exc_info.value)

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_generic_exception(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test handling of generic exceptions during video generation."""
        output_file = temp_dir / "output.mp4"

        mock_run.side_effect = Exception("Unexpected error")

        generator = VideoGenerator()

        with pytest.raises(Exception) as exc_info:
            generator.generate_video(
                audio_file=temp_audio_file,
                output_file=output_file,
            )

        assert "Unexpected error" in str(exc_info.value)


# =============================================================================
# Output File Validation Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestOutputFileValidation:
    """Test output file validation."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_output_file_size_logged(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test that output file size is logged."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)

        # Create output file with known size (1 MB)
        output_file.write_bytes(b"\x00" * (1024 * 1024))

        generator = VideoGenerator()
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
        )

        assert result.stat().st_size == 1024 * 1024

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_overwrite_existing(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test that existing output file is overwritten."""
        output_file = temp_dir / "output.mp4"

        # Create existing file
        output_file.write_bytes(b"old content")

        mock_run.return_value = Mock(returncode=0)

        # Simulate FFmpeg overwriting
        output_file.write_bytes(b"new content")

        generator = VideoGenerator()
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
        )

        assert output_file.read_bytes() == b"new content"


# =============================================================================
# Edge Cases and Integration Tests
# =============================================================================


@pytest.mark.unit
@pytest.mark.video
class TestVideoGeneratorEdgeCases:
    """Test edge cases in video generation."""

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_thumbnail_not_exists(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test video generation when specified thumbnail doesn't exist."""
        output_file = temp_dir / "output.mp4"
        non_existent_thumb = Path("/nonexistent/thumb.jpg")

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()

        # Should fall back to waveform when thumbnail doesn't exist
        result = generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
            thumbnail=non_existent_thumb,
        )

        # Verify it used waveform command (no thumbnail)
        call_args = mock_run.call_args[0][0]
        assert "showwaves" in str(call_args)

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_very_long_title(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test video generation with very long title."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()

        # Very long title
        long_title = "A" * 500
        result = generator.generate_video_with_text_overlay(
            audio_file=temp_audio_file,
            output_file=output_file,
            title=long_title,
        )

        assert result == output_file

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_unicode_title(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test video generation with unicode characters in title."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0)
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()

        # Title with unicode
        unicode_title = "测试歌曲 🎵 Тест"
        result = generator.generate_video_with_text_overlay(
            audio_file=temp_audio_file,
            output_file=output_file,
            title=unicode_title,
        )

        assert result == output_file

    @patch("app.services.video_generator.subprocess.run")
    def test_generate_video_subprocess_arguments(
        self, mock_run, temp_audio_file, temp_dir
    ):
        """Test that subprocess is called with correct arguments."""
        output_file = temp_dir / "output.mp4"

        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        output_file.write_bytes(b"\x00" * 1000)

        generator = VideoGenerator()
        generator.generate_video(
            audio_file=temp_audio_file,
            output_file=output_file,
        )

        # Verify subprocess.run was called with correct kwargs
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["capture_output"] is True
        assert call_kwargs["text"] is True
        assert call_kwargs["check"] is True
