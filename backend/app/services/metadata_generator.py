"""Metadata auto-generator for YouTube uploads."""

import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class MetadataGenerator:
    """Generate YouTube metadata from song data."""

    # Genre-specific tags
    GENRE_TAGS = {
        "pop": ["pop music", "pop song", "catchy", "mainstream", "radio hit", "pop vibes"],
        "rock": ["rock music", "rock song", "guitar", "band", "electric guitar", "rock vibes"],
        "hip-hop": ["hip hop", "rap", "beats", "flow", "bars", "hip hop music"],
        "edm": ["edm", "electronic", "dance music", "electronic music", "edm song", "club music"],
        "jazz": ["jazz", "jazz music", "smooth jazz", "jazz song", "jazzy", "instrumental"],
        "country": ["country music", "country song", "acoustic", "country vibes", "americana"],
        "r&b": ["r&b", "rnb", "rhythm and blues", "soul", "r&b music", "smooth"],
        "indie": ["indie music", "indie song", "alternative", "indie vibes", "independent"],
        "metal": ["metal", "heavy metal", "metal music", "hard rock", "headbanger"],
        "classical": ["classical music", "orchestral", "instrumental", "symphony"],
    }

    # Common AI music tags
    AI_TAGS = ["ai music", "ai generated", "ai song", "suno ai", "ai composition", "generated music"]

    # Description templates
    DESCRIPTION_TEMPLATES = {
        "default": """{title}

🎵 Genre: {genre}
🎨 Style: {style_preview}

---
📝 LYRICS:
{lyrics_preview}

---
🤖 This song was created with AI music generation technology.

#AIMusic #{genre_tag} #NewMusic #MusicVideo
""",

        "minimal": """{title}

Genre: {genre}

{lyrics_preview}

---
AI Generated Music
""",

        "detailed": """🎶 {title} 🎶

═══════════════════════════════════════
🎵 ABOUT THIS TRACK
═══════════════════════════════════════

Genre: {genre}
Style: {style_preview}
Mood: {mood}

═══════════════════════════════════════
📝 FULL LYRICS
═══════════════════════════════════════

{lyrics_full}

═══════════════════════════════════════
🤖 CREATED WITH AI
═══════════════════════════════════════

This track was generated using Suno AI music generation technology.
Cover art and video created with AI assistance.

🔔 Subscribe for more AI-generated music!
👍 Like if you enjoyed the song!
💬 Comment your favorite part!

═══════════════════════════════════════

#AIMusic #{genre_tag} #{title_tag} #NewMusic #AIGenerated
#MusicVideo #SunoAI #AIComposer #GeneratedMusic
""",
    }

    def __init__(self):
        """Initialize the metadata generator."""
        pass

    def _clean_for_tag(self, text: str) -> str:
        """Clean text for use as a hashtag.

        Args:
            text: Text to clean

        Returns:
            Cleaned text suitable for hashtag
        """
        # Remove special characters, keep alphanumeric
        cleaned = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        # Remove extra spaces and capitalize words
        words = cleaned.split()
        return "".join(word.capitalize() for word in words[:3])  # Max 3 words

    def _extract_mood(self, style_prompt: str, lyrics: str) -> str:
        """Extract mood from style prompt and lyrics.

        Args:
            style_prompt: Style description
            lyrics: Song lyrics

        Returns:
            Detected mood (e.g., "Happy", "Sad", "Energetic")
        """
        mood_keywords = {
            "happy": ["happy", "joy", "upbeat", "cheerful", "bright", "fun"],
            "sad": ["sad", "melancholy", "heartbreak", "lonely", "tears"],
            "energetic": ["energetic", "powerful", "intense", "hype", "fire"],
            "chill": ["chill", "relaxed", "smooth", "calm", "laid-back"],
            "romantic": ["love", "romantic", "passion", "heart", "desire"],
            "dark": ["dark", "angry", "aggressive", "intense", "heavy"],
            "nostalgic": ["nostalgic", "memories", "past", "remember"],
            "motivational": ["motivate", "inspire", "rise", "strength", "overcome"],
        }

        combined_text = f"{style_prompt} {lyrics}".lower()

        for mood, keywords in mood_keywords.items():
            if any(kw in combined_text for kw in keywords):
                return mood.capitalize()

        return "Expressive"

    def _extract_style_keywords(self, style_prompt: str) -> List[str]:
        """Extract meaningful keywords from style prompt.

        Args:
            style_prompt: Style description

        Returns:
            List of extracted keywords
        """
        if not style_prompt:
            return []

        # Common style keywords to look for
        keywords = [
            "acoustic", "electric", "synth", "piano", "guitar", "bass",
            "drums", "beats", "vocal", "harmony", "melody", "rhythm",
            "fast", "slow", "upbeat", "mellow", "groovy", "funky",
            "ethereal", "dreamy", "punchy", "crisp", "warm", "bright",
        ]

        style_lower = style_prompt.lower()
        found = [kw for kw in keywords if kw in style_lower]
        return found[:5]

    def generate_tags(
        self,
        title: str,
        genre: str,
        style_prompt: str = "",
        max_tags: int = 15
    ) -> List[str]:
        """Generate YouTube tags from song metadata.

        Args:
            title: Song title
            genre: Song genre
            style_prompt: Style description (optional)
            max_tags: Maximum number of tags to return

        Returns:
            List of YouTube tags
        """
        tags = []

        # Add AI music tags
        tags.extend(self.AI_TAGS[:3])

        # Add genre-specific tags
        genre_lower = genre.lower()
        if genre_lower in self.GENRE_TAGS:
            tags.extend(self.GENRE_TAGS[genre_lower][:4])
        else:
            tags.append(genre.lower())

        # Add title-based tag
        title_tag = self._clean_for_tag(title)
        if title_tag and len(title_tag) > 2:
            tags.append(title_tag.lower())

        # Extract keywords from style prompt
        style_keywords = self._extract_style_keywords(style_prompt)
        tags.extend(style_keywords[:3])

        # Add general music tags
        tags.extend(["new music", "music video", "lyrics video"])

        # Remove duplicates and limit
        seen = set()
        unique_tags = []
        for tag in tags:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in seen and len(tag_lower) > 1:
                seen.add(tag_lower)
                unique_tags.append(tag)

        return unique_tags[:max_tags]

    def generate_description(
        self,
        title: str,
        genre: str,
        style_prompt: str,
        lyrics: str,
        template: str = "default"
    ) -> str:
        """Generate YouTube description from template.

        Args:
            title: Song title
            genre: Song genre
            style_prompt: Style description
            lyrics: Song lyrics
            template: Template name ("default", "minimal", or "detailed")

        Returns:
            Formatted YouTube description
        """
        # Get template
        template_str = self.DESCRIPTION_TEMPLATES.get(
            template,
            self.DESCRIPTION_TEMPLATES["default"]
        )

        # Prepare values
        genre_tag = self._clean_for_tag(genre)
        title_tag = self._clean_for_tag(title)
        mood = self._extract_mood(style_prompt, lyrics)

        # Truncate lyrics for preview
        lyrics_lines = [
            l for l in lyrics.split("\n")
            if l.strip() and not l.strip().startswith("[")
        ]
        lyrics_preview = "\n".join(lyrics_lines[:20])
        if len(lyrics_lines) > 20:
            lyrics_preview += "\n..."

        lyrics_full = "\n".join(lyrics_lines[:50])
        if len(lyrics_lines) > 50:
            lyrics_full += "\n\n[Full lyrics in video]"

        # Format template
        description = template_str.format(
            title=title,
            genre=genre,
            genre_tag=genre_tag,
            title_tag=title_tag,
            style_preview=style_prompt[:200] if style_prompt else "AI Generated",
            mood=mood,
            lyrics_preview=lyrics_preview,
            lyrics_full=lyrics_full,
        )

        # Ensure YouTube's 5000 char limit
        if len(description) > 4900:
            description = description[:4900] + "\n..."

        return description

    def suggest_title(
        self,
        original_title: str,
        genre: str,
        include_prefix: bool = False
    ) -> str:
        """Suggest a YouTube-optimized title.

        Args:
            original_title: Original song title
            genre: Song genre
            include_prefix: Whether to add emoji prefix

        Returns:
            Optimized YouTube title
        """
        title = original_title

        # Add genre prefix if requested
        if include_prefix:
            genre_prefixes = {
                "pop": "🎵",
                "rock": "🎸",
                "hip-hop": "🎤",
                "edm": "🎧",
                "jazz": "🎷",
                "country": "🤠",
            }
            prefix = genre_prefixes.get(genre.lower(), "🎶")
            title = f"{prefix} {title}"

        # Ensure title isn't too long (YouTube limit is 100 chars)
        if len(title) > 95:
            title = title[:92] + "..."

        return title

    def generate_all(
        self,
        title: str,
        genre: str,
        style_prompt: str,
        lyrics: str,
        template: str = "default"
    ) -> Dict[str, Any]:
        """Generate all metadata at once.

        Args:
            title: Song title
            genre: Song genre
            style_prompt: Style description
            lyrics: Song lyrics
            template: Description template name

        Returns:
            Dict with suggested_title, tags, and description
        """
        return {
            "suggested_title": self.suggest_title(title, genre),
            "tags": self.generate_tags(title, genre, style_prompt),
            "description": self.generate_description(
                title, genre, style_prompt, lyrics, template
            ),
        }


# Global instance
_metadata_generator: Optional[MetadataGenerator] = None


def get_metadata_generator() -> MetadataGenerator:
    """Get the global metadata generator instance.

    Returns:
        The singleton MetadataGenerator instance
    """
    global _metadata_generator
    if _metadata_generator is None:
        _metadata_generator = MetadataGenerator()
    return _metadata_generator
