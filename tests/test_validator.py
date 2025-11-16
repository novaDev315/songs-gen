"""
Test Suite for Validation Framework
"""

import pytest
from pathlib import Path
import tempfile
from tools.validation.validator import SongValidator, MetadataValidator


class TestSongValidator:
    """Test song validation"""

    def test_validator_init(self):
        """Validator should initialize correctly"""
        validator = SongValidator()
        assert validator.REQUIRED_FIELDS == ['title', 'genre', 'style_prompt', 'lyrics']
        assert 'pop' in validator.VALID_GENRES

    def test_genre_validation(self):
        """Should validate genres correctly"""
        validator = SongValidator()
        validator._validate_genre('pop')
        assert len(validator.errors) == 0

    def test_invalid_genre(self):
        """Should reject invalid genres"""
        validator = SongValidator()
        validator._validate_genre('invalid_genre')
        assert len(validator.errors) > 0

    def test_style_prompt_too_short(self):
        """Should warn about short style prompts"""
        validator = SongValidator()
        validator._validate_style_prompt("short")
        assert len(validator.errors) > 0

    def test_descriptor_count_warning(self):
        """Should warn about descriptor count"""
        validator = SongValidator()
        validator._validate_style_prompt("pop, happy")  # Only 2
        assert len(validator.warnings) > 0

    def test_lyrics_structure_check(self):
        """Should check for structure tags"""
        validator = SongValidator()
        lyrics = "[Verse]\nSome lyrics\n[Chorus]\nMore lyrics"
        validator._validate_lyrics_structure(lyrics)
        assert len(validator.errors) == 0

    def test_missing_chorus(self):
        """Should warn about missing chorus"""
        validator = SongValidator()
        lyrics = "[Verse]\nSome lyrics\n[Bridge]\nMore lyrics"
        validator._validate_lyrics_structure(lyrics)
        assert len(validator.warnings) > 0


class TestMetadataValidator:
    """Test metadata validation"""

    def test_metadata_validator_init(self):
        """Metadata validator should initialize"""
        validator = MetadataValidator()
        assert validator.REQUIRED_FIELDS == ['id', 'title', 'genre']

    def test_uuid_validation(self):
        """Should validate UUID format"""
        validator = MetadataValidator()
        validator._validate_uuid('a1b2c3d4e5f6')
        assert len(validator.errors) == 0

    def test_invalid_uuid_length(self):
        """Should reject invalid UUID length"""
        validator = MetadataValidator()
        validator._validate_uuid('short')
        assert len(validator.errors) > 0

    def test_invalid_uuid_hex(self):
        """Should reject non-hexadecimal UUIDs"""
        validator = MetadataValidator()
        validator._validate_uuid('gggggggggggg')
        assert len(validator.errors) > 0


class TestValidationIntegration:
    """Integration tests for validation"""

    def test_full_song_validation(self):
        """Should validate complete song"""
        validator = SongValidator()

        # Create minimal valid data
        test_data = {
            'title': 'Test Song',
            'genre': 'pop',
            'style_prompt': 'Pop, upbeat, female vocals, synth pads, 125 BPM',
            'lyrics': '[Verse]\nSome lyrics\n[Chorus]\nChorus lyrics'
        }

        validator._validate_required_fields(test_data)
        validator._validate_genre(test_data['genre'])
        validator._validate_style_prompt(test_data['style_prompt'])
        validator._validate_lyrics_structure(test_data['lyrics'])

        assert len(validator.errors) == 0
