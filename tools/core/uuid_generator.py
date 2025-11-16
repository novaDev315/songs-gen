"""
Secure UUID generation with collision detection
Generates 12-character hex UUIDs with collision avoidance
"""

import uuid
import logging
import json
from typing import Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class UUIDGenerator:
    """Generate collision-safe UUIDs for songs"""

    # 12 hex characters = 16^12 = 281,474,976,710,656 combinations
    # Even with 10,000 songs: collision probability < 0.000018%
    UUID_LENGTH = 12
    MAX_ATTEMPTS = 100

    def __init__(self, existing_ids: Optional[Set[str]] = None):
        """
        Initialize UUID generator

        Args:
            existing_ids: Set of already-used IDs to avoid collisions
        """
        self.existing_ids = existing_ids or set()

    def generate(self) -> str:
        """
        Generate unique UUID with collision detection

        Returns:
            12-character hex UUID

        Raises:
            RuntimeError: If unable to generate unique ID after MAX_ATTEMPTS
        """
        for attempt in range(self.MAX_ATTEMPTS):
            new_id = str(uuid.uuid4()).replace('-', '')[:self.UUID_LENGTH]

            if new_id not in self.existing_ids:
                self.existing_ids.add(new_id)
                logger.debug(f"Generated UUID: {new_id}")
                return new_id

            logger.warning(f"UUID collision detected on attempt {attempt + 1}: {new_id}")

        raise RuntimeError(
            f"Failed to generate unique UUID after {self.MAX_ATTEMPTS} attempts. "
            f"This is extremely unlikely. Check system entropy."
        )

    def load_existing_ids(self, base_dir: Path) -> Set[str]:
        """
        Load all existing UUIDs from metadata files

        Args:
            base_dir: Root directory to scan for .meta.json files

        Returns:
            Set of existing UUIDs
        """
        existing = set()

        for meta_file in base_dir.rglob("*.meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    data = json.load(f)
                    if 'id' in data:
                        existing.add(data['id'])
            except Exception as e:
                logger.error(f"Error reading {meta_file}: {e}")

        logger.info(f"Loaded {len(existing)} existing UUIDs")
        self.existing_ids = existing
        return existing

    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Validate UUID format

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if valid format (correct length and hex)
        """
        if not uuid_str or len(uuid_str) != self.UUID_LENGTH:
            return False

        try:
            int(uuid_str, 16)  # Verify it's hex
            return True
        except ValueError:
            return False

    def is_unique(self, uuid_str: str) -> bool:
        """
        Check if UUID is unique (not already in use)

        Args:
            uuid_str: UUID string to check

        Returns:
            True if UUID is not in use
        """
        return uuid_str not in self.existing_ids
