"""Generate videos from audio files for YouTube upload."""

import json
import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class LyricLine:
    """Represents a single line of lyrics with timing."""

    text: str
    start_time: float  # seconds
    end_time: float  # seconds

    def duration(self) -> float:
        """Get duration of this lyric line."""
        return self.end_time - self.start_time


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

    def parse_lyrics(
        self,
        lyrics: str,
        audio_duration: float,
        section_markers: bool = True
    ) -> list[LyricLine]:
        """
        Parse lyrics text into timed lines.

        If lyrics contain section markers like [Verse], [Chorus], etc.,
        those are preserved. Timing is estimated based on word count and
        audio duration.

        Args:
            lyrics: Raw lyrics text
            audio_duration: Total audio duration in seconds
            section_markers: Whether to include section markers

        Returns:
            List of LyricLine objects with estimated timing
        """
        lines = []
        raw_lines = lyrics.strip().split('\n')

        # Filter out empty lines and optionally section markers
        filtered_lines = []
        for line in raw_lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's a section marker like [Verse], [Chorus]
            is_marker = re.match(r'^\[.*\]$', line)

            if is_marker:
                if section_markers:
                    filtered_lines.append(line)
            else:
                filtered_lines.append(line)

        if not filtered_lines:
            return []

        # Calculate timing based on line count
        # Reserve time for transitions
        usable_duration = audio_duration * 0.95  # Use 95% of audio
        start_offset = audio_duration * 0.025  # Start at 2.5%

        # Estimate time per line (weighted by word count)
        total_words = sum(len(line.split()) for line in filtered_lines if not line.startswith('['))
        if total_words == 0:
            total_words = len(filtered_lines)

        current_time = start_offset

        for i, line in enumerate(filtered_lines):
            is_marker = line.startswith('[')

            if is_marker:
                # Section markers get shorter display time
                line_duration = 2.0
            else:
                # Calculate duration based on word count
                word_count = len(line.split())
                line_duration = max(2.0, (word_count / total_words) * usable_duration)
                line_duration = min(line_duration, 8.0)  # Cap at 8 seconds

            end_time = min(current_time + line_duration, audio_duration)

            lines.append(LyricLine(
                text=line,
                start_time=current_time,
                end_time=end_time
            ))

            current_time = end_time

        return lines

    def get_audio_duration(self, audio_file: Path) -> float:
        """
        Get duration of an audio file using FFprobe.

        Args:
            audio_file: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(audio_file)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 180.0  # Default to 3 minutes

    def generate_lyric_video(
        self,
        audio_file: Path,
        output_file: Path,
        lyrics: str,
        title: Optional[str] = None,
        background_color: str = "black",
        text_color: str = "white",
        font_size: int = 48,
        highlight_color: str = "yellow",
        style: str = "fade"  # fade, karaoke, scroll
    ) -> Path:
        """
        Generate video with animated lyrics.

        Creates an MP4 video with lyrics displayed and animated.
        Supports multiple animation styles.

        Args:
            audio_file: Path to audio file
            output_file: Output video path (MP4)
            lyrics: Song lyrics text
            title: Optional title to display at start
            background_color: Background color (default: black)
            text_color: Main text color (default: white)
            font_size: Font size for lyrics (default: 48)
            highlight_color: Color for highlighted/active text
            style: Animation style - 'fade', 'karaoke', or 'scroll'

        Returns:
            Path to generated video file

        Raises:
            FileNotFoundError: If audio file not found
            ValueError: If video generation fails
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        try:
            logger.info(f"Generating lyric video: {audio_file}")

            # Get audio duration
            duration = self.get_audio_duration(audio_file)

            # Parse lyrics into timed lines
            lyric_lines = self.parse_lyrics(lyrics, duration)

            if not lyric_lines:
                logger.warning("No lyrics to display, generating simple video")
                return self.generate_video(audio_file, output_file, title=title)

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg filter based on style
            if style == "karaoke":
                filter_complex = self._build_karaoke_filter(
                    lyric_lines, duration, text_color, highlight_color, font_size, title
                )
            elif style == "scroll":
                filter_complex = self._build_scroll_filter(
                    lyric_lines, duration, text_color, font_size, title
                )
            else:  # fade (default)
                filter_complex = self._build_fade_filter(
                    lyric_lines, duration, text_color, font_size, title
                )

            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c={background_color}:s=1920x1080:d={duration}',
                '-i', str(audio_file),
                '-filter_complex', filter_complex,
                '-map', '[out]',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-y',
                str(output_file)
            ]

            logger.info(f"Running FFmpeg for lyric video generation")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # 10 minute timeout
            )

            if not output_file.exists():
                raise ValueError(f"Lyric video generation failed: {output_file} not created")

            file_size_mb = output_file.stat().st_size / (1024 * 1024)
            logger.info(f"Lyric video generated successfully: {output_file} ({file_size_mb:.2f} MB)")

            return output_file

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error during lyric video generation: {e.stderr}")
            # Fall back to simple video
            logger.info("Falling back to simple video generation")
            return self.generate_video(audio_file, output_file, title=title)
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout during lyric video generation")
            raise ValueError("Video generation timed out")
        except Exception as e:
            logger.error(f"Lyric video generation error: {e}")
            raise

    def _escape_text_for_ffmpeg(self, text: str) -> str:
        """Escape special characters for FFmpeg drawtext filter."""
        # Escape characters that have special meaning in FFmpeg
        text = text.replace("\\", "\\\\\\\\")
        text = text.replace("'", "'\\\\\\''")
        text = text.replace(":", "\\:")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        text = text.replace("%", "\\%")
        return text

    def _build_fade_filter(
        self,
        lyric_lines: list[LyricLine],
        duration: float,
        text_color: str,
        font_size: int,
        title: Optional[str]
    ) -> str:
        """
        Build FFmpeg filter for fade-in/fade-out lyric animation.

        Each lyric line fades in at its start time and fades out at end time.
        """
        filters = ["[0:v]"]

        # Add title at the beginning if provided
        if title:
            escaped_title = self._escape_text_for_ffmpeg(title)
            filters.append(
                f"drawtext=text='{escaped_title}':"
                f"fontcolor={text_color}:fontsize={font_size + 24}:"
                f"x=(w-text_w)/2:y=h/4:"
                f"enable='between(t,0,3)':alpha='if(lt(t,1),t,if(lt(t,2),1,3-t))'"
            )
            filters.append(",")

        # Add each lyric line with fade effect
        for i, line in enumerate(lyric_lines):
            escaped_text = self._escape_text_for_ffmpeg(line.text)
            start = line.start_time
            end = line.end_time
            fade_duration = 0.5

            # Calculate alpha expression for fade in/out
            # Fade in during first 0.5s, stay visible, fade out during last 0.5s
            alpha_expr = (
                f"if(lt(t-{start},{fade_duration}),(t-{start})/{fade_duration},"
                f"if(gt(t,{end - fade_duration}),({end}-t)/{fade_duration},1))"
            )

            # Determine if this is a section marker
            is_marker = line.text.startswith('[')
            y_position = "h/3" if is_marker else "h/2"
            actual_font_size = font_size - 8 if is_marker else font_size

            filters.append(
                f"drawtext=text='{escaped_text}':"
                f"fontcolor={text_color}:fontsize={actual_font_size}:"
                f"x=(w-text_w)/2:y={y_position}:"
                f"enable='between(t,{start},{end})':"
                f"alpha='{alpha_expr}'"
            )

            if i < len(lyric_lines) - 1:
                filters.append(",")

        filters.append("[out]")
        return "".join(filters)

    def _build_karaoke_filter(
        self,
        lyric_lines: list[LyricLine],
        duration: float,
        text_color: str,
        highlight_color: str,
        font_size: int,
        title: Optional[str]
    ) -> str:
        """
        Build FFmpeg filter for karaoke-style lyric animation.

        Shows current line with word-by-word highlighting.
        """
        # For karaoke, we show current and next line, highlighting current
        filters = ["[0:v]"]

        # Add title
        if title:
            escaped_title = self._escape_text_for_ffmpeg(title)
            filters.append(
                f"drawtext=text='{escaped_title}':"
                f"fontcolor={text_color}:fontsize={font_size + 24}:"
                f"x=(w-text_w)/2:y=h/4:"
                f"enable='between(t,0,3)'"
            )
            filters.append(",")

        for i, line in enumerate(lyric_lines):
            if line.text.startswith('['):
                continue  # Skip section markers for karaoke

            escaped_text = self._escape_text_for_ffmpeg(line.text)
            start = line.start_time
            end = line.end_time

            # Main line (highlighted)
            filters.append(
                f"drawtext=text='{escaped_text}':"
                f"fontcolor={highlight_color}:fontsize={font_size}:"
                f"x=(w-text_w)/2:y=h/2:"
                f"enable='between(t,{start},{end})'"
            )

            # Show next line preview (if exists)
            next_line = None
            for j in range(i + 1, len(lyric_lines)):
                if not lyric_lines[j].text.startswith('['):
                    next_line = lyric_lines[j]
                    break

            if next_line:
                escaped_next = self._escape_text_for_ffmpeg(next_line.text)
                filters.append(",")
                filters.append(
                    f"drawtext=text='{escaped_next}':"
                    f"fontcolor={text_color}:fontsize={font_size - 12}:"
                    f"x=(w-text_w)/2:y=h/2+{font_size + 20}:"
                    f"enable='between(t,{start},{end})':alpha=0.5"
                )

            if i < len(lyric_lines) - 1:
                filters.append(",")

        filters.append("[out]")
        return "".join(filters)

    def _build_scroll_filter(
        self,
        lyric_lines: list[LyricLine],
        duration: float,
        text_color: str,
        font_size: int,
        title: Optional[str]
    ) -> str:
        """
        Build FFmpeg filter for scrolling lyrics.

        All lyrics scroll from bottom to top like credits.
        """
        # Combine all lyrics into one text block
        all_text = "\n\n".join(line.text for line in lyric_lines)
        escaped_text = self._escape_text_for_ffmpeg(all_text)

        # Calculate scroll speed
        # Text should scroll from bottom to top over the duration
        line_count = len(lyric_lines)
        total_height = line_count * (font_size + 30) + 1080  # Including screen height

        filters = [
            f"[0:v]drawtext=text='{escaped_text}':"
            f"fontcolor={text_color}:fontsize={font_size}:"
            f"x=(w-text_w)/2:"
            f"y=h-({total_height}*t/{duration})+h:"
            f"line_spacing=30"
            f"[out]"
        ]

        return "".join(filters)

    def generate_simple_lyric_image_video(
        self,
        audio_file: Path,
        output_file: Path,
        lyrics: str,
        title: Optional[str] = None,
        background_color: str = "black",
        text_color: str = "white"
    ) -> Path:
        """
        Generate a simple video with static lyrics display.

        Fallback method that creates a video with all lyrics displayed
        as a static image (good for when complex animations fail).

        Args:
            audio_file: Path to audio file
            output_file: Output video path
            lyrics: Song lyrics
            title: Optional title
            background_color: Background color
            text_color: Text color

        Returns:
            Path to generated video
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        try:
            # Create a temporary image with lyrics
            # Truncate lyrics to fit
            lyrics_preview = lyrics[:1000] if len(lyrics) > 1000 else lyrics
            display_text = f"{title}\n\n{lyrics_preview}" if title else lyrics_preview
            escaped_text = self._escape_text_for_ffmpeg(display_text.replace('\n', '\\n'))

            duration = self.get_audio_duration(audio_file)

            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c={background_color}:s=1920x1080:d={duration}',
                '-i', str(audio_file),
                '-filter_complex',
                f"[0:v]drawtext=text='{escaped_text}':"
                f"fontcolor={text_color}:fontsize=32:"
                f"x=100:y=100:line_spacing=10[out]",
                '-map', '[out]',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-y',
                str(output_file)
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            return output_file

        except Exception as e:
            logger.error(f"Simple lyric video failed: {e}")
            # Final fallback to waveform
            return self.generate_video(audio_file, output_file)


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
