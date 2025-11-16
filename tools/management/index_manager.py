"""
Index Management Tool
Manages song indexes and collections
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class IndexManager:
    """Manage song indexes and collections"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.generated_dir = base_dir / "generated" if (base_dir / "generated").exists() else base_dir
        self.songs_dir = self.generated_dir / "songs"

    def scan_songs(self) -> Dict:
        """Scan all songs and create statistics"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'total_songs': 0,
            'by_genre': {},
            'by_collection': {},
            'files': {
                'md_files': [],
                'metadata_files': [],
                'orphaned_metadata': [],
                'missing_metadata': []
            }
        }

        if not self.songs_dir.exists():
            logger.warning(f"Songs directory not found: {self.songs_dir}")
            return stats

        # Track files
        md_files = set(self.songs_dir.rglob("*.md"))
        meta_files = set(self.songs_dir.rglob("*.meta.json"))

        # Check for orphaned metadata
        for meta_file in meta_files:
            song_file = meta_file.with_suffix('.md')
            if song_file not in md_files:
                stats['files']['orphaned_metadata'].append(str(meta_file.relative_to(self.base_dir)))

        # Check for missing metadata
        for song_file in md_files:
            meta_file = song_file.with_suffix('.meta.json')
            if meta_file not in meta_files:
                stats['files']['missing_metadata'].append(str(song_file.relative_to(self.base_dir)))
            stats['total_songs'] += 1

        # Count by genre and collection
        for genre_dir in self.songs_dir.iterdir():
            if genre_dir.is_dir():
                genre = genre_dir.name
                stats['by_genre'][genre] = 0

                for collection_dir in genre_dir.iterdir():
                    if collection_dir.is_dir():
                        collection = collection_dir.name
                        song_count = len(list(collection_dir.glob("*.md")))
                        stats['by_genre'][genre] += song_count

                        if collection not in stats['by_collection']:
                            stats['by_collection'][collection] = 0
                        stats['by_collection'][collection] += song_count

        return stats

    def validate_index(self) -> Dict:
        """Validate song index"""
        issues = {
            'errors': [],
            'warnings': [],
            'stats': self.scan_songs()
        }

        # Check for orphaned files
        if issues['stats']['files']['orphaned_metadata']:
            issues['warnings'].append(
                f"Found {len(issues['stats']['files']['orphaned_metadata'])} orphaned metadata files"
            )

        # Check for missing metadata
        if issues['stats']['files']['missing_metadata']:
            issues['warnings'].append(
                f"Found {len(issues['stats']['files']['missing_metadata'])} songs without metadata"
            )

        return issues

    def generate_collection_views(self) -> bool:
        """Generate collection view files"""
        try:
            stats = self.scan_songs()

            # Create TRIUMPH-COLLECTION.md
            triumph_file = self.generated_dir / "TRIUMPH-COLLECTION.md"
            self._write_collection_file(triumph_file, "Triumph Collection", "triumph")

            # Create STANDALONE-SONGS.md
            standalone_file = self.generated_dir / "STANDALONE-SONGS.md"
            self._write_collection_file(standalone_file, "Standalone Songs", "standalone")

            logger.info("Generated collection view files")
            return True

        except Exception as e:
            logger.error(f"Error generating collection views: {e}")
            return False

    def _write_collection_file(self, filepath: Path, title: str, collection: str):
        """Write collection view file"""
        content = f"""# {title}

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

This document lists all songs in the "{collection}" collection.

## Songs by Genre

"""

        if self.songs_dir.exists():
            genres = {}
            for genre_dir in self.songs_dir.iterdir():
                if genre_dir.is_dir():
                    genre = genre_dir.name
                    collection_dir = genre_dir / collection
                    if collection_dir.exists():
                        songs = list(collection_dir.glob("*.md"))
                        if songs:
                            genres[genre] = songs

            for genre, songs in sorted(genres.items()):
                content += f"\n### {genre.title()} ({len(songs)} songs)\n\n"
                for song in sorted(songs):
                    song_id = song.stem.split('-')[0]
                    song_title = '-'.join(song.stem.split('-')[1:]).replace('-', ' ').title()
                    content += f"- `{song_id}` - {song_title}\n"

        filepath.write_text(content)
        logger.info(f"Generated collection view: {filepath}")

    def update_all_songs_index(self) -> bool:
        """Update ALL-SONGS-INDEX.md"""
        try:
            index_file = self.generated_dir / "ALL-SONGS-INDEX.md"

            content = """# All Songs Index

**Last Updated**: {timestamp}

## Overview

Complete catalog of all {total} songs organized by genre and collection.

""".format(
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                total=self._count_total_songs()
            )

            if self.songs_dir.exists():
                for genre_dir in sorted(self.songs_dir.iterdir()):
                    if genre_dir.is_dir():
                        genre = genre_dir.name
                        content += f"\n## {genre.title()}\n\n"

                        for collection_dir in sorted(genre_dir.iterdir()):
                            if collection_dir.is_dir():
                                collection = collection_dir.name
                                songs = list(collection_dir.glob("*.md"))

                                if songs:
                                    marker = "⭐" if collection == "triumph" else ""
                                    content += f"### {collection.title()} ({len(songs)} songs) {marker}\n\n"

                                    for song in sorted(songs):
                                        song_id = song.stem.split('-')[0]
                                        song_title = '-'.join(song.stem.split('-')[1:]).replace('-', ' ').title()
                                        content += f"- `{song_id}` - {song_title} {marker}\n"
                                    content += "\n"

            index_file.write_text(content)
            logger.info(f"Updated ALL-SONGS-INDEX.md")
            return True

        except Exception as e:
            logger.error(f"Error updating index: {e}")
            return False

    def _count_total_songs(self) -> int:
        """Count total songs"""
        if not self.songs_dir.exists():
            return 0
        return len(list(self.songs_dir.rglob("*.md")))
