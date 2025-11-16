"""
Interactive song creation wizard
Guides users through creating new songs step by step
"""

from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class SongCreationWizard:
    """Step-by-step interactive song creator"""

    GENRES = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']

    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent
        self.base_dir = base_dir
        self.song_data = {}

    def run(self):
        """Run the complete wizard"""
        print("Let's create your song! I'll guide you through each step.\n")

        # Step 1: Genre
        if not self.select_genre():
            return

        # Step 2: Title
        if not self.enter_title():
            return

        # Step 3: Theme/Mood
        if not self.enter_theme():
            return

        # Step 4: Personas (if applicable)
        if not self.select_personas():
            return

        # Step 5: Generate outputs
        self.generate_outputs()

        # Step 6: Save
        if not self.save_song():
            return

        print("\n✅ Song created successfully!")
        print(f"📁 Location: {self.song_data['filepath']}")
        print(f"\n💡 Next steps:")
        print("  1. Review the generated content")
        print("  2. Copy style prompt and lyrics to Suno AI")
        print("  3. Generate 6+ variations")

    def select_genre(self) -> bool:
        """Select genre"""
        print("STEP 1: Select Genre")
        print("-" * 50)

        for i, genre in enumerate(self.GENRES, 1):
            print(f"  [{i}] {genre.title()}")

        while True:
            choice = input("\nSelect genre (1-8) or 'Q' to quit: ").strip()

            if choice.upper() == 'Q':
                return False

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.GENRES):
                    self.song_data['genre'] = self.GENRES[idx]
                    print(f"✓ Genre: {self.song_data['genre'].title()}\n")
                    return True
            except ValueError:
                pass

            print("Invalid choice. Please try again.")

    def enter_title(self) -> bool:
        """Enter song title"""
        print("STEP 2: Song Title")
        print("-" * 50)

        while True:
            title = input("Enter song title (or 'Q' to quit): ").strip()

            if title.upper() == 'Q':
                return False

            if self.validate_title(title):
                self.song_data['title'] = title
                print(f"✓ Title: {title}\n")
                return True

            print("❌ Invalid title. Please use 2-100 characters, no special symbols.")

    def validate_title(self, title: str) -> bool:
        """Validate song title"""
        if not title or len(title) < 2 or len(title) > 100:
            return False

        # Check for filesystem-unsafe characters
        unsafe = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(c in title for c in unsafe):
            return False

        return True

    def enter_theme(self) -> bool:
        """Enter theme and mood"""
        print("STEP 3: Theme & Mood")
        print("-" * 50)

        theme = input("What's the song about? (e.g., 'love', 'success', 'heartbreak'): ").strip()
        if theme.upper() == 'Q':
            return False

        mood = input("What's the mood? (e.g., 'upbeat', 'melancholic', 'aggressive'): ").strip()
        if mood.upper() == 'Q':
            return False

        self.song_data['theme'] = theme
        self.song_data['mood'] = mood

        print(f"✓ Theme: {theme}")
        print(f"✓ Mood: {mood}\n")
        return True

    def select_personas(self) -> bool:
        """Select personas for multi-singer (if applicable)"""
        if self.song_data['genre'] != 'multi-singer':
            self.song_data['personas'] = []
            return True

        print("STEP 4: Select Personas")
        print("-" * 50)
        print("Select personas for your multi-singer song:")
        print("  [1] PHOENIX (powerful female)")
        print("  [2] NEON (smooth male)")
        print("  [3] REBEL (edgy rapper)")
        print("  [4] PHOENIX + NEON")
        print("  [5] PHOENIX + REBEL")
        print("  [6] All Three (PHOENIX + NEON + REBEL)")

        # Simplified for now
        self.song_data['personas'] = ['PHOENIX', 'NEON']
        print("✓ Using PHOENIX + NEON\n")

        return True

    def generate_outputs(self):
        """Generate style prompt and lyrics structure"""
        print("STEP 5: Generating Content")
        print("-" * 50)
        print("⚙️  Generating style prompt and lyrics structure...\n")

        # Generate style prompt
        style_prompt = self.create_style_prompt()
        self.song_data['style_prompt'] = style_prompt

        # Generate lyrics structure
        lyrics_structure = self.create_lyrics_structure()
        self.song_data['lyrics'] = lyrics_structure

        print("✓ Style prompt generated")
        print("✓ Lyrics structure created\n")

    def create_style_prompt(self) -> str:
        """Create style prompt"""
        genre = self.song_data['genre'].title()
        mood = self.song_data['mood']

        # Simple template - would be more sophisticated in production
        prompt = f"{genre}, {mood}, catchy hooks, professional production, 120 BPM"

        if self.song_data.get('personas'):
            persona_desc = ", ".join(f"{p} vocals" for p in self.song_data['personas'][:2])
            prompt += f", {persona_desc}"

        return prompt

    def create_lyrics_structure(self) -> str:
        """Create lyrics structure template"""
        return """[Intro]
(Instrumental or vocal ad-libs)

[Verse 1]
(Write your first verse here - establish the story)

[Pre-Chorus]
(Build tension leading to chorus)

[Chorus]
(Main hook - catchy and memorable)
(Use CAPS for emphasis)

[Verse 2]
(Develop the story further)

[Pre-Chorus]
(Build tension again)

[Chorus]
(Repeat with possible variations)

[Bridge]
(Change perspective or add contrast)

[Final Chorus]
(Most powerful version with ad-libs)

[Outro]
(Fade out or instrumental ending)
"""

    def save_song(self) -> bool:
        """Save song to file"""
        print("STEP 6: Save Song")
        print("-" * 50)

        confirm = input("Save song? (Y/n): ").strip().lower()
        if confirm == 'n':
            return False

        try:
            # Generate UUID for song
            from tools.core.uuid_generator import UUIDGenerator
            uuid_gen = UUIDGenerator()
            song_id = uuid_gen.generate()

            # Create filename
            slug = self.song_data['title'].lower().replace(' ', '-')[:50]
            filename = f"{song_id}-{slug}.md"

            # Create file path - use new structure
            genre_dir = self.base_dir / "generated" / "songs" / self.song_data['genre']
            genre_dir.mkdir(parents=True, exist_ok=True)
            filepath = genre_dir / filename

            # Write markdown file
            content = self.format_song_markdown()
            filepath.write_text(content, encoding='utf-8')

            # Create metadata file
            metadata = self.create_metadata(song_id)
            meta_path = filepath.with_suffix('.meta.json')
            meta_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

            self.song_data['filepath'] = filepath

            print(f"✓ Saved to: {filepath}")
            logger.info(f"Song created: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving song: {e}")
            print(f"❌ Error saving song: {e}")
            return False

    def format_song_markdown(self) -> str:
        """Format song as markdown"""
        return f"""# {self.song_data['title']}

## Song Information
- **Genre**: {self.song_data['genre'].title()}
- **Theme**: {self.song_data['theme']}
- **Mood**: {self.song_data['mood']}

## Style Prompt
```
{self.song_data['style_prompt']}
```

## Lyrics

{self.song_data['lyrics']}

## Notes
- Created with Songs Generation System
- Remember to generate 6+ variations in Suno AI
- Use the 4-7 descriptor rule for style prompts
- Refer to personas/persona-selection-guide.md for multi-singer tips
"""

    def create_metadata(self, song_id: str) -> Dict:
        """Create metadata dict"""
        return {
            "id": song_id,
            "title": self.song_data['title'],
            "genre": self.song_data['genre'],
            "theme": self.song_data['theme'],
            "mood": self.song_data['mood'],
            "personas": self.song_data.get('personas', []),
            "version": "1.0",
            "created_by": "wizard"
        }
