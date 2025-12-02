# Cover Art Generator Guide

## Overview

The Cover Art Generator service provides two methods for creating YouTube-ready cover images:

1. **Template-based generation** - Fast, customizable gradients with text overlays
2. **AI-based generation** - Creative AI-generated artwork via OpenRouter API

## Features

- **YouTube-optimized output**: 1280x720 images perfect for thumbnails
- **Genre-specific templates**: Pre-configured color schemes for each genre
- **Text effects**: Shadow/glow effects for professional-looking text
- **Vignette effects**: Automatic edge darkening for depth
- **AI generation**: Optional AI-powered unique artwork
- **Letterboxing**: Automatic aspect ratio handling

## Template-Based Generation

### Available Templates

**Pop**
- `gradient_bright` - Pink to teal gradient, white text
- `neon_city` - Purple to pink gradient, white text
- `abstract_colorful` - Orange to red gradient, white text

**Rock**
- `dark_grunge` - Dark to purple gradient, orange-red text
- `fire_smoke` - Dark red to black gradient, gold text
- `electric` - Black to cyan gradient, cyan text

**Hip-Hop**
- `urban_night` - Dark blue to red gradient, gold text
- `gold_chains` - Black to gold gradient, gold text
- `street_art` - Dark to purple gradient, green text

**EDM**
- `laser_grid` - Dark blue to cyan gradient, cyan text
- `spectrum` - Black to magenta gradient, white text
- `dj_silhouette` - Dark purple to orange gradient, white text

**Jazz**
- `vintage_sepia` - Brown to beige gradient, dark brown text
- `piano_keys` - Black to white gradient, gold text
- `smoky_club` - Dark to brown gradient, gold text

**Country**
- `sunset_field` - Sky blue to orange gradient, white text
- `acoustic_wood` - Brown to tan gradient, white text
- `barn` - Dark red to black gradient, gold text

### Usage Example

```python
from app.services.cover_generator import generate_cover

# Generate template-based cover
output_path = await generate_cover(
    title="Summer Vibes",
    genre="pop",
    song_id="song_123",
    method="template",
    template_id="gradient_bright",
    subtitle="By Artist Name"  # Optional
)
```

## AI-Based Generation

### Requirements

1. OpenRouter API key (get from https://openrouter.ai/keys)
2. Configure in `.env`:
   ```bash
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_MODEL=stabilityai/stable-diffusion-xl
   OPENROUTER_SITE_URL=https://songflow.app
   ```

### Usage Example

```python
from app.services.cover_generator import generate_cover

# Generate AI cover with default prompt
output_path = await generate_cover(
    title="Epic Journey",
    genre="rock",
    song_id="song_456",
    method="ai",
    style_prompt="powerful, epic, electric guitar, stadium rock"
)

# Generate AI cover with custom prompt
output_path = await generate_cover(
    title="Neon Dreams",
    genre="edm",
    song_id="song_789",
    method="ai",
    custom_prompt="Futuristic cyberpunk cityscape at night, neon lights, rain-soaked streets"
)
```

### AI Prompt Building

The service automatically builds prompts from:
- **Title**: Song title for context
- **Genre**: Influences visual style keywords
- **Style prompt**: Suno style prompt provides mood hints
- **Custom prompt**: Override with your own detailed description

**Genre-specific AI styles:**
- Pop: colorful, vibrant, modern, glossy
- Rock: dark, edgy, electric, powerful
- Hip-Hop: urban, gold accents, street style, bold
- EDM: neon lights, abstract, futuristic, electronic
- Jazz: vintage, warm tones, sophisticated, smoky
- Country: rustic, sunset, acoustic, natural

## API Integration

### FastAPI Endpoint Example

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.cover_generator import generate_cover, get_available_templates

router = APIRouter()

class CoverGenerateRequest(BaseModel):
    title: str
    genre: str
    song_id: str
    method: str = "template"  # "template" or "ai"
    template_id: str | None = None
    style_prompt: str | None = None
    custom_prompt: str | None = None
    subtitle: str | None = None

@router.post("/covers/generate")
async def create_cover(request: CoverGenerateRequest):
    """Generate cover art for a song."""
    try:
        output_path = await generate_cover(
            title=request.title,
            genre=request.genre,
            song_id=request.song_id,
            method=request.method,
            template_id=request.template_id,
            style_prompt=request.style_prompt,
            custom_prompt=request.custom_prompt,
            subtitle=request.subtitle
        )
        return {"cover_url": f"/covers/{output_path.name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/covers/templates")
async def list_templates():
    """Get available template IDs by genre."""
    return get_available_templates()
```

## Output

All generated images are saved to the configured output directory:
```
COVER_ART_PATH=./data/covers  # From .env
```

Output filenames:
- Template: `{song_id}_cover.png`
- AI: `{song_id}_ai_cover.png`

## Performance

**Template Generation:**
- Speed: ~1-2 seconds
- Cost: Free
- Quality: Consistent, professional

**AI Generation:**
- Speed: ~5-15 seconds (API dependent)
- Cost: ~$0.01-0.05 per image (varies by model)
- Quality: Unique, creative, variable

## Best Practices

### When to Use Templates

✅ Use templates when:
- You need fast generation
- Consistency is important
- Budget is a concern
- Text-based covers are acceptable

### When to Use AI

✅ Use AI when:
- You want unique, creative artwork
- Visual storytelling is important
- You have API budget available
- The song is a major release

## Error Handling

The service handles common errors:

```python
try:
    cover = await generate_cover(...)
except ValueError as e:
    # Invalid method or missing API key
    logger.error(f"Configuration error: {e}")
except Exception as e:
    # Network error, file system error, etc.
    logger.error(f"Generation failed: {e}")
```

## Customization

### Adding New Templates

Edit `app/services/cover_generator.py`:

```python
TEMPLATES = {
    "pop": {
        "your_template_id": {
            "colors": ["#START_HEX", "#END_HEX"],
            "text_color": "#TEXT_HEX"
        },
        # ... existing templates
    }
}
```

### Changing Output Size

Default is 1280x720 (YouTube thumbnail). To change:

```python
class TemplateCoverGenerator:
    OUTPUT_SIZE = (1920, 1080)  # Full HD
```

### Custom Fonts

The service tries to load fonts in this order:
1. DejaVu Sans (Linux)
2. Liberation Sans (Linux)
3. Helvetica (macOS)
4. Default fallback

To use custom fonts, modify `_get_font()` method.

## Troubleshooting

**"No module named 'Pillow'"**
```bash
pip install Pillow==10.1.0
```

**"OpenRouter API key not configured"**
```bash
# Add to .env
OPENROUTER_API_KEY=your_key_here
```

**"Font not found" warning**
- Service falls back to default font
- Install DejaVu fonts: `apt-get install fonts-dejavu`

**Generated image has wrong colors**
- Check hex color format: `#RRGGBB`
- Ensure hex colors are valid (no typos)

**AI generation fails with 500 error**
- Check API key validity
- Verify OpenRouter account has credits
- Check model name is correct

## Examples

### Example 1: Quick Template Cover

```python
# Simple pop song cover
cover = await generate_cover(
    title="Dancing All Night",
    genre="pop",
    song_id="pop001",
    method="template"
)
# Uses first pop template by default
```

### Example 2: Specific Template with Subtitle

```python
# Rock cover with artist name
cover = await generate_cover(
    title="Thunder Road",
    genre="rock",
    song_id="rock001",
    method="template",
    template_id="fire_smoke",
    subtitle="The Lightning Bolts"
)
```

### Example 3: AI Cover from Style Prompt

```python
# EDM cover generated from Suno style
cover = await generate_cover(
    title="Electric Dreams",
    genre="edm",
    song_id="edm001",
    method="ai",
    style_prompt="Energetic EDM, supersaw leads, sidechained kick, festival anthem, 128 BPM"
)
```

### Example 4: AI Cover with Custom Prompt

```python
# Fully custom AI artwork
cover = await generate_cover(
    title="Midnight Jazz",
    genre="jazz",
    song_id="jazz001",
    method="ai",
    custom_prompt="1940s jazz club interior, smoky atmosphere, saxophone silhouette, warm amber lighting, art deco style"
)
```

## Integration with YouTube Upload

```python
from app.services.cover_generator import generate_cover
from app.services.youtube_client import YouTubeClient

# Generate cover
cover_path = await generate_cover(
    title=song.title,
    genre=song.genre,
    song_id=song.id,
    method="ai",
    style_prompt=song.style_prompt
)

# Use as YouTube thumbnail
youtube = YouTubeClient()
await youtube.upload_video(
    video_path=song.video_path,
    title=song.title,
    description=song.description,
    thumbnail_path=cover_path  # Use generated cover
)
```

## Cost Considerations

**Template Generation:**
- CPU cost: Negligible (~0.1s on modern CPU)
- Storage: ~200KB per image
- Free forever

**AI Generation via OpenRouter:**
- Stable Diffusion XL: ~$0.01-0.02 per image
- DALL-E 3: ~$0.04-0.08 per image
- Midjourney: ~$0.02-0.04 per image

For 100 songs/month:
- Templates: $0
- AI (SDXL): ~$1-2/month
- AI (DALL-E): ~$4-8/month

## Security

**API Key Protection:**
- Never commit `.env` to git
- Use environment variables
- Rotate keys periodically

**File System:**
- Output directory created automatically
- Files written with 644 permissions
- No user input in filenames (uses song_id)

## Future Enhancements

Planned features:
- [ ] Pre-built template backgrounds (not just gradients)
- [ ] Text positioning options (top, center, bottom)
- [ ] Multiple font choices
- [ ] Image filters (blur, sharpen, contrast)
- [ ] Batch generation endpoint
- [ ] Cover A/B testing tools
- [ ] Template editor UI

---

**Last Updated:** 2025-11-30
**Version:** 1.0.0
**Maintainer:** SongFlow Studio Team
