"""Audio analysis service for extracting features from audio files.

Uses librosa for audio analysis including beat detection, tempo estimation,
key detection, and other musical features.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Lazy import librosa to avoid startup overhead
_librosa = None


def _get_librosa():
    """Lazy load librosa."""
    global _librosa
    if _librosa is None:
        try:
            import librosa
            _librosa = librosa
        except ImportError:
            logger.warning("librosa not installed. Audio analysis will be limited.")
            return None
    return _librosa


@dataclass
class AudioFeatures:
    """Container for extracted audio features."""
    duration: float  # Duration in seconds
    tempo: float  # BPM
    beat_times: list[float]  # Beat timestamps in seconds
    key: Optional[str]  # Musical key (C, D#, etc.)
    mode: Optional[str]  # Major or Minor
    energy: float  # 0-1 energy level
    danceability: float  # 0-1 danceability score
    spectral_centroid_mean: float  # Brightness indicator
    rms_mean: float  # Average loudness


class AudioAnalyzer:
    """Analyzes audio files to extract musical features."""

    def __init__(self, sample_rate: int = 22050):
        """Initialize analyzer with sample rate.

        Args:
            sample_rate: Sample rate for audio loading. Default 22050 for librosa.
        """
        self.sample_rate = sample_rate
        self._key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    async def analyze(self, audio_path: Path) -> Optional[AudioFeatures]:
        """Analyze an audio file and extract features.

        Args:
            audio_path: Path to the audio file.

        Returns:
            AudioFeatures object with extracted features, or None if analysis fails.
        """
        librosa = _get_librosa()
        if librosa is None:
            logger.error("librosa not available for audio analysis")
            return None

        try:
            logger.info(f"Analyzing audio: {audio_path}")

            # Load audio
            y, sr = librosa.load(str(audio_path), sr=self.sample_rate)
            duration = len(y) / sr

            # Beat detection
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr).tolist()

            # Key detection using chromagram
            key, mode = self._detect_key(y, sr, librosa)

            # Energy analysis
            rms = librosa.feature.rms(y=y)[0]
            rms_mean = float(np.mean(rms))
            energy = min(1.0, rms_mean * 10)  # Normalize to 0-1

            # Spectral analysis for brightness
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_centroid_mean = float(np.mean(spectral_centroid))

            # Danceability (simplified: based on beat strength and tempo)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            danceability = self._calculate_danceability(tempo, onset_env)

            features = AudioFeatures(
                duration=duration,
                tempo=float(tempo),
                beat_times=beat_times,
                key=key,
                mode=mode,
                energy=energy,
                danceability=danceability,
                spectral_centroid_mean=spectral_centroid_mean,
                rms_mean=rms_mean
            )

            logger.info(
                f"Audio analysis complete: {duration:.1f}s, {tempo:.0f}BPM, "
                f"key={key} {mode}, energy={energy:.2f}"
            )

            return features

        except Exception as e:
            logger.error(f"Audio analysis failed for {audio_path}: {e}", exc_info=True)
            return None

    def _detect_key(self, y: np.ndarray, sr: int, librosa) -> tuple[Optional[str], Optional[str]]:
        """Detect musical key using chromagram analysis.

        Args:
            y: Audio time series
            sr: Sample rate
            librosa: librosa module

        Returns:
            Tuple of (key_name, mode) e.g. ('C', 'Major')
        """
        try:
            # Compute chromagram
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_mean = np.mean(chroma, axis=1)

            # Find dominant pitch class
            key_idx = int(np.argmax(chroma_mean))
            key_name = self._key_names[key_idx]

            # Simple major/minor detection based on third interval
            third_major = (key_idx + 4) % 12
            third_minor = (key_idx + 3) % 12

            if chroma_mean[third_major] > chroma_mean[third_minor]:
                mode = "Major"
            else:
                mode = "Minor"

            return key_name, mode

        except Exception as e:
            logger.warning(f"Key detection failed: {e}")
            return None, None

    def _calculate_danceability(self, tempo: float, onset_env: np.ndarray) -> float:
        """Calculate danceability score.

        Based on tempo being in danceable range (100-130 BPM)
        and consistency of onsets.

        Args:
            tempo: Detected tempo in BPM
            onset_env: Onset strength envelope

        Returns:
            Danceability score between 0 and 1
        """
        # Tempo factor: peaks at ~120 BPM
        tempo_factor = 1.0 - abs(tempo - 120) / 120
        tempo_factor = max(0, min(1, tempo_factor))

        # Rhythm consistency factor
        onset_std = np.std(onset_env)
        onset_mean = np.mean(onset_env)
        consistency = onset_mean / (onset_std + 0.001)
        consistency_factor = min(1.0, consistency / 5)

        # Combined score
        danceability = 0.6 * tempo_factor + 0.4 * consistency_factor
        return float(danceability)

    def get_beat_aligned_timestamps(
        self,
        features: AudioFeatures,
        num_timestamps: int
    ) -> list[float]:
        """Get timestamps aligned to beats.

        Useful for syncing lyrics or visual effects to music.

        Args:
            features: Extracted audio features
            num_timestamps: Number of timestamps needed

        Returns:
            List of beat-aligned timestamps
        """
        if not features.beat_times or num_timestamps <= 0:
            # Fall back to uniform distribution
            return [
                i * features.duration / num_timestamps
                for i in range(num_timestamps)
            ]

        beat_times = features.beat_times

        if len(beat_times) >= num_timestamps:
            # Select evenly spaced beats
            indices = np.linspace(0, len(beat_times) - 1, num_timestamps, dtype=int)
            return [beat_times[i] for i in indices]
        else:
            # Interpolate between beats
            timestamps = []
            for i in range(num_timestamps):
                position = i * (len(beat_times) - 1) / (num_timestamps - 1)
                lower_idx = int(position)
                upper_idx = min(lower_idx + 1, len(beat_times) - 1)
                fraction = position - lower_idx

                interpolated = (
                    beat_times[lower_idx] * (1 - fraction) +
                    beat_times[upper_idx] * fraction
                )
                timestamps.append(interpolated)

            return timestamps


# Singleton instance
_audio_analyzer: Optional[AudioAnalyzer] = None


def get_audio_analyzer() -> AudioAnalyzer:
    """Get singleton AudioAnalyzer instance."""
    global _audio_analyzer
    if _audio_analyzer is None:
        _audio_analyzer = AudioAnalyzer()
    return _audio_analyzer
