"""Song evaluation service for quality scoring."""

import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.evaluation import Evaluation
from app.models.song import Song
from app.services.audio_analyzer import get_audio_analyzer

logger = logging.getLogger(__name__)
settings = get_settings()


class EvaluatorService:
    """Service for evaluating song quality."""

    def __init__(self) -> None:
        """Initialize the evaluator service."""
        self.analyzer = get_audio_analyzer()
        self.download_folder = Path(settings.DOWNLOAD_FOLDER)
        self.download_folder.mkdir(parents=True, exist_ok=True)

    async def evaluate_song(self, song_id: str) -> Evaluation:
        """Evaluate a song's quality.

        Args:
            song_id: ID of the song to evaluate

        Returns:
            Evaluation object with quality scores

        Raises:
            ValueError: If song not found
            FileNotFoundError: If audio file not found
        """
        async with AsyncSessionLocal() as db:
            # Get song
            result = await db.execute(
                select(Song).where(Song.id == song_id)
            )
            song = result.scalar_one_or_none()

            if not song:
                raise ValueError(f"Song not found: {song_id}")

            # Get audio file
            audio_file = self.download_folder / f"{song_id}.mp3"
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

            logger.info(f"Evaluating song {song_id}")

            # Analyze audio
            analysis = self.analyzer.analyze_audio(audio_file)

            # Check for existing evaluation
            eval_result = await db.execute(
                select(Evaluation).where(Evaluation.song_id == song_id)
            )
            existing_eval = eval_result.scalar_one_or_none()

            # Determine if approved based on quality score
            audio_quality_score = analysis.get("audio_quality_score", 0)
            is_approved = audio_quality_score >= settings.MIN_QUALITY_SCORE

            if existing_eval:
                # Update existing evaluation
                existing_eval.audio_quality_score = audio_quality_score
                existing_eval.duration_seconds = analysis.get("duration_seconds")
                existing_eval.file_size_mb = analysis.get("file_size_mb")
                existing_eval.sample_rate = analysis.get("sample_rate")
                existing_eval.bitrate = analysis.get("bitrate")
                existing_eval.approved = is_approved
                evaluation = existing_eval
            else:
                # Create new evaluation
                evaluation = Evaluation(
                    song_id=song_id,
                    audio_quality_score=audio_quality_score,
                    duration_seconds=analysis.get("duration_seconds"),
                    file_size_mb=analysis.get("file_size_mb"),
                    sample_rate=analysis.get("sample_rate"),
                    bitrate=analysis.get("bitrate"),
                    approved=is_approved,
                )
                db.add(evaluation)

            # Update song status
            song.status = "evaluated"
            await db.commit()
            await db.commit()  # Second commit to ensure all changes are persisted

            logger.info(
                f"Song {song_id} evaluated: "
                f"score={audio_quality_score:.1f}, approved={is_approved}"
            )

            return evaluation


# Global instance
_evaluator: Optional[EvaluatorService] = None


def get_evaluator() -> EvaluatorService:
    """Get the global evaluator service instance.

    Returns:
        The singleton EvaluatorService instance
    """
    global _evaluator
    if _evaluator is None:
        _evaluator = EvaluatorService()
    return _evaluator
