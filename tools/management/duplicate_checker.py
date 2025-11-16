"""
Duplicate Song Checker
Detects duplicate or similar song titles
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import json
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DuplicateChecker:
    """Check for duplicate songs using fuzzy matching"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.songs = {}
        self.load_songs()

    def load_songs(self):
        """Load all songs from metadata files"""
        self.songs = {}
        songs_dir = self.base_dir / "songs" if (self.base_dir / "songs").exists() else self.base_dir

        for meta_file in songs_dir.rglob("*.meta.json"):
            try:
                with open(meta_file, 'r') as f:
                    data = json.load(f)
                    title = data.get('title', '')
                    if title:
                        self.songs[title.lower()] = {
                            'title': title,
                            'file': str(meta_file.relative_to(self.base_dir)),
                            'id': data.get('id', 'unknown'),
                            'genre': data.get('genre', 'unknown')
                        }
            except Exception as e:
                logger.error(f"Error loading {meta_file}: {e}")

        logger.info(f"Loaded {len(self.songs)} songs for duplicate checking")

    def check_title(self, title: str, threshold: float = 0.8) -> List[Dict]:
        """
        Check for songs similar to given title

        Args:
            title: Song title to check
            threshold: Similarity threshold (0-1)

        Returns:
            List of similar songs with similarity scores
        """
        results = []
        title_lower = title.lower()

        for existing_title, song_data in self.songs.items():
            # Exact match
            if existing_title == title_lower:
                results.append({
                    'file': song_data['file'],
                    'title': song_data['title'],
                    'genre': song_data['genre'],
                    'similarity': 1.0,
                    'type': 'exact'
                })
                continue

            # Fuzzy match
            similarity = SequenceMatcher(None, title_lower, existing_title).ratio()
            if similarity >= threshold:
                results.append({
                    'file': song_data['file'],
                    'title': song_data['title'],
                    'genre': song_data['genre'],
                    'similarity': similarity,
                    'type': 'fuzzy'
                })

        # Sort by similarity
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results

    def scan_all(self, threshold: float = 0.85) -> List[Dict]:
        """
        Scan all songs for duplicates

        Returns:
            List of duplicate groups
        """
        duplicates = []
        checked = set()

        for title1 in self.songs.keys():
            if title1 in checked:
                continue

            group = [self.songs[title1]['file']]
            checked.add(title1)

            for title2 in self.songs.keys():
                if title2 in checked:
                    continue

                similarity = SequenceMatcher(None, title1, title2).ratio()
                if similarity >= threshold:
                    group.append(self.songs[title2]['file'])
                    checked.add(title2)

            if len(group) > 1:
                duplicates.append({
                    'title': self.songs[title1]['title'],
                    'files': group,
                    'count': len(group)
                })

        return duplicates

    def get_statistics(self) -> Dict:
        """Get statistics about songs"""
        stats = {
            'total': len(self.songs),
            'by_genre': {},
        }

        for song_data in self.songs.values():
            # Get genre from song data
            genre = song_data.get('genre', 'unknown')
            if genre not in stats['by_genre']:
                stats['by_genre'][genre] = 0
            stats['by_genre'][genre] += 1

        return stats
