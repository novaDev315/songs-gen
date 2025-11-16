"""Evaluation service to analyze and score downloaded songs."""

import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.song import Song
from app.models.evaluation import Evaluation
from app.services.audio_analyzer import get_audio_analyzer
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()


class EvaluatorService:
    """Service to evaluate downloaded songs."""

    def __init__(self):
        self.analyzer = get_audio_analyzer()
        self.download_folder = Path(settings.DOWNLOAD_FOLDER)

    async def evaluate_song(self, song_id: str) -> Evaluation:
        """Evaluate a downloaded song.

        Args:
            song_id: Unique song identifier

        Returns:
            Evaluation record with quality metrics

        Raises:
            ValueError: If song not found
            FileNotFoundError: If audio file not found
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get song
                result = await db.execute(select(Song).where(Song.id == song_id))
                song = result.scalar_one_or_none()

                if not song:
                    raise ValueError(f"Song not found: {song_id}")

                # Find audio file
                audio_file = self.download_folder / f"{song_id}.mp3"
                if not audio_file.exists():
                    raise FileNotFoundError(f"Audio file not found: {audio_file}")

                logger.info(f"Evaluating song: {song_id}")

                # Analyze audio
                metrics = self.analyzer.analyze_audio(audio_file)

                # Check if evaluation already exists
                result = await db.execute(
                    select(Evaluation).where(Evaluation.song_id == song_id)
                )
                evaluation = result.scalar_one_or_none()

                if evaluation:
                    # Update existing
                    evaluation.audio_quality_score = metrics["audio_quality_score"]
                    evaluation.duration_seconds = metrics["duration_seconds"]
                    evaluation.file_size_mb = metrics["file_size_mb"]
                    evaluation.sample_rate = metrics["sample_rate"]
                    evaluation.bitrate = metrics["bitrate"]
                    evaluation.evaluated_at = datetime.utcnow()
                else:
                    # Create new
                    evaluation = Evaluation(
                        song_id=song_id,
                        audio_quality_score=metrics["audio_quality_score"],
                        duration_seconds=metrics["duration_seconds"],
                        file_size_mb=metrics["file_size_mb"],
                        sample_rate=metrics["sample_rate"],
                        bitrate=metrics["bitrate"],
                        evaluated_at=datetime.utcnow(),
                    )
                    db.add(evaluation)

                # Auto-approve if quality score is high enough
                if metrics["audio_quality_score"] >= settings.MIN_QUALITY_SCORE:
                    evaluation.approved = True
                    logger.info(
                        f"Song auto-approved (score: {metrics['audio_quality_score']})"
                    )

                await db.commit()
                await db.refresh(evaluation)

                # Update song status
                song.status = "evaluated"
                await db.commit()

                logger.info(
                    f"Evaluation complete: {song_id} (score: {metrics['audio_quality_score']})"
                )
                return evaluation

        except Exception as e:
            logger.error(f"Error evaluating song {song_id}: {e}", exc_info=True)
            raise


# Global instance
_evaluator = None


def get_evaluator() -> EvaluatorService:
    """Get the global evaluator instance.

    Returns:
        The singleton EvaluatorService instance
    """
    global _evaluator
    if _evaluator is None:
        _evaluator = EvaluatorService()
    return _evaluator
