"""
Metadata Extraction Tool
Extracts and searches metadata from all songs
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extract and manage song metadata"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.metadata = []
        self.extract_all()

    def extract_all(self):
        """Extract metadata from all song files"""
        self.metadata = []
        songs_dir = self.base_dir / "songs" if (self.base_dir / "songs").exists() else self.base_dir

        for meta_file in songs_dir.rglob("*.meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    data = json.load(f)
                    # Add file path for reference
                    data['file'] = str(meta_file.relative_to(self.base_dir))
                    data['song_file'] = str(meta_file.with_suffix('.md').relative_to(self.base_dir))
                    self.metadata.append(data)
            except Exception as e:
                logger.error(f"Error extracting metadata from {meta_file}: {e}")

        logger.info(f"Extracted metadata from {len(self.metadata)} songs")

    def search(self, query: str) -> List[Dict]:
        """
        Search songs by title, theme, or persona

        Args:
            query: Search term (case-insensitive)

        Returns:
            List of matching songs
        """
        query_lower = query.lower()
        results = []

        for song in self.metadata:
            # Search in title
            if query_lower in song.get('title', '').lower():
                results.append(song)
                continue

            # Search in theme
            if query_lower in song.get('theme', '').lower():
                results.append(song)
                continue

            # Search in mood
            if query_lower in song.get('mood', '').lower():
                results.append(song)
                continue

            # Search in personas
            personas = song.get('personas', [])
            for persona in personas:
                if query_lower in persona.lower():
                    results.append(song)
                    break

        return results

    def get_by_genre(self, genre: str) -> List[Dict]:
        """Get all songs for a specific genre"""
        return [s for s in self.metadata if s.get('genre', '').lower() == genre.lower()]

    def get_statistics(self) -> Dict:
        """Get metadata statistics"""
        stats = {
            'total_songs': len(self.metadata),
            'by_genre': {},
            'by_theme': {},
            'personas_used': set(),
        }

        for song in self.metadata:
            # Count by genre
            genre = song.get('genre', 'unknown')
            stats['by_genre'][genre] = stats['by_genre'].get(genre, 0) + 1

            # Count by theme
            theme = song.get('theme', 'unknown')
            stats['by_theme'][theme] = stats['by_theme'].get(theme, 0) + 1

            # Collect personas
            for persona in song.get('personas', []):
                stats['personas_used'].add(persona)

        # Convert set to list for JSON serialization
        stats['personas_used'] = list(stats['personas_used'])

        return stats

    def export_metadata(self, output_file: Path) -> bool:
        """Export all metadata to JSON file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info(f"Exported metadata to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting metadata: {e}")
            return False

    def validate_metadata(self) -> Dict:
        """Validate all metadata"""
        issues = {
            'missing_fields': [],
            'invalid_genres': [],
            'warnings': []
        }

        valid_genres = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']

        for song in self.metadata:
            # Check required fields
            required = ['id', 'title', 'genre']
            for field in required:
                if field not in song or not song[field]:
                    issues['missing_fields'].append(f"{song.get('title', 'Unknown')}: missing {field}")

            # Check valid genre
            if song.get('genre') not in valid_genres:
                issues['invalid_genres'].append(f"{song.get('title', 'Unknown')}: {song.get('genre')}")

            # Warnings
            if not song.get('personas'):
                issues['warnings'].append(f"{song.get('title', 'Unknown')}: no personas defined")

        return issues
