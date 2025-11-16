"""Tests for file watcher service."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.file_watcher import SongFileHandler


class TestSongFileHandler:
    """Tests for SongFileHandler."""

    def test_parse_song_file_extracts_title(self):
        """Test that song file parser extracts title correctly."""
        handler = SongFileHandler()

        content = """# My Awesome Song

## Style Prompt
Pop, upbeat, catchy

## Lyrics
[Verse 1]
This is a test song
"""

        metadata = handler.parse_song_file(content)

        assert metadata["title"] == "My Awesome Song"
        assert "Pop" in metadata["style_prompt"]
        assert metadata["genre"] == "Pop"

    def test_parse_song_file_extracts_style_prompt(self):
        """Test that song file parser extracts style prompt."""
        handler = SongFileHandler()

        content = """# Test Song

## Style Prompt
Hip-hop, trap beat, aggressive, 808s, Atlanta trap

## Lyrics
[Verse 1]
Lyrics here
"""

        metadata = handler.parse_song_file(content)

        assert "Hip-hop" in metadata["style_prompt"]
        assert "trap beat" in metadata["style_prompt"]
        assert metadata["genre"] == "Hip-Hop"

    def test_parse_song_file_extracts_lyrics(self):
        """Test that song file parser extracts lyrics section."""
        handler = SongFileHandler()

        content = """# Test Song

## Style Prompt
Jazz, smooth

## Lyrics
[Verse 1]
First line
Second line

[Chorus]
Chorus line
"""

        metadata = handler.parse_song_file(content)

        assert "[Verse 1]" in metadata["lyrics"]
        assert "[Chorus]" in metadata["lyrics"]
        assert "First line" in metadata["lyrics"]

    @pytest.mark.asyncio
    async def test_process_song_file_creates_song(self):
        """Test that processing a song file creates a database record."""
        handler = SongFileHandler()

        # Create a temporary test file
        test_file = Path("/tmp/test_song.md")
        test_file.write_text("""# Test Song

## Style Prompt
Pop, upbeat

## Lyrics
[Verse 1]
Test lyrics
""")

        # Mock the database session
        with patch("app.services.file_watcher.AsyncSessionLocal") as mock_session:
            mock_db = AsyncMock()
            mock_session.return_value.__aenter__.return_value = mock_db

            # Mock the database query
            mock_result = AsyncMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute.return_value = mock_result

            # Mock settings
            with patch("app.services.file_watcher.settings") as mock_settings:
                mock_settings.AUTO_UPLOAD_TO_SUNO = False

                # Process the file
                await handler.process_song_file(test_file)

                # Verify song was added
                assert mock_db.add.called
                assert mock_db.commit.called

        # Cleanup
        test_file.unlink()


class TestFileWatcherService:
    """Tests for FileWatcherService."""

    def test_file_watcher_initialization(self):
        """Test that file watcher can be initialized."""
        with patch("app.services.file_watcher.settings") as mock_settings:
            mock_settings.WATCH_FOLDER = "/tmp/test_watch"

            from app.services.file_watcher import FileWatcherService

            watcher = FileWatcherService()

            assert watcher.observer is not None
            assert watcher.handler is not None
            assert watcher.watch_folder == Path("/tmp/test_watch")
