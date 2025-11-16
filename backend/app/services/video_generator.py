"""Generate videos from audio files for YouTube upload."""

import logging
from pathlib import Path
from typing import Optional
import subprocess

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Generates videos from audio files using FFmpeg."""

    def generate_video(
        self,
        audio_file: Path,
        output_file: Path,
        thumbnail: Optional[Path] = None,
        title: Optional[str] = None
    ) -> Path:
        """
        Generate video from audio file.

        Creates an MP4 video from an audio file (MP3/WAV). If a thumbnail image
        is provided, it will be used as a static image. Otherwise, generates a
        waveform visualization.

        Args:
            audio_file: Path to audio file (MP3, WAV, etc.)
            output_file: Output video path (MP4)
            thumbnail: Optional image for video thumbnail (JPG, PNG)
            title: Optional title overlay (not currently used)

        Returns:
            Path to generated video file

        Raises:
            FileNotFoundError: If audio file not found
            ValueError: If video generation fails
            subprocess.CalledProcessError: If FFmpeg command fails
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        try:
            logger.info(f"Generating video from audio: {audio_file}")

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # FFmpeg command to create video from audio
            if thumbnail and thumbnail.exists():
                # Use provided thumbnail as static image
                cmd = [
                    'ffmpeg',
                    '-loop', '1',                    # Loop image
                    '-i', str(thumbnail),            # Input image
                    '-i', str(audio_file),           # Input audio
                    '-c:v', 'libx264',              # Video codec
                    '-tune', 'stillimage',          # Optimize for still image
                    '-c:a', 'aac',                  # Audio codec
                    '-b:a', '192k',                 # Audio bitrate
                    '-pix_fmt', 'yuv420p',          # Pixel format for compatibility
                    '-shortest',                     # End when shortest input ends
                    '-y',                           # Overwrite output
                    str(output_file)
                ]
            else:
                # Generate video with waveform visualization
                cmd = [
                    'ffmpeg',
                    '-i', str(audio_file),
                    '-filter_complex',
                    # Create waveform visualization
                    '[0:a]showwaves=s=1920x1080:mode=line:colors=white,format=yuv420p[v]',
                    '-map', '[v]',                  # Map video output
                    '-map', '0:a',                  # Map audio
                    '-c:v', 'libx264',              # Video codec
                    '-c:a', 'aac',                  # Audio codec
                    '-b:a', '192k',                 # Audio bitrate
                    '-y',                           # Overwrite output
                    str(output_file)
                ]

            # Execute FFmpeg
            logger.info(f"Running FFmpeg command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            if not output_file.exists():
                raise ValueError(f"Video generation failed: {output_file} not created")

            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Video generated successfully: {output_file} ({file_size_mb:.2f} MB)")

            return output_file

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise ValueError(f"FFmpeg failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise

    def generate_video_with_text_overlay(
        self,
        audio_file: Path,
        output_file: Path,
        title: str,
        background_color: str = 'black'
    ) -> Path:
        """
        Generate video with text overlay on colored background.

        Creates an MP4 video with the song title displayed on a colored background.

        Args:
            audio_file: Path to audio file
            output_file: Output video path (MP4)
            title: Title text to display
            background_color: Background color (black, white, blue, etc.)

        Returns:
            Path to generated video file

        Raises:
            FileNotFoundError: If audio file not found
            ValueError: If video generation fails
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        try:
            logger.info(f"Generating video with text overlay: {title}")

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Escape special characters in title for FFmpeg
            escaped_title = title.replace("'", "'\\\\\\''").replace(":", "\\:")

            # FFmpeg command with text overlay
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c={background_color}:s=1920x1080:d=300',  # Color background
                '-i', str(audio_file),              # Input audio
                '-filter_complex',
                # Add text overlay
                f"[0:v]drawtext=text='{escaped_title}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2[v]",
                '-map', '[v]',
                '-map', '1:a',                      # Map audio from second input
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-y',
                str(output_file)
            ]

            # Execute FFmpeg
            logger.info(f"Running FFmpeg with text overlay")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            if not output_file.exists():
                raise ValueError(f"Video generation failed: {output_file} not created")

            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Video with text generated successfully: {output_file} ({file_size_mb:.2f} MB)")

            return output_file

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error: {e.stderr}")
            raise ValueError(f"FFmpeg failed: {e.stderr}")
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            raise


# Global instance
_video_generator: Optional[VideoGenerator] = None


def get_video_generator() -> VideoGenerator:
    """Get the global video generator instance.

    Returns:
        The singleton VideoGenerator instance
    """
    global _video_generator
    if _video_generator is None:
        _video_generator = VideoGenerator()
    return _video_generator
