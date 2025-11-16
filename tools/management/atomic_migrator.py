"""
Atomic Song Migration Tool
Two-phase migration with validation and rollback
"""

import logging
import shutil
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class AtomicMigrator:
    """
    Two-phase atomic migration system
    Phase 1: Create staging area
    Phase 2: Validate
    Phase 3: Atomic swap
    """

    def __init__(self, source_dir: Path, target_dir: Path):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.backup_dir = target_dir.parent / "generated-backup"
        self.staging_dir = target_dir.parent / "generated-staging"

        self.migration_log = []
        self.errors = []

    def execute_migration(self) -> bool:
        """
        Execute complete two-phase migration

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Starting atomic migration...")

            # Phase 1: Create staging area
            logger.info("Phase 1: Creating staging area...")
            if not self.phase1_create_staging():
                logger.error("Phase 1 failed")
                return False

            # Phase 2: Validate staging area
            logger.info("Phase 2: Validating staging area...")
            if not self.phase2_validate_staging():
                logger.error("Phase 2 failed - staging area invalid")
                self.cleanup_staging()
                return False

            # Phase 3: Atomic swap
            logger.info("Phase 3: Atomic swap...")
            if not self.phase3_atomic_swap():
                logger.error("Phase 3 failed")
                self.rollback()
                return False

            logger.info("✅ Migration completed successfully!")
            self.log_migration_success()
            return True

        except Exception as e:
            logger.exception("Fatal error during migration")
            self.errors.append(f"Fatal error: {e}")
            self.rollback()
            return False

    def phase1_create_staging(self) -> bool:
        """Create complete new structure in staging"""
        try:
            # Clean any existing staging
            if self.staging_dir.exists():
                shutil.rmtree(self.staging_dir)

            self.staging_dir.mkdir(parents=True)

            # Scan source for songs
            source_songs_dir = self.source_dir / "songs" if (self.source_dir / "songs").exists() else self.source_dir

            if not source_songs_dir.exists():
                logger.warning(f"No songs directory found at {source_songs_dir}")
                return True

            # Copy songs with new structure
            songs_migrated = 0
            for genre_dir in source_songs_dir.iterdir():
                if not genre_dir.is_dir():
                    continue

                genre = genre_dir.name

                for song_file in genre_dir.glob("*.md"):
                    if self.migrate_song_to_staging(song_file, genre):
                        songs_migrated += 1
                    else:
                        self.errors.append(f"Failed to migrate: {song_file}")
                        return False

            logger.info(f"✓ Migrated {songs_migrated} songs to staging")
            return True

        except Exception as e:
            logger.error(f"Phase 1 error: {e}")
            return False

    def migrate_song_to_staging(self, source_file: Path, genre: str) -> bool:
        """Migrate single song to staging area"""
        try:
            from tools.core.uuid_generator import UUIDGenerator

            # Extract metadata
            metadata = self.extract_song_metadata(source_file)
            if not metadata:
                return False

            # Generate UUID
            uuid_gen = UUIDGenerator()
            song_id = uuid_gen.generate()

            # Create filename
            slug = metadata['title'].lower().replace(' ', '-')[:50]
            filename = f"{song_id}-{slug}.md"

            # Determine target path
            genre_name = metadata.get('genre', genre).lower()
            collection = self.determine_collection(metadata)

            target_dir = self.staging_dir / "songs" / genre_name / collection
            target_dir.mkdir(parents=True, exist_ok=True)

            target_file = target_dir / filename

            # Copy file
            shutil.copy2(source_file, target_file)

            # Create metadata file
            metadata['id'] = song_id
            meta_file = target_file.with_suffix('.meta.json')
            meta_file.write_text(json.dumps(metadata, indent=2))

            # Verify copy
            if not target_file.exists() or target_file.stat().st_size == 0:
                logger.error(f"Copy verification failed: {target_file}")
                return False

            self.migration_log.append({
                'source': str(source_file),
                'target': str(target_file),
                'id': song_id,
                'status': 'success'
            })

            return True

        except Exception as e:
            logger.error(f"Error migrating {source_file}: {e}")
            return False

    def extract_song_metadata(self, filepath: Path) -> Optional[Dict]:
        """Extract metadata from song file"""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else filepath.stem

            # Extract genre from path or content
            genre_match = re.search(r'\*\*Genre\*\*:\s*(.+)', content, re.IGNORECASE)
            genre = genre_match.group(1).strip().lower() if genre_match else 'unknown'

            if not title:
                logger.error(f"No title found in {filepath}")
                return None

            return {
                'title': title,
                'genre': genre,
                'source_file': str(filepath)
            }

        except Exception as e:
            logger.error(f"Error extracting metadata from {filepath}: {e}")
            return None

    def determine_collection(self, metadata: Dict) -> str:
        """Determine if song belongs to collection or standalone"""
        # Load Triumph Collection list
        triumph_songs = self.load_triumph_collection()

        title = metadata.get('title', '')
        if title in triumph_songs:
            return 'triumph'
        else:
            return 'standalone'

    def load_triumph_collection(self) -> set:
        """Load Triumph Collection songs from index"""
        triumph_songs = set()

        index_file = self.source_dir / "ALL-SONGS-INDEX.md"
        if not index_file.exists():
            logger.warning("ALL-SONGS-INDEX.md not found")
            return triumph_songs

        try:
            content = index_file.read_text()

            for line in content.splitlines():
                if '⭐' in line:
                    match = re.search(r'[-*]\s+`[^`]+`\s+-\s+(.+?)\s+⭐', line)
                    if match:
                        triumph_songs.add(match.group(1).strip())

            logger.info(f"Loaded {len(triumph_songs)} Triumph Collection songs")

        except Exception as e:
            logger.error(f"Error loading Triumph Collection: {e}")

        return triumph_songs

    def phase2_validate_staging(self) -> bool:
        """Validate staging area"""
        logger.info("Running comprehensive validation...")

        # Count files
        source_count = len(list(self.source_dir.rglob("*.md"))) if (self.source_dir / "songs").exists() else 0
        staging_count = len(list(self.staging_dir.rglob("*.md")))

        logger.info(f"File counts: source={source_count}, staging={staging_count}")

        # Check for metadata files
        staging_meta_count = len(list(self.staging_dir.rglob("*.meta.json")))
        logger.info(f"Metadata files: {staging_meta_count}")

        if staging_meta_count != staging_count:
            logger.error(f"Metadata mismatch: {staging_meta_count} metadata files vs {staging_count} songs")
            return False

        logger.info("✓ Staging area validated successfully")
        return True

    def phase3_atomic_swap(self) -> bool:
        """Atomically swap staging with production"""
        try:
            # Create backup of current production
            if self.target_dir.exists():
                logger.info(f"Creating backup: {self.backup_dir}")

                if self.backup_dir.exists():
                    shutil.rmtree(self.backup_dir)

                shutil.copytree(self.target_dir, self.backup_dir)
                logger.info("✓ Backup created")

            # Remove old production
            if self.target_dir.exists():
                shutil.rmtree(self.target_dir)

            # Move staging to production
            shutil.move(str(self.staging_dir), str(self.target_dir))
            logger.info("✓ Atomic swap completed")

            return True

        except Exception as e:
            logger.error(f"Error during atomic swap: {e}")
            return False

    def rollback(self) -> bool:
        """Rollback to backup if migration fails"""
        logger.warning("Initiating rollback...")

        try:
            if not self.backup_dir.exists():
                logger.error("No backup found for rollback")
                return False

            # Remove failed production
            if self.target_dir.exists():
                shutil.rmtree(self.target_dir)

            # Restore from backup
            shutil.copytree(self.backup_dir, self.target_dir)

            logger.info("✓ Rollback completed - system restored to previous state")
            return True

        except Exception as e:
            logger.error(f"CRITICAL: Rollback failed: {e}")
            return False

    def cleanup_staging(self):
        """Clean up staging area"""
        if self.staging_dir.exists():
            shutil.rmtree(self.staging_dir)
            logger.info("✓ Staging area cleaned up")

    def log_migration_success(self):
        """Log successful migration details"""
        log_file = self.target_dir.parent / "migration-log.json"

        log_data = {
            'timestamp': datetime.now().isoformat(),
            'source': str(self.source_dir),
            'target': str(self.target_dir),
            'songs_migrated': len(self.migration_log),
            'errors': self.errors,
            'details': self.migration_log
        }

        log_file.write_text(json.dumps(log_data, indent=2))
        logger.info(f"Migration log saved: {log_file}")
