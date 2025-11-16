#!/usr/bin/env python3
"""
Add metadata files to existing songs
Generates UUIDs and .meta.json files for all songs without metadata
"""

import json
import re
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.core.uuid_generator import UUIDGenerator
from tools.core.logging_config import setup_logging

class MetadataGenerator:
    """Generate metadata files for existing songs"""

    GENRES = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']
    TRIUMPH_KEYWORDS = ['triumph', 'victory', 'hustle', 'grind', 'elevation', 'champion',
                         'unstoppable', 'rise', 'conquer']

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.songs_dir = base_dir / 'generated' / 'songs'
        self.uuid_gen = UUIDGenerator()
        self.processed = 0
        self.errors = 0

        # Load existing UUIDs if any
        self.load_existing_uuids()

    def load_existing_uuids(self):
        """Load existing UUIDs from metadata files"""
        for genre in self.GENRES:
            genre_dir = self.songs_dir / genre
            if not genre_dir.exists():
                continue

            for meta_file in genre_dir.glob('*.meta.json'):
                try:
                    with open(meta_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'id' in data:
                            self.uuid_gen.existing_ids.add(data['id'])
                except Exception as e:
                    print(f"Warning: Could not load {meta_file}: {e}")

    def extract_metadata_from_file(self, filepath: Path) -> dict:
        """Extract metadata from markdown file"""
        metadata = {
            'id': self.uuid_gen.generate(),
            'title': '',
            'genre': filepath.parent.name,
            'file_path': str(filepath.relative_to(self.base_dir / 'generated')),
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat(),
            'collections': []
        }

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return None

        # Extract title from first line
        if lines and lines[0].startswith('#'):
            metadata['title'] = lines[0].replace('#', '').strip()
        else:
            # Fallback: use filename
            metadata['title'] = filepath.stem.replace('-', ' ').title()

        # Extract theme/mood from first 30 lines
        themes = []
        for line in lines[:30]:
            # Look for Genre, Theme, Mood, etc.
            if 'Genre' in line and '**' in line:
                match = re.search(r'\*\*Genre\*\*:\s*(.+)', line)
                if match:
                    metadata['genre_detail'] = match.group(1).strip()

            elif 'Theme' in line and '**' in line:
                match = re.search(r'\*\*Theme\*\*:\s*(.+)', line)
                if match:
                    themes.extend([t.strip() for t in match.group(1).split(',')])

            elif 'Mood' in line and '**' in line:
                match = re.search(r'\*\*Mood\*\*:\s*(.+)', line)
                if match:
                    metadata['mood'] = match.group(1).strip()

        if themes:
            metadata['themes'] = themes

        # Extract personas from content
        personas = set()
        persona_patterns = ['PHOENIX', 'NEON', 'REBEL']
        for pattern in persona_patterns:
            if pattern in content:
                personas.add(pattern)

        if personas:
            metadata['personas'] = sorted(list(personas))

        # Check if it's a Triumph Collection song
        title_lower = metadata['title'].lower()
        content_lower = content.lower()

        is_triumph = any(keyword in title_lower or keyword in content_lower
                        for keyword in self.TRIUMPH_KEYWORDS)

        if is_triumph or '⭐' in content:
            metadata['collections'] = ['triumph-collection']

        # Extract style prompt if available
        if '## Style Prompt' in content:
            start = content.find('## Style Prompt')
            end = content.find('\n##', start + 1)
            if end == -1:
                end = len(content)

            style_section = content[start:end]
            # Remove markdown code blocks
            style_text = re.sub(r'```[^`]*```', '', style_section)
            metadata['style_prompt_length'] = len(style_text.strip())

        # Extract lyrics length
        if '## Lyrics' in content:
            start = content.find('## Lyrics')
            end = content.find('\n##', start + 1)
            if end == -1:
                end = len(content)

            lyrics_section = content[start:end]
            lyrics_text = re.sub(r'```[^`]*```', '', lyrics_section)
            metadata['lyrics_length'] = len(lyrics_text.strip())

        return metadata

    def process_all_songs(self):
        """Process all songs and generate metadata files"""
        print("\n🎵 Generating Metadata Files for Existing Songs")
        print("=" * 60)

        total_songs = 0

        for genre in self.GENRES:
            genre_dir = self.songs_dir / genre
            if not genre_dir.exists():
                continue

            print(f"\nProcessing {genre}...")
            genre_count = 0

            for md_file in sorted(genre_dir.glob('*.md')):
                # Check if metadata already exists
                meta_file = md_file.with_suffix('.meta.json')

                if meta_file.exists():
                    print(f"  ⏭️  Skipping {md_file.name} (metadata exists)")
                    continue

                # Extract metadata
                metadata = self.extract_metadata_from_file(md_file)

                if metadata:
                    # Save metadata file
                    try:
                        with open(meta_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2)

                        print(f"  ✓ Created {meta_file.name}")
                        self.processed += 1
                        genre_count += 1
                        total_songs += 1
                    except Exception as e:
                        print(f"  ❌ Error saving {meta_file}: {e}")
                        self.errors += 1
                else:
                    print(f"  ❌ Failed to extract metadata from {md_file.name}")
                    self.errors += 1

            if genre_count > 0:
                print(f"  Generated {genre_count} metadata files for {genre}")

        print("\n" + "=" * 60)
        print(f"✅ Processing Complete!")
        print(f"  Total files processed: {self.processed}")
        print(f"  Total songs: {total_songs}")
        if self.errors > 0:
            print(f"  ⚠️  Errors: {self.errors}")

        return self.processed, self.errors

def main():
    """Main entry point"""
    base_dir = Path(__file__).parent.parent.parent

    # Setup logging
    setup_logging(base_dir / 'logs')

    print("\n" + "="* 60)
    print("METADATA GENERATOR FOR EXISTING SONGS")
    print("=" * 60)
    print(f"Base directory: {base_dir}")
    print(f"Songs directory: {base_dir / 'generated' / 'songs'}")

    generator = MetadataGenerator(base_dir)
    processed, errors = generator.process_all_songs()

    if errors == 0:
        print("\n✅ All songs processed successfully!")
        return 0
    else:
        print(f"\n⚠️  Completed with {errors} errors")
        return 1

if __name__ == '__main__':
    sys.exit(main())
