"""Cover art generator service for YouTube Studio."""

import logging
from pathlib import Path
from typing import Optional
import math
import aiohttp
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class TemplateCoverGenerator:
    """Generate cover images from templates."""

    # Template configurations by genre
    TEMPLATES = {
        "pop": {
            "gradient_bright": {"colors": ["#FF6B6B", "#4ECDC4"], "text_color": "#FFFFFF"},
            "neon_city": {"colors": ["#A855F7", "#EC4899"], "text_color": "#FFFFFF"},
            "abstract_colorful": {"colors": ["#F59E0B", "#EF4444"], "text_color": "#FFFFFF"},
        },
        "rock": {
            "dark_grunge": {"colors": ["#1F1F1F", "#4B0082"], "text_color": "#FF4500"},
            "fire_smoke": {"colors": ["#8B0000", "#1C1C1C"], "text_color": "#FFD700"},
            "electric": {"colors": ["#0D0D0D", "#00D4FF"], "text_color": "#00D4FF"},
        },
        "hip-hop": {
            "urban_night": {"colors": ["#1A1A2E", "#E94560"], "text_color": "#FFD700"},
            "gold_chains": {"colors": ["#1C1C1C", "#B8860B"], "text_color": "#FFD700"},
            "street_art": {"colors": ["#2D2D2D", "#7B68EE"], "text_color": "#00FF00"},
        },
        "edm": {
            "laser_grid": {"colors": ["#000033", "#00FFFF"], "text_color": "#00FFFF"},
            "spectrum": {"colors": ["#0A0A0A", "#FF00FF"], "text_color": "#FFFFFF"},
            "dj_silhouette": {"colors": ["#1A0033", "#FF6600"], "text_color": "#FFFFFF"},
        },
        "jazz": {
            "vintage_sepia": {"colors": ["#704214", "#F5DEB3"], "text_color": "#2F1810"},
            "piano_keys": {"colors": ["#1C1C1C", "#F5F5F5"], "text_color": "#FFD700"},
            "smoky_club": {"colors": ["#2C2C2C", "#8B4513"], "text_color": "#D4AF37"},
        },
        "country": {
            "sunset_field": {"colors": ["#87CEEB", "#FF8C00"], "text_color": "#FFFFFF"},
            "acoustic_wood": {"colors": ["#8B4513", "#DEB887"], "text_color": "#FFFFFF"},
            "barn": {"colors": ["#8B0000", "#1C1C1C"], "text_color": "#FFD700"},
        },
    }

    OUTPUT_SIZE = (1280, 720)  # YouTube thumbnail size

    def __init__(self):
        self.output_dir = Path(settings.COVER_ART_PATH)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._font_cache = {}

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get font with caching."""
        key = (size, bold)
        if key not in self._font_cache:
            # Try common fonts, fallback to default
            font_names = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            for font_name in font_names:
                try:
                    self._font_cache[key] = ImageFont.truetype(font_name, size)
                    logger.debug(f"Loaded font: {font_name}")
                    break
                except (OSError, IOError):
                    continue
            else:
                logger.warning("No truetype fonts found, using default font")
                self._font_cache[key] = ImageFont.load_default()
        return self._font_cache[key]

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _create_gradient(
        self,
        size: tuple[int, int],
        color1: str,
        color2: str,
        angle: float = 45
    ) -> Image.Image:
        """Create a gradient image."""
        width, height = size
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)

        image = Image.new("RGB", size)
        pixels = image.load()

        # Calculate gradient based on angle
        angle_rad = math.radians(angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)

        for y in range(height):
            for x in range(width):
                # Normalize position along gradient direction
                t = (x * cos_a + y * sin_a) / (width * cos_a + height * sin_a)
                t = max(0, min(1, t))

                # Interpolate colors
                r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * t)
                g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * t)
                b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * t)
                pixels[x, y] = (r, g, b)

        return image

    def _add_text_with_shadow(
        self,
        image: Image.Image,
        text: str,
        position: tuple[int, int],
        font: ImageFont.FreeTypeFont,
        text_color: str,
        shadow_color: str = "#000000",
        shadow_offset: int = 4
    ) -> Image.Image:
        """Add text with shadow effect."""
        draw = ImageDraw.Draw(image)

        # Draw shadow
        shadow_pos = (position[0] + shadow_offset, position[1] + shadow_offset)
        draw.text(shadow_pos, text, font=font, fill=shadow_color)

        # Draw main text
        draw.text(position, text, font=font, fill=text_color)

        return image

    def _add_vignette(self, image: Image.Image, intensity: float = 0.4) -> Image.Image:
        """Add vignette effect to image."""
        width, height = image.size

        # Create radial gradient mask
        mask = Image.new("L", (width, height), 255)
        pixels = mask.load()

        center_x, center_y = width // 2, height // 2
        max_dist = ((width/2)**2 + (height/2)**2) ** 0.5

        for y in range(height):
            for x in range(width):
                dist = ((x - center_x)**2 + (y - center_y)**2) ** 0.5
                factor = 1 - (dist / max_dist) * intensity
                pixels[x, y] = int(255 * max(0, factor))

        # Apply vignette
        darkened = Image.new("RGB", (width, height), (0, 0, 0))
        return Image.composite(image, darkened, mask)

    async def generate(
        self,
        title: str,
        genre: str,
        template_id: str,
        song_id: str,
        subtitle: Optional[str] = None
    ) -> Path:
        """Generate cover image from template."""
        logger.info(f"Generating template cover for song {song_id}: {template_id}")

        # Get template config
        genre_lower = genre.lower()
        if genre_lower not in self.TEMPLATES:
            logger.warning(f"Genre '{genre}' not found, using 'pop' as default")
            genre_lower = "pop"  # Default fallback

        genre_templates = self.TEMPLATES[genre_lower]
        if template_id not in genre_templates:
            logger.warning(f"Template '{template_id}' not found for genre '{genre}', using first available")
            template_id = list(genre_templates.keys())[0]

        template = genre_templates[template_id]

        # Create gradient background
        image = self._create_gradient(
            self.OUTPUT_SIZE,
            template["colors"][0],
            template["colors"][1]
        )

        # Add vignette effect
        image = self._add_vignette(image)

        # Calculate text position (centered)
        draw = ImageDraw.Draw(image)
        title_font = self._get_font(72, bold=True)

        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), title, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = (self.OUTPUT_SIZE[0] - text_width) // 2
        y = (self.OUTPUT_SIZE[1] - text_height) // 2 - 30

        # Add title with shadow
        self._add_text_with_shadow(
            image, title, (x, y),
            title_font,
            template["text_color"]
        )

        # Add subtitle if provided
        if subtitle:
            subtitle_font = self._get_font(36)
            bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_width = bbox[2] - bbox[0]
            sub_x = (self.OUTPUT_SIZE[0] - sub_width) // 2
            sub_y = y + text_height + 20

            self._add_text_with_shadow(
                image, subtitle, (sub_x, sub_y),
                subtitle_font,
                template["text_color"],
                shadow_offset=2
            )

        # Save image
        output_path = self.output_dir / f"{song_id}_cover.png"
        image.save(str(output_path), "PNG", quality=95)

        logger.info(f"Template cover generated: {output_path}")
        return output_path

    def get_available_templates(self) -> dict:
        """Return available templates organized by genre."""
        return {
            genre: list(templates.keys())
            for genre, templates in self.TEMPLATES.items()
        }


class OpenRouterCoverGenerator:
    """Generate AI cover images via OpenRouter API."""

    API_URL = "https://openrouter.ai/api/v1/images/generations"

    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.site_url = settings.OPENROUTER_SITE_URL
        self.output_dir = Path(settings.COVER_ART_PATH)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _build_prompt(
        self,
        title: str,
        genre: str,
        style_prompt: str,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Build image generation prompt."""
        if custom_prompt:
            return f"{custom_prompt}. Professional album cover art style, no text, no words, visually striking."

        genre_styles = {
            "pop": "colorful, vibrant, modern, glossy",
            "rock": "dark, edgy, electric, powerful",
            "hip-hop": "urban, gold accents, street style, bold",
            "edm": "neon lights, abstract, futuristic, electronic",
            "jazz": "vintage, warm tones, sophisticated, smoky",
            "country": "rustic, sunset, acoustic, natural",
        }

        style = genre_styles.get(genre.lower(), "artistic, professional")

        return f"""Album cover art for a {genre} song titled "{title}".
Style: {style}
Mood hints: {style_prompt[:150] if style_prompt else 'modern, professional'}
Requirements: Professional album artwork, absolutely no text or words,
visually striking composition, high contrast, suitable for YouTube thumbnail."""

    async def generate(
        self,
        title: str,
        genre: str,
        style_prompt: str,
        song_id: str,
        custom_prompt: Optional[str] = None
    ) -> Path:
        """Generate AI cover image via OpenRouter."""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured in settings")

        logger.info(f"Generating AI cover for song {song_id} via OpenRouter")

        prompt = self._build_prompt(title, genre, style_prompt, custom_prompt)

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": "SongFlow Studio",
                "Content-Type": "application/json",
            }

            payload = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": "1024x1024",
            }

            try:
                async with session.post(self.API_URL, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API error: {response.status} - {error_text}")

                    result = await response.json()
            except aiohttp.ClientError as e:
                logger.error(f"HTTP request failed: {e}")
                raise Exception(f"Failed to connect to OpenRouter API: {e}")

        # Download and save the generated image
        image_url = result["data"][0]["url"]
        output_path = await self._download_and_resize(image_url, song_id)

        logger.info(f"AI cover generated: {output_path}")
        return output_path

    async def _download_and_resize(self, url: str, song_id: str) -> Path:
        """Download image and resize to YouTube thumbnail size."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download image: {response.status}")
                image_data = await response.read()

        # Load and resize image
        image = Image.open(BytesIO(image_data))

        # Resize to 1280x720 with letterboxing if needed
        image = self._resize_with_letterbox(image, (1280, 720))

        # Save
        output_path = self.output_dir / f"{song_id}_ai_cover.png"
        image.save(str(output_path), "PNG", quality=95)

        return output_path

    def _resize_with_letterbox(
        self,
        image: Image.Image,
        target_size: tuple[int, int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio with letterboxing."""
        target_w, target_h = target_size
        orig_w, orig_h = image.size

        # Calculate scale factor
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        # Resize
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Create canvas and paste centered
        canvas = Image.new("RGB", target_size, (0, 0, 0))
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y))

        return canvas


# Singleton instances for easy access
template_generator = TemplateCoverGenerator()
ai_generator = OpenRouterCoverGenerator()


async def generate_cover(
    title: str,
    genre: str,
    song_id: str,
    method: str = "template",
    template_id: Optional[str] = None,
    style_prompt: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    subtitle: Optional[str] = None
) -> Path:
    """
    Generate cover art using specified method.

    Args:
        title: Song title to display on cover
        genre: Song genre (affects template selection)
        song_id: Unique song identifier
        method: "template" or "ai"
        template_id: Template ID (for template method)
        style_prompt: Suno style prompt (for AI method)
        custom_prompt: Custom AI prompt override
        subtitle: Optional subtitle text

    Returns:
        Path to generated cover image
    """
    if method == "template":
        if not template_id:
            # Get first available template for genre
            templates = template_generator.get_available_templates()
            genre_key = genre.lower() if genre.lower() in templates else "pop"
            template_id = list(templates[genre_key].keys())[0]

        return await template_generator.generate(
            title=title,
            genre=genre,
            template_id=template_id,
            song_id=song_id,
            subtitle=subtitle
        )
    elif method == "ai":
        return await ai_generator.generate(
            title=title,
            genre=genre,
            style_prompt=style_prompt or "",
            song_id=song_id,
            custom_prompt=custom_prompt
        )
    else:
        raise ValueError(f"Invalid cover generation method: {method}. Use 'template' or 'ai'")


def get_available_templates() -> dict:
    """Get all available template IDs organized by genre."""
    return template_generator.get_available_templates()
