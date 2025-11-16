"""
Comprehensive validation framework for songs and metadata
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re
import logging

logger = logging.getLogger(__name__)


class SongValidator:
    """Validate song files and metadata"""

    REQUIRED_FIELDS = ['title', 'genre', 'style_prompt', 'lyrics']
    VALID_GENRES = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']

    # Structure tags that should appear in lyrics
    STRUCTURE_TAGS = [
        '[Intro]', '[Verse]', '[Pre-Chorus]', '[Chorus]',
        '[Bridge]', '[Outro]'
    ]

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_song_file(self, filepath: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a song markdown file

        Args:
            filepath: Path to song .md file

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Check file exists
        if not filepath.exists():
            self.errors.append(f"File not found: {filepath}")
            return False, self.errors, self.warnings

        # Read content
        try:
            content = filepath.read_text(encoding='utf-8')
        except Exception as e:
            self.errors.append(f"Cannot read file: {e}")
            return False, self.errors, self.warnings

        # Parse content
        song_data = self._parse_markdown(content)

        # Validate required fields
        self._validate_required_fields(song_data)

        # Validate genre
        self._validate_genre(song_data.get('genre'))

        # Validate style prompt
        self._validate_style_prompt(song_data.get('style_prompt'))

        # Validate lyrics structure
        self._validate_lyrics_structure(song_data.get('lyrics'))

        # Check metadata file exists
        self._check_metadata_file(filepath)

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _parse_markdown(self, content: str) -> Dict:
        """Parse markdown content into dict"""
        data = {}

        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            data['title'] = title_match.group(1).strip()

        # Extract genre
        genre_match = re.search(r'\*\*Genre\*\*:\s*(.+)', content, re.IGNORECASE)
        if genre_match:
            data['genre'] = genre_match.group(1).strip().lower()

        # Extract style prompt (in code block)
        style_match = re.search(r'##\s+Style Prompt.*?```\n(.+?)\n```', content, re.DOTALL)
        if style_match:
            data['style_prompt'] = style_match.group(1).strip()

        # Extract lyrics (after ## Lyrics)
        lyrics_match = re.search(r'##\s+Lyrics\s*\n(.+)', content, re.DOTALL)
        if lyrics_match:
            data['lyrics'] = lyrics_match.group(1).strip()

        return data

    def _validate_required_fields(self, data: Dict):
        """Check all required fields present"""
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                self.errors.append(f"Missing required field: {field}")

    def _validate_genre(self, genre: Optional[str]):
        """Validate genre value"""
        if not genre:
            return  # Already caught by required fields

        if genre not in self.VALID_GENRES:
            self.errors.append(
                f"Invalid genre '{genre}'. Must be one of: {', '.join(self.VALID_GENRES)}"
            )

    def _validate_style_prompt(self, style_prompt: Optional[str]):
        """Validate style prompt follows best practices"""
        if not style_prompt:
            return  # Already caught by required fields

        # Check length (should be 200-1000 chars)
        length = len(style_prompt)
        if length < 50:
            self.errors.append(f"Style prompt too short ({length} chars). Aim for 200-1000.")
        elif length > 1500:
            self.warnings.append(f"Style prompt very long ({length} chars). Aim for 200-1000.")

        # Count descriptors (comma-separated)
        descriptors = [d.strip() for d in style_prompt.split(',')]
        descriptor_count = len(descriptors)

        if descriptor_count < 4:
            self.warnings.append(
                f"Only {descriptor_count} descriptors. Aim for 4-7 (the 4-7 rule)."
            )
        elif descriptor_count > 10:
            self.warnings.append(
                f"{descriptor_count} descriptors may confuse AI. Aim for 4-7."
            )

    def _validate_lyrics_structure(self, lyrics: Optional[str]):
        """Validate lyrics have proper structure tags"""
        if not lyrics:
            return  # Already caught by required fields

        # Check for at least some structure tags
        found_tags = [tag for tag in self.STRUCTURE_TAGS if tag in lyrics]

        if len(found_tags) < 3:
            self.errors.append(
                f"Missing structure tags. Found {len(found_tags)}, need at least 3. "
                f"Use: [Intro], [Verse], [Chorus], etc."
            )

        # Check for [Chorus] specifically (most important)
        if '[Chorus]' not in lyrics:
            self.warnings.append("No [Chorus] tag found. Choruses are essential!")

    def _check_metadata_file(self, song_file: Path):
        """Check if metadata file exists"""
        meta_file = song_file.with_suffix('.meta.json')
        if not meta_file.exists():
            self.warnings.append(f"No metadata file found: {meta_file.name}")


class MetadataValidator:
    """Validate metadata JSON files"""

    REQUIRED_FIELDS = ['id', 'title', 'genre']

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_metadata_file(self, filepath: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a metadata JSON file

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Check file exists
        if not filepath.exists():
            self.errors.append(f"File not found: {filepath}")
            return False, self.errors, self.warnings

        # Parse JSON
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Cannot read file: {e}")
            return False, self.errors, self.warnings

        # Validate required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                self.errors.append(f"Missing required field: {field}")

        # Validate UUID format
        if 'id' in data:
            self._validate_uuid(data['id'])

        # Check song file exists
        song_file = filepath.with_suffix('.md')
        if not song_file.exists():
            self.errors.append(f"Corresponding song file not found: {song_file.name}")

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_uuid(self, uuid_str: str):
        """Validate UUID format"""
        if not uuid_str or len(uuid_str) != 12:
            self.errors.append(
                f"Invalid UUID length. Expected 12 chars, got {len(uuid_str) if uuid_str else 0}"
            )
            return

        try:
            int(uuid_str, 16)  # Verify it's hexadecimal
        except ValueError:
            self.errors.append(f"Invalid UUID format. Must be hexadecimal: {uuid_str}")


def validate_all_songs(base_dir: Path) -> Dict:
    """
    Validate all songs in the repository

    Returns:
        Dict with validation results
    """
    song_validator = SongValidator()
    meta_validator = MetadataValidator()

    results = {
        'total': 0,
        'valid': 0,
        'errors': 0,
        'warnings': 0,
        'details': []
    }

    songs_dir = base_dir / "generated" / "songs"

    if not songs_dir.exists():
        logger.warning(f"Songs directory not found: {songs_dir}")
        return results

    for song_file in songs_dir.rglob("*.md"):
        results['total'] += 1

        is_valid, errors, warnings = song_validator.validate_song_file(song_file)

        if is_valid:
            results['valid'] += 1

        if errors:
            results['errors'] += len(errors)

        if warnings:
            results['warnings'] += len(warnings)

        if errors or warnings:
            results['details'].append({
                'file': str(song_file.relative_to(base_dir)),
                'errors': errors,
                'warnings': warnings
            })

    return results
