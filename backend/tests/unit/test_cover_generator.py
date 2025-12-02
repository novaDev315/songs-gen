"""Unit tests for cover generator service."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from PIL import Image

from app.services.cover_generator import (
    TemplateCoverGenerator,
    OpenRouterCoverGenerator,
    generate_cover,
    get_available_templates,
)


class TestTemplateCoverGenerator:
    """Test template-based cover generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temporary output directory."""
        with patch("app.services.cover_generator.settings") as mock_settings:
            mock_settings.COVER_ART_PATH = str(tmp_path)
            gen = TemplateCoverGenerator()
            return gen

    def test_hex_to_rgb(self, generator):
        """Test hex color conversion."""
        assert generator._hex_to_rgb("#FF0000") == (255, 0, 0)
        assert generator._hex_to_rgb("#00FF00") == (0, 255, 0)
        assert generator._hex_to_rgb("#0000FF") == (0, 0, 255)
        assert generator._hex_to_rgb("FFFFFF") == (255, 255, 255)

    def test_create_gradient(self, generator):
        """Test gradient image creation."""
        gradient = generator._create_gradient((100, 100), "#FF0000", "#0000FF")
        assert gradient.size == (100, 100)
        assert gradient.mode == "RGB"

    def test_add_vignette(self, generator):
        """Test vignette effect."""
        image = Image.new("RGB", (100, 100), (255, 255, 255))
        result = generator._add_vignette(image)
        assert result.size == (100, 100)
        assert result.mode == "RGB"

    @pytest.mark.asyncio
    async def test_generate_pop_cover(self, generator, tmp_path):
        """Test pop genre cover generation."""
        output = await generator.generate(
            title="Test Song",
            genre="pop",
            template_id="gradient_bright",
            song_id="test123"
        )

        assert output.exists()
        assert output.suffix == ".png"
        assert output.parent == tmp_path

        # Verify image properties
        with Image.open(output) as img:
            assert img.size == (1280, 720)
            assert img.mode == "RGB"

    @pytest.mark.asyncio
    async def test_generate_with_subtitle(self, generator, tmp_path):
        """Test cover generation with subtitle."""
        output = await generator.generate(
            title="Test Song",
            genre="rock",
            template_id="dark_grunge",
            song_id="test456",
            subtitle="By Test Artist"
        )

        assert output.exists()
        with Image.open(output) as img:
            assert img.size == (1280, 720)

    @pytest.mark.asyncio
    async def test_generate_unknown_genre_fallback(self, generator, tmp_path):
        """Test fallback to pop for unknown genre."""
        output = await generator.generate(
            title="Test Song",
            genre="unknown-genre",
            template_id="gradient_bright",
            song_id="test789"
        )

        assert output.exists()

    @pytest.mark.asyncio
    async def test_generate_unknown_template_fallback(self, generator, tmp_path):
        """Test fallback to first template if template_id not found."""
        output = await generator.generate(
            title="Test Song",
            genre="pop",
            template_id="nonexistent-template",
            song_id="test101"
        )

        assert output.exists()

    def test_get_available_templates(self, generator):
        """Test retrieving available templates."""
        templates = generator.get_available_templates()

        assert "pop" in templates
        assert "rock" in templates
        assert "hip-hop" in templates
        assert "edm" in templates
        assert "jazz" in templates
        assert "country" in templates

        assert "gradient_bright" in templates["pop"]
        assert "dark_grunge" in templates["rock"]


class TestOpenRouterCoverGenerator:
    """Test AI-based cover generation."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temporary output directory."""
        with patch("app.services.cover_generator.settings") as mock_settings:
            mock_settings.COVER_ART_PATH = str(tmp_path)
            mock_settings.OPENROUTER_API_KEY = "test-api-key"
            mock_settings.OPENROUTER_MODEL = "test-model"
            mock_settings.OPENROUTER_SITE_URL = "https://test.com"
            gen = OpenRouterCoverGenerator()
            return gen

    def test_build_prompt_default(self, generator):
        """Test default prompt building."""
        prompt = generator._build_prompt(
            title="Test Song",
            genre="pop",
            style_prompt="upbeat, energetic"
        )

        assert "pop" in prompt.lower()
        assert "Test Song" in prompt
        assert "upbeat, energetic" in prompt
        assert "no text" in prompt.lower()

    def test_build_prompt_custom(self, generator):
        """Test custom prompt override."""
        custom = "A futuristic cyberpunk cityscape"
        prompt = generator._build_prompt(
            title="Test Song",
            genre="edm",
            style_prompt="",
            custom_prompt=custom
        )

        assert custom in prompt
        assert "no text" in prompt.lower()

    def test_resize_with_letterbox_landscape(self, generator):
        """Test letterboxing for landscape image."""
        # Create test image
        image = Image.new("RGB", (1000, 500), (255, 0, 0))
        result = generator._resize_with_letterbox(image, (1280, 720))

        assert result.size == (1280, 720)
        assert result.mode == "RGB"

    def test_resize_with_letterbox_portrait(self, generator):
        """Test letterboxing for portrait image."""
        # Create test image
        image = Image.new("RGB", (500, 1000), (0, 255, 0))
        result = generator._resize_with_letterbox(image, (1280, 720))

        assert result.size == (1280, 720)
        assert result.mode == "RGB"

    @pytest.mark.asyncio
    async def test_generate_no_api_key(self, tmp_path):
        """Test error when API key not configured."""
        with patch("app.services.cover_generator.settings") as mock_settings:
            mock_settings.COVER_ART_PATH = str(tmp_path)
            mock_settings.OPENROUTER_API_KEY = ""
            gen = OpenRouterCoverGenerator()

            with pytest.raises(ValueError, match="API key not configured"):
                await gen.generate(
                    title="Test",
                    genre="pop",
                    style_prompt="test",
                    song_id="test"
                )

    @pytest.mark.asyncio
    async def test_generate_api_success(self, generator, tmp_path):
        """Test successful AI generation."""
        # Mock API response
        mock_response_data = {
            "data": [{"url": "https://example.com/image.png"}]
        }

        # Create a test image to return
        test_image = Image.new("RGB", (1024, 1024), (100, 100, 100))
        test_image_bytes = BytesIO()
        test_image.save(test_image_bytes, "PNG")
        test_image_bytes.seek(0)

        with patch("aiohttp.ClientSession") as mock_session:
            # Mock API call
            mock_api_response = AsyncMock()
            mock_api_response.status = 200
            mock_api_response.json = AsyncMock(return_value=mock_response_data)

            # Mock image download
            mock_img_response = AsyncMock()
            mock_img_response.status = 200
            mock_img_response.read = AsyncMock(return_value=test_image_bytes.getvalue())

            mock_session_instance = AsyncMock()
            mock_session_instance.post = AsyncMock(return_value=mock_api_response)
            mock_session_instance.get = AsyncMock(return_value=mock_img_response)
            mock_session.return_value.__aenter__.return_value = mock_session_instance

            output = await generator.generate(
                title="Test Song",
                genre="pop",
                style_prompt="colorful, vibrant",
                song_id="test123"
            )

            assert output.exists()
            assert output.suffix == ".png"
            assert "_ai_cover.png" in output.name

    @pytest.mark.asyncio
    async def test_generate_api_error(self, generator):
        """Test handling of API errors."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_response.text = AsyncMock(return_value="Internal Server Error")

            mock_session_instance = AsyncMock()
            mock_session_instance.post = AsyncMock(return_value=mock_response)
            mock_session.return_value.__aenter__.return_value = mock_session_instance

            with pytest.raises(Exception, match="OpenRouter API error: 500"):
                await generator.generate(
                    title="Test",
                    genre="pop",
                    style_prompt="test",
                    song_id="test"
                )


class TestHelperFunctions:
    """Test module-level helper functions."""

    @pytest.mark.asyncio
    async def test_generate_cover_template_method(self, tmp_path):
        """Test generate_cover with template method."""
        with patch("app.services.cover_generator.template_generator") as mock_gen:
            mock_gen.generate = AsyncMock(return_value=Path("/test/output.png"))
            mock_gen.get_available_templates = Mock(return_value={
                "pop": ["gradient_bright"]
            })

            result = await generate_cover(
                title="Test",
                genre="pop",
                song_id="test123",
                method="template",
                template_id="gradient_bright"
            )

            mock_gen.generate.assert_called_once()
            assert result == Path("/test/output.png")

    @pytest.mark.asyncio
    async def test_generate_cover_ai_method(self):
        """Test generate_cover with AI method."""
        with patch("app.services.cover_generator.ai_generator") as mock_gen:
            mock_gen.generate = AsyncMock(return_value=Path("/test/ai_output.png"))

            result = await generate_cover(
                title="Test",
                genre="pop",
                song_id="test123",
                method="ai",
                style_prompt="futuristic"
            )

            mock_gen.generate.assert_called_once()
            assert result == Path("/test/ai_output.png")

    @pytest.mark.asyncio
    async def test_generate_cover_invalid_method(self):
        """Test error for invalid generation method."""
        with pytest.raises(ValueError, match="Invalid cover generation method"):
            await generate_cover(
                title="Test",
                genre="pop",
                song_id="test123",
                method="invalid"
            )

    def test_get_available_templates_helper(self):
        """Test get_available_templates helper function."""
        templates = get_available_templates()

        assert isinstance(templates, dict)
        assert "pop" in templates
        assert isinstance(templates["pop"], list)


# Import BytesIO for mock
from io import BytesIO
