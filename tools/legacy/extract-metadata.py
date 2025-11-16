#!/usr/bin/env python3
# extract-metadata.py
# Extract metadata from all song files for better searchability

import os
import re
import json
from pathlib import Path
from datetime import datetime
import hashlib

class MetadataExtractor:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.metadata_pattern = {
            'title': r'^#\s+(.+)$',
            'genre': r'\*\*Genre\*\*:\s*(.+)',
            'theme': r'\*\*Theme\*\*:\s*(.+)',
            'personas': r'\*\*Personas\*\*:\s*(.+)',
            'bpm': r'\*\*BPM\*\*:\s*(\d+)',
            'key': r'\*\*Key\*\*:\s*(.+)',
        }
        self.genres = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']

    def extract_from_file(self, filepath):
        """Extract metadata from markdown file"""
        metadata = {
            'id': self.generate_id(filepath),
            'file_path': str(filepath.relative_to(self.base_dir)),
            'filename': filepath.name,
            'genre_folder': filepath.parent.name,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return None

        # Extract metadata using patterns
        for line in lines[:25]:  # Check first 25 lines for metadata
            for key, pattern in self.metadata_pattern.items():
                match = re.match(pattern, line)
                if match:
                    value = match.group(1).strip()

                    if key == 'personas':
                        # Split personas into list
                        metadata[key] = [p.strip() for p in value.split(',')]
                    elif key == 'theme':
                        # Split themes
                        metadata[key] = [t.strip().lower() for t in value.split(',')]
                    elif key == 'bpm':
                        metadata[key] = int(value)
                    else:
                        metadata[key] = value

        # Count style prompt and lyrics lengths
        if "## Style Prompt" in content:
            style_start = content.find("## Style Prompt")
            style_end = content.find("\n##", style_start + 1)
            if style_end == -1:
                style_end = len(content)

            style_content = content[style_start:style_end]
            # Remove markdown code blocks
            style_text = re.sub(r'```[^`]*```', '', style_content)
            metadata['style_prompt_length'] = len(style_text.strip())

        if "## Lyrics" in content:
            lyrics_start = content.find("## Lyrics")
            lyrics_end = content.find("\n##", lyrics_start + 1)
            if lyrics_end == -1:
                lyrics_end = len(content)

            lyrics_content = content[lyrics_start:lyrics_end]
            # Remove markdown code blocks
            lyrics_text = re.sub(r'```[^`]*```', '', lyrics_content)
            metadata['lyrics_length'] = len(lyrics_text.strip())

            # Count lyrics lines
            lyrics_lines = [l for l in lyrics_text.split('\n') if l.strip() and not l.strip().startswith('#')]
            metadata['lyrics_lines'] = len(lyrics_lines)

        # Determine collection membership from filename or content
        if '⭐' in filepath.read_text(encoding='utf-8'):
            metadata['collections'] = ['triumph-collection']
        else:
            # Check ALL-SONGS-INDEX.md
            metadata['collections'] = []

        return metadata

    def generate_id(self, filepath):
        """Generate 8-character ID from filename"""
        hash_obj = hashlib.md5(str(filepath).encode())
        return hash_obj.hexdigest()[:8]

    def process_all_songs(self, save_individual=False):
        """Extract metadata for all songs"""
        all_metadata = {}
        processed_count = 0

        print("\n📊 Extracting Metadata from Song Files")
        print("=" * 50)

        for genre in self.genres:
            genre_dir = self.base_dir / genre
            if not genre_dir.exists():
                continue

            print(f"\nProcessing {genre}...")

            for md_file in genre_dir.glob("*.md"):
                metadata = self.extract_from_file(md_file)

                if metadata:
                    all_metadata[metadata['file_path']] = metadata
                    processed_count += 1

                    # Optionally save individual metadata files
                    if save_individual:
                        meta_file = md_file.with_suffix('.meta.json')
                        with open(meta_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, indent=2)

                    # Show progress
                    if processed_count % 10 == 0:
                        print(f"  Processed {processed_count} songs...")

        # Save master index
        index_file = self.base_dir / "songs-metadata.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(all_metadata, f, indent=2)

        print(f"\n✅ Processed {processed_count} songs")
        print(f"✓ Created master index: {index_file}")

        # Generate summary
        self.generate_summary(all_metadata)

        return all_metadata

    def generate_summary(self, metadata_dict):
        """Generate metadata summary report"""
        print("\n📈 Metadata Summary")
        print("=" * 50)

        # Total counts
        print(f"Total songs: {len(metadata_dict)}")

        # By genre
        from collections import Counter
        genres = Counter(m.get('genre_folder', 'unknown') for m in metadata_dict.values())
        print(f"\nBy Genre:")
        for genre, count in sorted(genres.items()):
            print(f"  - {genre:10s}: {count:3d} songs")

        # By collection
        triumph_count = sum(1 for m in metadata_dict.values()
                           if 'triumph-collection' in m.get('collections', []))
        print(f"\nBy Collection:")
        print(f"  - Triumph Collection: {triumph_count} songs")
        print(f"  - Standalone: {len(metadata_dict) - triumph_count} songs")

        # Songs with personas
        persona_count = sum(1 for m in metadata_dict.values() if m.get('personas'))
        print(f"\nWith Personas: {persona_count} songs")

        # Average lengths
        avg_style = sum(m.get('style_prompt_length', 0) for m in metadata_dict.values()) / len(metadata_dict)
        avg_lyrics = sum(m.get('lyrics_length', 0) for m in metadata_dict.values()) / len(metadata_dict)

        print(f"\nAverage Lengths:")
        print(f"  - Style Prompt: {avg_style:.0f} characters")
        print(f"  - Lyrics: {avg_lyrics:.0f} characters")

        # Most common themes
        all_themes = []
        for m in metadata_dict.values():
            all_themes.extend(m.get('theme', []))

        theme_counts = Counter(all_themes)
        print(f"\nTop 5 Themes:")
        for theme, count in theme_counts.most_common(5):
            print(f"  - {theme:20s}: {count:3d} songs")

    def search_metadata(self, query, metadata_dict=None):
        """Search metadata by query"""
        if metadata_dict is None:
            # Load from file
            index_file = self.base_dir / "songs-metadata.json"
            if not index_file.exists():
                print("❌ Metadata index not found. Run extract-metadata.py first.")
                return []

            with open(index_file, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)

        results = []
        query_lower = query.lower()

        for path, metadata in metadata_dict.items():
            # Search in title
            if query_lower in metadata.get('title', '').lower():
                results.append((metadata, 'title'))
                continue

            # Search in themes
            themes = metadata.get('theme', [])
            if any(query_lower in theme for theme in themes):
                results.append((metadata, 'theme'))
                continue

            # Search in personas
            personas = metadata.get('personas', [])
            if any(query_lower in persona.lower() for persona in personas):
                results.append((metadata, 'persona'))
                continue

        return results

if __name__ == "__main__":
    import sys

    extractor = MetadataExtractor()

    if len(sys.argv) > 1 and sys.argv[1] == 'search':
        # Search mode
        if len(sys.argv) < 3:
            print("Usage: python3 extract-metadata.py search [query]")
            sys.exit(1)

        query = ' '.join(sys.argv[2:])
        results = extractor.search_metadata(query)

        if results:
            print(f"\n🔍 Search Results for '{query}':")
            print("=" * 50)
            for metadata, match_type in results:
                print(f"\n• {metadata.get('title', 'Unknown')}")
                print(f"  File: {metadata.get('file_path', '')}")
                print(f"  Genre: {metadata.get('genre_folder', '')}")
                print(f"  Match: {match_type}")
                if match_type == 'theme':
                    print(f"  Themes: {', '.join(metadata.get('theme', []))}")
                elif match_type == 'persona':
                    print(f"  Personas: {', '.join(metadata.get('personas', []))}")
        else:
            print(f"\n❌ No results found for '{query}'")
    else:
        # Extract mode
        save_individual = '--individual' in sys.argv
        extractor.process_all_songs(save_individual=save_individual)

        print("\n💡 Usage:")
        print("  python3 extract-metadata.py                    # Extract all metadata")
        print("  python3 extract-metadata.py --individual       # Also save individual .meta.json files")
        print("  python3 extract-metadata.py search [query]     # Search metadata")
