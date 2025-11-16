"""Audio analysis service using librosa."""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import librosa
import soundfile as sf

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """Analyzes audio files for quality metrics."""

    def analyze_audio(self, file_path: Path) -> Dict[str, Any]:
        """Analyze audio file and return quality metrics.

        Args:
            file_path: Path to the audio file

        Returns:
            Dictionary containing audio quality metrics:
                - duration_seconds: Length of audio in seconds
                - file_size_mb: File size in megabytes
                - sample_rate: Audio sample rate in Hz
                - bitrate: Estimated bitrate in bits per second
                - channels: Number of audio channels
                - rms_energy: RMS energy level
                - spectral_centroid: Average spectral centroid
                - zero_crossing_rate: Average zero-crossing rate
                - tempo: Estimated tempo in BPM
                - audio_quality_score: Overall quality score (0-100)

        Raises:
            FileNotFoundError: If audio file doesn't exist
            Exception: If audio analysis fails
        """
        try:
            logger.info(f"Analyzing audio: {file_path}")

            # Load audio
            y, sr = librosa.load(str(file_path), sr=None)

            # Basic metrics
            duration = librosa.get_duration(y=y, sr=sr)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)

            # Get audio info with soundfile for more details
            info = sf.info(str(file_path))
            sample_rate = info.samplerate
            channels = info.channels

            # Calculate bitrate (approximate)
            bitrate = int(
                (file_path.stat().st_size * 8) / duration
            )  # bits per second

            # Advanced metrics
            rms_energy = float(librosa.feature.rms(y=y).mean())
            spectral_centroid = float(
                librosa.feature.spectral_centroid(y=y, sr=sr).mean()
            )
            zero_crossing_rate = float(librosa.feature.zero_crossing_rate(y).mean())

            # Tempo and beat detection
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            # Calculate quality score (0-100)
            quality_score = self.calculate_quality_score(
                duration=duration,
                file_size_mb=file_size_mb,
                sample_rate=sample_rate,
                bitrate=bitrate,
                rms_energy=rms_energy,
            )

            metrics = {
                "duration_seconds": round(duration, 2),
                "file_size_mb": round(file_size_mb, 2),
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "channels": channels,
                "rms_energy": round(rms_energy, 4),
                "spectral_centroid": round(spectral_centroid, 2),
                "zero_crossing_rate": round(zero_crossing_rate, 4),
                "tempo": round(float(tempo), 2),
                "audio_quality_score": round(quality_score, 2),
            }

            logger.info(f"Analysis complete: {metrics}")
            return metrics

        except Exception as e:
            logger.error(f"Error analyzing audio {file_path}: {e}", exc_info=True)
            raise

    def calculate_quality_score(
        self,
        duration: float,
        file_size_mb: float,
        sample_rate: int,
        bitrate: int,
        rms_energy: float,
    ) -> float:
        """Calculate overall quality score (0-100).

        Args:
            duration: Audio duration in seconds
            file_size_mb: File size in megabytes
            sample_rate: Sample rate in Hz
            bitrate: Bitrate in bits per second
            rms_energy: RMS energy level

        Returns:
            Quality score from 0 to 100
        """
        score = 0.0

        # Duration score (prefer 2-5 minutes)
        if 120 <= duration <= 300:
            score += 20
        elif 60 <= duration < 120 or 300 < duration <= 360:
            score += 15
        else:
            score += 10

        # Sample rate score
        if sample_rate >= 44100:
            score += 25
        elif sample_rate >= 32000:
            score += 20
        else:
            score += 15

        # Bitrate score
        if bitrate >= 256000:  # 256 kbps or higher
            score += 25
        elif bitrate >= 192000:  # 192 kbps
            score += 20
        elif bitrate >= 128000:  # 128 kbps
            score += 15
        else:
            score += 10

        # File size score (relative to duration)
        expected_size = (bitrate / 8) * duration / (1024 * 1024)  # Expected MB
        size_ratio = file_size_mb / expected_size if expected_size > 0 else 0

        if 0.8 <= size_ratio <= 1.2:  # Within 20% of expected
            score += 15
        elif 0.6 <= size_ratio < 0.8 or 1.2 < size_ratio <= 1.4:
            score += 10
        else:
            score += 5

        # RMS energy score (check for silence or clipping)
        if 0.05 <= rms_energy <= 0.5:  # Healthy range
            score += 15
        elif 0.02 <= rms_energy < 0.05 or 0.5 < rms_energy <= 0.7:
            score += 10
        else:
            score += 5

        return min(score, 100.0)


# Global instance
_audio_analyzer: Optional[AudioAnalyzer] = None


def get_audio_analyzer() -> AudioAnalyzer:
    """Get the global audio analyzer instance.

    Returns:
        The singleton AudioAnalyzer instance
    """
    global _audio_analyzer
    if _audio_analyzer is None:
        _audio_analyzer = AudioAnalyzer()
    return _audio_analyzer
