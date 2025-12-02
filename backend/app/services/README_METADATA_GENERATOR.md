# Metadata Generator Service

Auto-generates YouTube metadata (title, tags, description) from song data.

## Overview

The `MetadataGenerator` service creates optimized YouTube metadata for AI-generated songs. It analyzes song content to generate:
- **YouTube-optimized titles** with optional emoji prefixes
- **Relevant tags** (max 15) including AI music tags, genre tags, and content-based keywords
- **Formatted descriptions** with lyrics previews and customizable templates

## Usage

### Basic Example

```python
from app.services.metadata_generator import get_metadata_generator

# Get singleton instance
generator = get_metadata_generator()

# Generate all metadata at once
metadata = generator.generate_all(
    title="Midnight Dreams",
    genre="pop",
    style_prompt="dreamy pop with ethereal synths and soft vocals",
    lyrics="""[Verse 1]
Dancing in the moonlight
Stars above shining bright

[Chorus]
Midnight dreams come alive
In the silver sky we thrive
"""
)

# Result contains:
# metadata["suggested_title"] - YouTube-optimized title
# metadata["tags"] - List of 15 tags
# metadata["description"] - Formatted description
```

### Generate Individual Components

```python
# Generate tags only
tags = generator.generate_tags(
    title="Summer Vibes",
    genre="edm",
    style_prompt="upbeat electronic dance music with tropical house elements",
    max_tags=15
)
# ['ai music', 'ai generated', 'edm', 'electronic', 'dance music', ...]

# Generate description with template
description = generator.generate_description(
    title="Epic Journey",
    genre="rock",
    style_prompt="powerful rock with electric guitars",
    lyrics="[Verse 1]\n...",
    template="detailed"  # Options: "default", "minimal", "detailed"
)

# Suggest YouTube title
title = generator.suggest_title(
    original_title="My Song",
    genre="pop",
    include_prefix=True  # Adds genre emoji (🎵 for pop)
)
# Result: "🎵 My Song"
```

## API Reference

### `MetadataGenerator`

Main class for generating YouTube metadata.

#### Methods

##### `generate_tags(title, genre, style_prompt="", max_tags=15) -> List[str]`

Generate YouTube tags from song metadata.

**Parameters:**
- `title` (str): Song title
- `genre` (str): Song genre (pop, rock, hip-hop, edm, jazz, country, etc.)
- `style_prompt` (str, optional): Style description
- `max_tags` (int, optional): Maximum number of tags to return (default: 15)

**Returns:**
- List of YouTube tags (no duplicates)

**Example:**
```python
tags = generator.generate_tags(
    title="Night Rider",
    genre="synthwave",
    style_prompt="80s retro synthwave with neon vibes"
)
```

##### `generate_description(title, genre, style_prompt, lyrics, template="default") -> str`

Generate YouTube description from template.

**Parameters:**
- `title` (str): Song title
- `genre` (str): Song genre
- `style_prompt` (str): Style description
- `lyrics` (str): Song lyrics
- `template` (str, optional): Template name ("default", "minimal", "detailed")

**Returns:**
- Formatted description (max 5000 chars for YouTube)

**Templates:**
- `"default"`: Balanced format with genre, style, lyrics preview, and AI attribution
- `"minimal"`: Simple format with just title, genre, and lyrics
- `"detailed"`: Extended format with mood analysis, full lyrics section, and CTAs

**Example:**
```python
description = generator.generate_description(
    title="Sunset Drive",
    genre="lo-fi",
    style_prompt="chill lo-fi beats with jazz piano",
    lyrics="...",
    template="minimal"
)
```

##### `suggest_title(original_title, genre, include_prefix=False) -> str`

Suggest a YouTube-optimized title.

**Parameters:**
- `original_title` (str): Original song title
- `genre` (str): Song genre
- `include_prefix` (bool, optional): Add genre emoji prefix (default: False)

**Returns:**
- Optimized title (max 100 chars for YouTube)

**Genre Emojis:**
- pop: 🎵
- rock: 🎸
- hip-hop: 🎤
- edm: 🎧
- jazz: 🎷
- country: 🤠
- default: 🎶

**Example:**
```python
title = generator.suggest_title("My Song", "rock", include_prefix=True)
# Result: "🎸 My Song"
```

##### `generate_all(title, genre, style_prompt, lyrics, template="default") -> Dict[str, Any]`

Generate all metadata at once.

**Parameters:**
- Same as individual methods

**Returns:**
- Dictionary with keys:
  - `suggested_title` (str): Optimized YouTube title
  - `tags` (List[str]): List of YouTube tags
  - `description` (str): Formatted description

**Example:**
```python
metadata = generator.generate_all(
    title="Ocean Waves",
    genre="ambient",
    style_prompt="peaceful ambient soundscape",
    lyrics="..."
)
```

### `get_metadata_generator() -> MetadataGenerator`

Get the global MetadataGenerator instance (singleton pattern).

**Returns:**
- MetadataGenerator instance

## Integration Examples

### With Song Model

```python
from app.models.song import Song
from app.services.metadata_generator import get_metadata_generator

async def prepare_youtube_metadata(song: Song):
    """Generate YouTube metadata for a song."""
    generator = get_metadata_generator()

    metadata = generator.generate_all(
        title=song.title,
        genre=song.genre,
        style_prompt=song.style_prompt,
        lyrics=song.lyrics,
        template="default"
    )

    return metadata
```

### With YouTube Uploader

```python
from app.services.metadata_generator import get_metadata_generator
from app.services.youtube_uploader import get_youtube_uploader

async def upload_to_youtube(song_id: str, video_path: Path):
    """Upload song to YouTube with auto-generated metadata."""
    # Get song data
    song = await get_song(song_id)

    # Generate metadata
    generator = get_metadata_generator()
    metadata = generator.generate_all(
        title=song.title,
        genre=song.genre,
        style_prompt=song.style_prompt,
        lyrics=song.lyrics
    )

    # Upload to YouTube
    uploader = get_youtube_uploader()
    result = await uploader.upload_video(
        video_file=video_path,
        title=metadata["suggested_title"],
        description=metadata["description"],
        tags=metadata["tags"],
        privacy_status="public"
    )

    return result
```

### In Studio Wizard (Frontend)

```typescript
// TypeScript/React example
interface SongMetadata {
  title: string;
  genre: string;
  stylePrompt: string;
  lyrics: string;
}

async function generateMetadata(song: SongMetadata) {
  const response = await fetch('/api/metadata/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(song)
  });

  const metadata = await response.json();

  // metadata.suggested_title
  // metadata.tags
  // metadata.description

  return metadata;
}
```

## Features

### Intelligent Tag Generation

- **AI Music Tags**: Always includes "ai music", "ai generated", "ai song"
- **Genre Tags**: Genre-specific tags (e.g., pop → "pop music", "pop song", "catchy")
- **Style Keywords**: Extracts keywords from style prompt (e.g., "acoustic", "guitar", "synth")
- **Title Tags**: Generates hashtag from title
- **No Duplicates**: Automatically removes duplicate tags

### Mood Detection

Automatically detects mood from style prompt and lyrics:
- Happy (upbeat, cheerful, joy)
- Sad (melancholy, heartbreak, tears)
- Energetic (powerful, intense, hype)
- Chill (relaxed, smooth, calm)
- Romantic (love, passion, heart)
- Dark (angry, aggressive, heavy)
- Nostalgic (memories, past, remember)
- Motivational (inspire, strength, overcome)

### Description Templates

**Default Template:**
```
{title}

🎵 Genre: {genre}
🎨 Style: {style_preview}

---
📝 LYRICS:
{lyrics_preview}

---
🤖 This song was created with AI music generation technology.

#AIMusic #{genre_tag} #NewMusic #MusicVideo
```

**Minimal Template:**
Simple format without emojis or hashtags.

**Detailed Template:**
Extended format with mood analysis, full lyrics section, subscribe/like CTAs, and comprehensive hashtags.

## Constraints

- **YouTube Title**: Max 100 characters (automatically truncated)
- **YouTube Description**: Max 5000 characters (automatically truncated)
- **Tags**: Max 15 tags by default (configurable)
- **Lyrics Preview**: First 20 lines in default template
- **Full Lyrics**: First 50 lines in detailed template

## Notes

- Structure tags like `[Verse 1]`, `[Chorus]` are filtered from lyrics previews
- Long titles are truncated with "..." to fit YouTube's 100-char limit
- All metadata respects YouTube's character limits and best practices
- Genre emojis are only added when `include_prefix=True`
- Tags are deduplicated and lowercase-normalized

## Testing

Run unit tests:
```bash
pytest tests/unit/test_metadata_generator.py -v
```

Test coverage includes:
- Tag generation for all genres
- Description templates (default, minimal, detailed)
- Title suggestions with and without emojis
- Mood detection from style/lyrics
- Edge cases (empty inputs, long content, special characters)
- Singleton pattern
