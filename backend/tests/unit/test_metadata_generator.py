"""Unit tests for metadata generator service.

Tests for YouTube metadata generation from song data.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.metadata_generator import (
    MetadataGenerator,
    get_metadata_generator,
)


@pytest.mark.unit
class TestMetadataGenerator:
    """Test MetadataGenerator class."""

    def test_init_creates_instance(self):
        """Test that initialization creates a metadata generator instance."""
        generator = MetadataGenerator()
        assert generator is not None

    def test_genre_tags_defined(self):
        """Test that genre tags are properly defined."""
        generator = MetadataGenerator()
        assert "pop" in generator.GENRE_TAGS
        assert "rock" in generator.GENRE_TAGS
        assert "hip-hop" in generator.GENRE_TAGS
        assert isinstance(generator.GENRE_TAGS["pop"], list)

    def test_ai_tags_defined(self):
        """Test that AI music tags are defined."""
        generator = MetadataGenerator()
        assert len(generator.AI_TAGS) > 0
        assert "ai music" in generator.AI_TAGS

    def test_description_templates_defined(self):
        """Test that description templates exist."""
        generator = MetadataGenerator()
        assert "default" in generator.DESCRIPTION_TEMPLATES
        assert "minimal" in generator.DESCRIPTION_TEMPLATES
        assert "detailed" in generator.DESCRIPTION_TEMPLATES


@pytest.mark.unit
class TestMetadataGeneratorCleanForTag:
    """Test MetadataGenerator._clean_for_tag method."""

    def test_clean_for_tag_simple_text(self):
        """Test cleaning simple text for hashtag."""
        generator = MetadataGenerator()
        result = generator._clean_for_tag("Hello World")
        assert result == "HelloWorld"

    def test_clean_for_tag_with_special_chars(self):
        """Test cleaning text with special characters."""
        generator = MetadataGenerator()
        result = generator._clean_for_tag("Love's Song!")
        assert result == "LovesSong"

    def test_clean_for_tag_max_three_words(self):
        """Test that only first 3 words are used."""
        generator = MetadataGenerator()
        result = generator._clean_for_tag("One Two Three Four Five")
        assert result == "OneTwoThree"

    def test_clean_for_tag_empty_string(self):
        """Test cleaning empty string."""
        generator = MetadataGenerator()
        result = generator._clean_for_tag("")
        assert result == ""


@pytest.mark.unit
class TestMetadataGeneratorExtractMood:
    """Test MetadataGenerator._extract_mood method."""

    def test_extract_mood_happy(self):
        """Test detecting happy mood."""
        generator = MetadataGenerator()
        result = generator._extract_mood("upbeat cheerful music", "joy and happiness")
        assert result == "Happy"

    def test_extract_mood_sad(self):
        """Test detecting sad mood."""
        generator = MetadataGenerator()
        result = generator._extract_mood("melancholy ballad", "heartbreak and tears")
        assert result == "Sad"

    def test_extract_mood_energetic(self):
        """Test detecting energetic mood."""
        generator = MetadataGenerator()
        result = generator._extract_mood("powerful intense beat", "fire and energy")
        assert result == "Energetic"

    def test_extract_mood_chill(self):
        """Test detecting chill mood."""
        generator = MetadataGenerator()
        result = generator._extract_mood("relaxed smooth vibes", "calm and laid-back")
        assert result == "Chill"

    def test_extract_mood_romantic(self):
        """Test detecting romantic mood."""
        generator = MetadataGenerator()
        result = generator._extract_mood("romantic melody", "love and passion")
        assert result == "Romantic"

    def test_extract_mood_default(self):
        """Test default mood when nothing matches."""
        generator = MetadataGenerator()
        result = generator._extract_mood("unusual style", "random lyrics")
        assert result == "Expressive"


@pytest.mark.unit
class TestMetadataGeneratorExtractStyleKeywords:
    """Test MetadataGenerator._extract_style_keywords method."""

    def test_extract_style_keywords_found(self):
        """Test extracting style keywords when present."""
        generator = MetadataGenerator()
        result = generator._extract_style_keywords("acoustic guitar with piano and synth")
        assert "acoustic" in result
        assert "guitar" in result
        assert "piano" in result
        assert "synth" in result

    def test_extract_style_keywords_max_five(self):
        """Test that maximum 5 keywords are returned."""
        generator = MetadataGenerator()
        style = "acoustic electric guitar piano bass drums synth vocal melody rhythm"
        result = generator._extract_style_keywords(style)
        assert len(result) <= 5

    def test_extract_style_keywords_empty_prompt(self):
        """Test extraction with empty prompt."""
        generator = MetadataGenerator()
        result = generator._extract_style_keywords("")
        assert result == []

    def test_extract_style_keywords_none_found(self):
        """Test when no keywords match."""
        generator = MetadataGenerator()
        result = generator._extract_style_keywords("random unknown terms")
        assert result == []


@pytest.mark.unit
class TestMetadataGeneratorGenerateTags:
    """Test MetadataGenerator.generate_tags method."""

    def test_generate_tags_basic(self):
        """Test basic tag generation."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="My Song",
            genre="pop",
            style_prompt="upbeat pop music with synth"
        )
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert "ai music" in tags  # AI tags included
        assert "pop music" in tags or "pop song" in tags  # Genre tags

    def test_generate_tags_max_limit(self):
        """Test that max_tags limit is respected."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="My Song",
            genre="pop",
            style_prompt="upbeat pop music with synth",
            max_tags=5
        )
        assert len(tags) <= 5

    def test_generate_tags_no_duplicates(self):
        """Test that duplicate tags are removed."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="Pop Song",
            genre="pop",
            style_prompt="pop music with pop vibes"
        )
        # Check for uniqueness
        assert len(tags) == len(set([t.lower() for t in tags]))

    def test_generate_tags_unknown_genre(self):
        """Test tag generation with unknown genre."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="My Song",
            genre="unknown-genre",
            style_prompt=""
        )
        assert "unknown-genre" in tags

    def test_generate_tags_hip_hop(self):
        """Test hip-hop specific tags."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="Rap Battle",
            genre="hip-hop",
            style_prompt="hard-hitting beats with flow"
        )
        assert any("hip hop" in tag or "rap" in tag for tag in tags)

    def test_generate_tags_includes_style_keywords(self):
        """Test that style keywords are included in tags."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(
            title="My Song",
            genre="pop",
            style_prompt="acoustic guitar melody"
        )
        assert "acoustic" in tags or "guitar" in tags or "melody" in tags


@pytest.mark.unit
class TestMetadataGeneratorGenerateDescription:
    """Test MetadataGenerator.generate_description method."""

    def test_generate_description_default_template(self):
        """Test description generation with default template."""
        generator = MetadataGenerator()
        description = generator.generate_description(
            title="My Test Song",
            genre="pop",
            style_prompt="upbeat pop music",
            lyrics="[Verse 1]\nTest lyrics\nMore lyrics"
        )
        assert "My Test Song" in description
        assert "pop" in description.lower()
        assert "Test lyrics" in description
        assert "AI" in description or "ai" in description

    def test_generate_description_minimal_template(self):
        """Test description generation with minimal template."""
        generator = MetadataGenerator()
        description = generator.generate_description(
            title="My Song",
            genre="rock",
            style_prompt="rock music",
            lyrics="Test lyrics",
            template="minimal"
        )
        assert "My Song" in description
        assert "rock" in description.lower()
        assert len(description) < 500  # Minimal should be shorter

    def test_generate_description_detailed_template(self):
        """Test description generation with detailed template."""
        generator = MetadataGenerator()
        description = generator.generate_description(
            title="Epic Song",
            genre="edm",
            style_prompt="electronic dance music",
            lyrics="Dance all night",
            template="detailed"
        )
        assert "Epic Song" in description
        assert "edm" in description.lower()
        assert "Subscribe" in description  # Detailed template includes CTA
        assert len(description) > 200  # Detailed should be longer

    def test_generate_description_truncates_long_content(self):
        """Test that very long descriptions are truncated."""
        generator = MetadataGenerator()
        # Create very long lyrics
        long_lyrics = "\n".join([f"Line {i}" for i in range(500)])
        description = generator.generate_description(
            title="Long Song",
            genre="pop",
            style_prompt="test",
            lyrics=long_lyrics
        )
        assert len(description) <= 5000  # YouTube limit

    def test_generate_description_filters_structure_tags(self):
        """Test that structure tags are filtered from lyrics preview."""
        generator = MetadataGenerator()
        lyrics = "[Verse 1]\nActual lyrics\n[Chorus]\nMore lyrics\n[Bridge]\nBridge lyrics"
        description = generator.generate_description(
            title="Structured Song",
            genre="pop",
            style_prompt="test",
            lyrics=lyrics
        )
        # Structure tags should not appear in the lyrics preview
        assert "Actual lyrics" in description
        assert "More lyrics" in description
        # But the bracketed tags themselves shouldn't show
        assert description.count("[Verse 1]") <= 1  # May appear in full lyrics section


@pytest.mark.unit
class TestMetadataGeneratorSuggestTitle:
    """Test MetadataGenerator.suggest_title method."""

    def test_suggest_title_without_prefix(self):
        """Test title suggestion without emoji prefix."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="My Song",
            genre="pop",
            include_prefix=False
        )
        assert result == "My Song"

    def test_suggest_title_with_prefix_pop(self):
        """Test title suggestion with pop emoji prefix."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="My Song",
            genre="pop",
            include_prefix=True
        )
        assert result.startswith("🎵")
        assert "My Song" in result

    def test_suggest_title_with_prefix_rock(self):
        """Test title suggestion with rock emoji prefix."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="Rock On",
            genre="rock",
            include_prefix=True
        )
        assert result.startswith("🎸")
        assert "Rock On" in result

    def test_suggest_title_with_prefix_hip_hop(self):
        """Test title suggestion with hip-hop emoji prefix."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="Rap Song",
            genre="hip-hop",
            include_prefix=True
        )
        assert result.startswith("🎤")

    def test_suggest_title_truncates_long_title(self):
        """Test that very long titles are truncated."""
        generator = MetadataGenerator()
        long_title = "A" * 150
        result = generator.suggest_title(
            original_title=long_title,
            genre="pop"
        )
        assert len(result) <= 100  # YouTube limit
        assert result.endswith("...")

    def test_suggest_title_unknown_genre_default_emoji(self):
        """Test that unknown genre gets default emoji."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="My Song",
            genre="unknown",
            include_prefix=True
        )
        assert result.startswith("🎶")


@pytest.mark.unit
class TestMetadataGeneratorGenerateAll:
    """Test MetadataGenerator.generate_all method."""

    def test_generate_all_returns_complete_metadata(self):
        """Test that generate_all returns all metadata fields."""
        generator = MetadataGenerator()
        result = generator.generate_all(
            title="Test Song",
            genre="pop",
            style_prompt="upbeat pop music",
            lyrics="Test lyrics here"
        )
        assert "suggested_title" in result
        assert "tags" in result
        assert "description" in result
        assert isinstance(result["tags"], list)
        assert isinstance(result["description"], str)
        assert isinstance(result["suggested_title"], str)

    def test_generate_all_with_template(self):
        """Test generate_all with custom template."""
        generator = MetadataGenerator()
        result = generator.generate_all(
            title="My Song",
            genre="rock",
            style_prompt="rock music",
            lyrics="Rock lyrics",
            template="minimal"
        )
        # Minimal template should produce shorter description
        assert len(result["description"]) < 1000

    def test_generate_all_consistency(self):
        """Test that all generated fields are consistent."""
        generator = MetadataGenerator()
        result = generator.generate_all(
            title="Consistent Song",
            genre="edm",
            style_prompt="electronic dance music",
            lyrics="Dance lyrics"
        )
        # Title should appear in description
        assert "Consistent Song" in result["description"]
        # Genre should appear in tags
        assert any("edm" in tag.lower() for tag in result["tags"])


@pytest.mark.unit
class TestGetMetadataGenerator:
    """Test get_metadata_generator singleton function."""

    def test_get_metadata_generator_returns_instance(self):
        """Test that get_metadata_generator returns a MetadataGenerator."""
        with patch('app.services.metadata_generator._metadata_generator', None):
            generator = get_metadata_generator()
            assert isinstance(generator, MetadataGenerator)

    def test_get_metadata_generator_singleton(self):
        """Test that get_metadata_generator returns the same instance."""
        with patch('app.services.metadata_generator._metadata_generator', None):
            generator1 = get_metadata_generator()
            generator2 = get_metadata_generator()
            assert generator1 is generator2


@pytest.mark.unit
class TestMetadataGeneratorEdgeCases:
    """Test edge cases and error handling."""

    def test_generate_tags_empty_inputs(self):
        """Test tag generation with empty inputs."""
        generator = MetadataGenerator()
        tags = generator.generate_tags(title="", genre="", style_prompt="")
        assert isinstance(tags, list)
        assert len(tags) > 0  # Should still have AI tags

    def test_generate_description_empty_lyrics(self):
        """Test description generation with empty lyrics."""
        generator = MetadataGenerator()
        description = generator.generate_description(
            title="No Lyrics",
            genre="instrumental",
            style_prompt="instrumental music",
            lyrics=""
        )
        assert "No Lyrics" in description
        assert len(description) > 0

    def test_generate_description_only_structure_tags(self):
        """Test description with only structure tags in lyrics."""
        generator = MetadataGenerator()
        lyrics = "[Verse 1]\n[Chorus]\n[Bridge]\n[Outro]"
        description = generator.generate_description(
            title="Structured",
            genre="pop",
            style_prompt="test",
            lyrics=lyrics
        )
        assert "Structured" in description

    def test_suggest_title_empty_title(self):
        """Test title suggestion with empty title."""
        generator = MetadataGenerator()
        result = generator.suggest_title(
            original_title="",
            genre="pop"
        )
        assert result == ""

    def test_clean_for_tag_numbers_only(self):
        """Test cleaning text with only numbers."""
        generator = MetadataGenerator()
        result = generator._clean_for_tag("123 456")
        assert result == "123456"

    def test_generate_all_empty_style_prompt(self):
        """Test generate_all with empty style prompt."""
        generator = MetadataGenerator()
        result = generator.generate_all(
            title="Simple Song",
            genre="pop",
            style_prompt="",
            lyrics="Simple lyrics"
        )
        assert result["suggested_title"] == "Simple Song"
        assert len(result["tags"]) > 0
        assert len(result["description"]) > 0
