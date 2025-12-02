"""Variation service for managing Suno variations."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.models.song import Song
from app.models.suno_job import SunoJob
from app.models.suno_variation import SunoVariation

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)
settings = get_settings()


class VariationService:
    """Service for managing Suno variations."""

    def __init__(self, download_folder: Path | None = None):
        """Initialize the variation service.

        Args:
            download_folder: Path to the download folder (defaults to settings.DOWNLOAD_FOLDER)
        """
        self.download_folder = download_folder or Path(settings.DOWNLOAD_FOLDER)

    async def get_pending_review_songs(
        self, db: AsyncSession, limit: int = 50
    ) -> list[Song]:
        """Get songs that have downloaded variations awaiting selection.

        A song is pending review if it has:
        - Status is 'downloaded' or 'reviewing'
        - Has SunoVariation records where none are selected

        Args:
            db: Database session
            limit: Maximum number of songs to return

        Returns:
            List of songs pending review
        """
        try:
            # Query for songs with downloaded/reviewing status
            stmt = (
                select(Song)
                .where(
                    and_(
                        Song.status.in_(["downloaded", "reviewing"]),
                        Song.selected_variation_id.is_(None),
                    )
                )
                .order_by(Song.created_at.desc())
                .limit(limit)
            )

            result = await db.execute(stmt)
            songs = result.scalars().all()

            logger.info(f"Found {len(songs)} songs pending review")
            return list(songs)

        except Exception as e:
            logger.error(f"Error getting pending review songs: {e}", exc_info=True)
            raise

    async def get_variations(
        self, db: AsyncSession, song_id: str
    ) -> list[SunoVariation]:
        """Get all variations for a song.

        Returns variations from the latest SunoJob, ordered by variation_index.

        Args:
            db: Database session
            song_id: Song identifier

        Returns:
            List of variations for the song

        Raises:
            ValueError: If song or SunoJob not found
        """
        try:
            # Get the latest SunoJob for this song
            stmt = (
                select(SunoJob)
                .where(SunoJob.song_id == song_id)
                .order_by(SunoJob.created_at.desc())
                .limit(1)
                .options(selectinload(SunoJob.variations))
            )

            result = await db.execute(stmt)
            suno_job = result.scalar_one_or_none()

            if not suno_job:
                raise ValueError(f"No SunoJob found for song: {song_id}")

            # Get variations and sort by index
            variations = sorted(
                suno_job.variations, key=lambda v: v.variation_index
            )

            logger.info(
                f"Found {len(variations)} variations for song {song_id} (job {suno_job.id})"
            )
            return variations

        except Exception as e:
            logger.error(
                f"Error getting variations for song {song_id}: {e}", exc_info=True
            )
            raise

    async def select_variation(
        self,
        db: AsyncSession,
        song_id: str,
        variation_id: int,
        delete_other: bool = False,
    ) -> Song:
        """Select a variation as the winner.

        1. Mark the selected variation as is_selected=True
        2. Mark sibling variations as is_selected=False
        3. Update Song.selected_variation_id
        4. Update Song.audio_path to the selected variation's path
        5. Update Song.status to 'evaluated' (ready for next step)
        6. If delete_other=True, soft delete other variations (is_deleted=True)
           and delete their files from disk

        Args:
            db: Database session
            song_id: Song identifier
            variation_id: ID of the variation to select
            delete_other: Whether to delete other variations

        Returns:
            The updated Song

        Raises:
            ValueError: If song, variation, or SunoJob not found
        """
        try:
            # Get the song
            stmt = select(Song).where(Song.id == song_id)
            result = await db.execute(stmt)
            song = result.scalar_one_or_none()

            if not song:
                raise ValueError(f"Song not found: {song_id}")

            # Get the selected variation
            stmt = select(SunoVariation).where(SunoVariation.id == variation_id)
            result = await db.execute(stmt)
            selected_variation = result.scalar_one_or_none()

            if not selected_variation:
                raise ValueError(f"Variation not found: {variation_id}")

            # Verify the variation belongs to this song
            stmt = select(SunoJob).where(SunoJob.id == selected_variation.suno_job_id)
            result = await db.execute(stmt)
            suno_job = result.scalar_one_or_none()

            if not suno_job or suno_job.song_id != song_id:
                raise ValueError(
                    f"Variation {variation_id} does not belong to song {song_id}"
                )

            # Get all sibling variations
            stmt = (
                select(SunoVariation)
                .where(SunoVariation.suno_job_id == suno_job.id)
            )
            result = await db.execute(stmt)
            all_variations = result.scalars().all()

            # Update selection status
            for variation in all_variations:
                if variation.id == variation_id:
                    variation.is_selected = True
                    variation.selected_at = datetime.now(timezone.utc)
                    logger.info(f"Selected variation {variation_id} for song {song_id}")
                else:
                    variation.is_selected = False
                    variation.selected_at = None

                    # Delete other variations if requested
                    if delete_other:
                        variation.is_deleted = True
                        # Delete the file from disk
                        await self._delete_variation_file_from_disk(
                            song_id, variation.variation_index
                        )
                        logger.info(
                            f"Deleted variation {variation.id} (index {variation.variation_index}) for song {song_id}"
                        )

            # Update song
            song.selected_variation_id = variation_id
            song.audio_path = selected_variation.audio_path
            song.status = "evaluated"
            song.updated_at = datetime.now(timezone.utc)

            await db.commit()
            await db.refresh(song)

            logger.info(
                f"Variation selection complete for song {song_id}: variation {variation_id}, delete_other={delete_other}"
            )
            return song

        except Exception as e:
            await db.rollback()
            logger.error(
                f"Error selecting variation {variation_id} for song {song_id}: {e}",
                exc_info=True,
            )
            raise

    async def delete_variation(
        self,
        db: AsyncSession,
        variation_id: int,
        hard_delete: bool = False,
    ) -> bool:
        """Delete a variation.

        If hard_delete=False: Set is_deleted=True (soft delete)
        If hard_delete=True: Delete the database record and file

        Args:
            db: Database session
            variation_id: ID of the variation to delete
            hard_delete: Whether to permanently delete the record

        Returns:
            True if successful

        Raises:
            ValueError: If variation not found
        """
        try:
            # Get the variation
            stmt = (
                select(SunoVariation)
                .where(SunoVariation.id == variation_id)
                .options(selectinload(SunoVariation.suno_job))
            )
            result = await db.execute(stmt)
            variation = result.scalar_one_or_none()

            if not variation:
                raise ValueError(f"Variation not found: {variation_id}")

            song_id = variation.suno_job.song_id

            if hard_delete:
                # Delete file from disk
                await self._delete_variation_file_from_disk(
                    song_id, variation.variation_index
                )

                # Delete database record
                await db.delete(variation)
                await db.commit()

                logger.info(f"Hard deleted variation {variation_id}")
            else:
                # Soft delete
                variation.is_deleted = True
                await db.commit()

                logger.info(f"Soft deleted variation {variation_id}")

            return True

        except Exception as e:
            await db.rollback()
            logger.error(
                f"Error deleting variation {variation_id}: {e}", exc_info=True
            )
            raise

    async def get_variation_by_id(
        self, db: AsyncSession, variation_id: int
    ) -> SunoVariation | None:
        """Get a single variation by ID.

        Args:
            db: Database session
            variation_id: ID of the variation

        Returns:
            The variation, or None if not found
        """
        try:
            stmt = (
                select(SunoVariation)
                .where(SunoVariation.id == variation_id)
                .options(selectinload(SunoVariation.suno_job))
            )
            result = await db.execute(stmt)
            variation = result.scalar_one_or_none()

            if variation:
                logger.debug(f"Found variation {variation_id}")
            else:
                logger.debug(f"Variation {variation_id} not found")

            return variation

        except Exception as e:
            logger.error(
                f"Error getting variation {variation_id}: {e}", exc_info=True
            )
            raise

    async def _delete_variation_file_from_disk(
        self, song_id: str, variation_index: int
    ) -> bool:
        """Delete a variation file from disk.

        Args:
            song_id: Song identifier
            variation_index: Variation index (1-based)

        Returns:
            True if deleted, False if file didn't exist
        """
        try:
            song_folder = self.download_folder / song_id
            filename = f"{song_id}_v{variation_index}.mp3"
            file_path = song_folder / filename

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted variation file: {file_path}")
                return True
            else:
                logger.warning(f"Variation file does not exist: {file_path}")
                return False

        except Exception as e:
            logger.error(
                f"Error deleting variation file {song_id}_v{variation_index}: {e}",
                exc_info=True,
            )
            return False


# Global instance
_variation_service: VariationService | None = None


def get_variation_service() -> VariationService:
    """Get the global variation service instance.

    Returns:
        The singleton VariationService instance
    """
    global _variation_service
    if _variation_service is None:
        _variation_service = VariationService()
    return _variation_service
