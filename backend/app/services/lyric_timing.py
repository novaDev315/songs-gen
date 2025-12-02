"""Beat-synced lyric timing service for video generation."""

import logging
import re
import json
from pathlib import Path
from typing import Optional, Literal

import numpy as np
import librosa

logger = logging.getLogger(__name__)

TimingMode = Literal["beat_synced", "uniform", "measures"]


class LyricTimingService:
    """Generate beat-synced timing for lyrics.

    This service analyzes audio files using librosa to detect beats, tempo,
    and musical structure, then aligns lyrics to the detected beats for
    synchronized video rendering.

    Attributes:
        _cache: In-memory cache for audio analysis results
    """

    def __init__(self):
        """Initialize the lyric timing service."""
        self._cache: dict[str, dict] = {}

    def _parse_lyrics(self, lyrics: str) -> list[dict]:
        """Parse lyrics into lines, filtering out section markers.

        Args:
            lyrics: Raw lyrics string with section markers and formatting

        Returns:
            List of lyric line dictionaries with text and emphasis flags

        Notes:
            - Filters out section markers like [Verse 1], [Chorus]
            - Filters out standalone performance directions in parentheses
            - Preserves inline performance directions as part of lyrics
            - Detects emphasis from CAPS or exclamation marks
        """
        lines = []

        for line in lyrics.strip().split("\n"):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip section markers like [Verse 1], [Chorus], etc.
            if re.match(r"^\[.*\]$", line):
                continue

            # Skip standalone performance directions in parentheses
            if re.match(r"^\(.*\)$", line):
                continue

            lines.append({
                "text": line,
                "is_emphasized": line.isupper() or line.endswith("!"),
            })

        return lines

    async def analyze_audio(self, audio_path: Path) -> dict:
        """Analyze audio file for beat timing and tempo.

        Args:
            audio_path: Path to audio file (MP3, WAV, etc.)

        Returns:
            Dictionary containing:
                - duration: Total audio duration in seconds
                - tempo: Detected tempo in BPM
                - beat_times: Array of beat timestamps
                - onset_times: Array of onset (attack) timestamps
                - beat_count: Total number of detected beats

        Raises:
            FileNotFoundError: If audio file doesn't exist
            librosa.LibrosaError: If audio file is corrupted or invalid

        Notes:
            - Uses librosa for beat detection and tempo estimation
            - Detects onsets for more precise timing points
            - Results are cached to avoid redundant analysis
        """
        logger.info(f"Analyzing audio: {audio_path}")

        # Check cache first
        cache_key = str(audio_path)
        if cache_key in self._cache:
            logger.debug(f"Using cached analysis for {audio_path}")
            return self._cache[cache_key]

        # Validate file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        try:
            # Load audio (resample to 22050 Hz for consistent processing)
            y, sr = librosa.load(str(audio_path), sr=22050)
            duration = len(y) / sr

            # Handle very short audio (less than 1 second)
            if duration < 1.0:
                logger.warning(f"Audio file too short: {duration:.2f}s")
                analysis = {
                    "duration": float(duration),
                    "tempo": 120.0,  # Default tempo
                    "beat_times": [0.0],
                    "onset_times": [0.0],
                    "beat_count": 1,
                }
                self._cache[cache_key] = analysis
                return analysis

            # Detect tempo and beats
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            # Detect onsets for more precise timing
            onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
            onset_times = librosa.frames_to_time(onset_frames, sr=sr)

            # Handle numpy scalar/array tempo values
            if isinstance(tempo, np.ndarray):
                tempo_value = float(tempo[0]) if len(tempo) > 0 else 120.0
            elif isinstance(tempo, (np.floating, np.integer)):
                tempo_value = float(tempo)
            else:
                tempo_value = float(tempo)

            # Ensure we have at least one beat
            if len(beat_times) == 0:
                logger.warning("No beats detected, using default timing")
                beat_times = np.array([0.0])

            analysis = {
                "duration": float(duration),
                "tempo": tempo_value,
                "beat_times": beat_times.tolist(),
                "onset_times": onset_times.tolist(),
                "beat_count": len(beat_times),
            }

            # Cache the result
            self._cache[cache_key] = analysis

            logger.info(
                f"Audio analysis complete: {duration:.1f}s, "
                f"{analysis['tempo']:.1f} BPM, {len(beat_times)} beats"
            )
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze audio {audio_path}: {e}")
            raise

    async def generate_timing(
        self,
        audio_path: Path,
        lyrics: str,
        mode: TimingMode = "beat_synced"
    ) -> list[dict]:
        """Generate beat-synced lyric timing.

        Args:
            audio_path: Path to audio file
            lyrics: Raw lyrics string
            mode: Timing mode - "beat_synced", "uniform", or "measures"

        Returns:
            List of timed lyric lines with start/end times

        Notes:
            - beat_synced: Aligns lyrics to detected beats (recommended)
            - uniform: Evenly distributes lyrics across duration
            - measures: Aligns lyrics to musical measures (4/4 time)
        """
        logger.info(f"Generating {mode} timing for lyrics")

        # Parse lyrics
        lines = self._parse_lyrics(lyrics)
        if not lines:
            logger.warning("No lyric lines found")
            return []

        # Analyze audio
        analysis = await self.analyze_audio(audio_path)
        duration = analysis["duration"]
        beat_times = np.array(analysis["beat_times"])

        # Generate timing based on mode
        if mode == "uniform":
            return self._uniform_timing(lines, duration)
        elif mode == "measures":
            return self._measure_timing(lines, beat_times, duration)
        else:  # beat_synced (default)
            return self._beat_synced_timing(lines, beat_times, duration)

    def _uniform_timing(self, lines: list[dict], duration: float) -> list[dict]:
        """Distribute lyrics evenly across duration.

        Args:
            lines: Parsed lyric lines
            duration: Total audio duration

        Returns:
            List of timed lyric lines

        Notes:
            - Leaves buffer at start (intro) and end (outro)
            - Each line gets equal time slot
            - Display time is 90% of slot or 4s max (whichever is less)
        """
        if not lines:
            return []

        # Leave buffer at start and end (5% of duration or 3s max)
        start_buffer = min(3.0, duration * 0.05)
        end_buffer = min(3.0, duration * 0.05)
        effective_duration = duration - start_buffer - end_buffer

        time_per_line = effective_duration / len(lines)
        display_time = min(time_per_line * 0.9, 4.0)  # Show for 90% of slot or 4s max

        timed_lines = []
        for i, line in enumerate(lines):
            start_time = start_buffer + (i * time_per_line)
            timed_lines.append({
                "text": line["text"],
                "start_time": round(start_time, 3),
                "end_time": round(start_time + display_time, 3),
                "is_emphasized": line["is_emphasized"],
            })

        return timed_lines

    def _beat_synced_timing(
        self,
        lines: list[dict],
        beat_times: np.ndarray,
        duration: float
    ) -> list[dict]:
        """Align lyrics to detected beats.

        Args:
            lines: Parsed lyric lines
            beat_times: Array of beat timestamps
            duration: Total audio duration

        Returns:
            List of timed lyric lines aligned to beats

        Notes:
            - Skips intro and outro beats
            - Falls back to uniform timing if not enough beats
            - Caps display time at 5 seconds per line
        """
        if len(beat_times) < 2:
            logger.warning("Not enough beats detected, falling back to uniform timing")
            return self._uniform_timing(lines, duration)

        # Skip first few beats (usually intro) and last few (outro)
        intro_beats = max(4, len(beat_times) // 10)
        outro_beats = max(2, len(beat_times) // 20)

        usable_beats = (
            beat_times[intro_beats:-outro_beats]
            if len(beat_times) > intro_beats + outro_beats
            else beat_times
        )

        if len(usable_beats) < len(lines):
            # Not enough beats, use uniform timing
            logger.warning(
                f"Not enough beats ({len(usable_beats)}) for lines ({len(lines)}), "
                "falling back to uniform timing"
            )
            return self._uniform_timing(lines, duration)

        # Calculate beats per line
        beats_per_line = len(usable_beats) / len(lines)

        timed_lines = []
        for i, line in enumerate(lines):
            # Get beat index for this line
            beat_idx = int(i * beats_per_line)
            next_beat_idx = min(int((i + 1) * beats_per_line), len(usable_beats) - 1)

            start_time = usable_beats[beat_idx]
            end_time = (
                usable_beats[next_beat_idx]
                if next_beat_idx > beat_idx
                else start_time + 2.0
            )

            # Cap display time at reasonable duration
            end_time = min(end_time, start_time + 5.0)

            timed_lines.append({
                "text": line["text"],
                "start_time": round(float(start_time), 3),
                "end_time": round(float(end_time), 3),
                "is_emphasized": line["is_emphasized"],
            })

        return timed_lines

    def _measure_timing(
        self,
        lines: list[dict],
        beat_times: np.ndarray,
        duration: float
    ) -> list[dict]:
        """Align lyrics to musical measures (4 beats = 1 measure in 4/4 time).

        Args:
            lines: Parsed lyric lines
            beat_times: Array of beat timestamps
            duration: Total audio duration

        Returns:
            List of timed lyric lines aligned to measures

        Notes:
            - Assumes 4/4 time signature
            - Groups beats into 4-beat measures
            - Falls back to uniform timing if not enough measures
        """
        if len(beat_times) < 8:
            logger.warning("Not enough beats for measure timing, falling back to uniform")
            return self._uniform_timing(lines, duration)

        # Group beats into measures (assuming 4/4 time)
        measures = []
        for i in range(0, len(beat_times) - 3, 4):
            measures.append({
                "start": beat_times[i],
                "end": beat_times[i + 3] if i + 3 < len(beat_times) else beat_times[-1],
            })

        if len(measures) < len(lines):
            logger.warning(
                f"Not enough measures ({len(measures)}) for lines ({len(lines)}), "
                "falling back to uniform timing"
            )
            return self._uniform_timing(lines, duration)

        # Assign 1-2 lines per measure
        measures_per_line = len(measures) / len(lines)

        timed_lines = []
        for i, line in enumerate(lines):
            measure_idx = int(i * measures_per_line)
            measure = measures[min(measure_idx, len(measures) - 1)]

            timed_lines.append({
                "text": line["text"],
                "start_time": round(float(measure["start"]), 3),
                "end_time": round(float(measure["end"]), 3),
                "is_emphasized": line["is_emphasized"],
            })

        return timed_lines

    def timing_to_json(self, timing: list[dict]) -> str:
        """Convert timing data to JSON string.

        Args:
            timing: List of timed lyric lines

        Returns:
            JSON string representation
        """
        return json.dumps(timing, indent=2)

    def timing_from_json(self, json_str: str) -> list[dict]:
        """Parse timing data from JSON string.

        Args:
            json_str: JSON string representation

        Returns:
            List of timed lyric lines

        Raises:
            json.JSONDecodeError: If JSON is invalid
        """
        return json.loads(json_str)

    async def adjust_timing(
        self,
        timing: list[dict],
        offset: float = 0.0,
        scale: float = 1.0
    ) -> list[dict]:
        """Adjust timing with offset and scale.

        Args:
            timing: List of timed lyric lines
            offset: Time offset in seconds (can be negative)
            scale: Time scale factor (1.0 = no change, >1 = slower, <1 = faster)

        Returns:
            List of adjusted timed lyric lines

        Notes:
            - Useful for fine-tuning sync after generation
            - Scale affects duration, offset shifts all times
        """
        adjusted = []
        for line in timing:
            adjusted.append({
                **line,
                "start_time": round((line["start_time"] * scale) + offset, 3),
                "end_time": round((line["end_time"] * scale) + offset, 3),
            })
        return adjusted

    def clear_cache(self) -> None:
        """Clear the audio analysis cache.

        Useful when audio files are modified or to free memory.
        """
        self._cache.clear()
        logger.info("Audio analysis cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache size and keys
        """
        return {
            "size": len(self._cache),
            "cached_files": list(self._cache.keys()),
        }
