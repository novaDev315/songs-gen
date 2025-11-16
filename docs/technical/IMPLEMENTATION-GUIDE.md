# Song Generation System - Implementation Guide

## Quick Start Implementation

This guide provides ready-to-use code and scripts for implementing the new architecture.

---

## Phase 1: Quick Wins Implementation (Day 1)

### 1.1 Documentation Reorganization Script

```bash
#!/bin/bash
# reorganize-docs.sh
# Run from generated/ directory

echo "Reorganizing documentation structure..."

# Create new documentation hierarchy
mkdir -p docs/{user-guide,technical,reference,archive}

# Move existing documentation files
if [ -f "SONG-CREATION-WORKFLOW.md" ]; then
    mv SONG-CREATION-WORKFLOW.md docs/user-guide/workflow.md
fi

if [ -f "QUICK-REFERENCE.md" ]; then
    mv QUICK-REFERENCE.md docs/user-guide/quick-reference.md
fi

if [ -f "VERIFICATION-REPORT.md" ]; then
    mv VERIFICATION-REPORT.md docs/archive/verification-report-v1.md
fi

if [ -f "COMPLETE-COLLECTION.md" ]; then
    mv COMPLETE-COLLECTION.md docs/reference/triumph-collection.md
fi

# Create navigation README
cat > docs/README.md << 'EOF'
# Documentation Index

## User Guides
- [Creation Workflow](user-guide/workflow.md) - Step-by-step song creation
- [Quick Reference](user-guide/quick-reference.md) - Cheat sheet for common tasks
- [Search Guide](user-guide/search-guide.md) - Finding songs efficiently

## Technical Documentation
- [Architecture](technical/architecture.md) - System design and decisions
- [Migration Guide](technical/migration-guide.md) - Upgrading to new structure
- [Automation](technical/automation.md) - Scripts and tools

## Reference
- [Triumph Collection](reference/triumph-collection.md) - Main 45-song collection
- [Metadata Schema](reference/metadata-schema.md) - JSON schema documentation
- [File Formats](reference/file-formats.md) - Markdown and metadata formats

## Archive
- [Version 1 Documentation](archive/) - Historical documentation
EOF

echo "Documentation reorganization complete!"
```

### 1.2 Enhanced Duplicate Checker

```python
#!/usr/bin/env python3
# enhanced-duplicate-checker.py

import os
import re
import json
from difflib import SequenceMatcher
from pathlib import Path

class DuplicateChecker:
    def __init__(self, base_dir="generated"):
        self.base_dir = Path(base_dir)
        self.songs = []
        self.load_songs()

    def load_songs(self):
        """Load all song files and extract titles"""
        for md_file in self.base_dir.rglob("*.md"):
            if md_file.parent.name in ['docs', 'archive']:
                continue

            with open(md_file, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    title = first_line.replace('#', '').strip()
                    self.songs.append({
                        'title': title,
                        'path': str(md_file),
                        'genre': md_file.parent.name
                    })

    def check_duplicate(self, title, threshold=0.8):
        """Check for duplicate or similar titles"""
        duplicates = []
        similar = []

        for song in self.songs:
            # Exact match
            if song['title'].lower() == title.lower():
                duplicates.append(song)
            else:
                # Similarity check
                ratio = SequenceMatcher(None, title.lower(), song['title'].lower()).ratio()
                if ratio >= threshold:
                    similar.append({**song, 'similarity': ratio})

        return duplicates, sorted(similar, key=lambda x: x['similarity'], reverse=True)

    def interactive_check(self):
        """Interactive duplicate checking"""
        print("\n🎵 Enhanced Duplicate Checker")
        print("=" * 40)

        while True:
            title = input("\nEnter song title to check (or 'quit'): ").strip()
            if title.lower() == 'quit':
                break

            duplicates, similar = self.check_duplicate(title)

            if duplicates:
                print(f"\n❌ EXACT DUPLICATES FOUND:")
                for dup in duplicates:
                    print(f"   - {dup['title']} ({dup['genre']}) - {dup['path']}")

            if similar:
                print(f"\n⚠️  SIMILAR TITLES FOUND:")
                for sim in similar[:5]:  # Show top 5
                    print(f"   - {sim['title']} ({sim['genre']}) - {sim['similarity']:.0%} match")

            if not duplicates and not similar:
                print(f"\n✅ No duplicates found for '{title}'")

            print("\nOptions:")
            print("1. Check another title")
            print("2. View all songs in a genre")
            print("3. Exit")

            choice = input("Choose option (1-3): ")
            if choice == "2":
                self.show_genre_songs()
            elif choice == "3":
                break

    def show_genre_songs(self):
        """Display all songs in a genre"""
        genres = set(song['genre'] for song in self.songs)
        print("\nAvailable genres:", ', '.join(genres))
        genre = input("Enter genre: ").strip().lower()

        genre_songs = [s for s in self.songs if s['genre'] == genre]
        if genre_songs:
            print(f"\n{genre.upper()} Songs ({len(genre_songs)}):")
            for song in sorted(genre_songs, key=lambda x: x['title']):
                print(f"   - {song['title']}")
        else:
            print(f"No songs found in {genre}")

if __name__ == "__main__":
    checker = DuplicateChecker()
    checker.interactive_check()
```

### 1.3 Collection View Generator

```python
#!/usr/bin/env python3
# generate-collection-views.py

import os
import re
from pathlib import Path
from datetime import datetime

class CollectionViewGenerator:
    def __init__(self, base_dir="generated"):
        self.base_dir = Path(base_dir)
        self.triumph_songs = []
        self.additional_songs = []
        self.load_index()

    def load_index(self):
        """Parse existing ALL-SONGS-INDEX.md"""
        index_file = self.base_dir / "ALL-SONGS-INDEX.md"
        if not index_file.exists():
            print("Index file not found!")
            return

        with open(index_file, 'r') as f:
            content = f.read()

        # Extract songs with ⭐ (Triumph Collection)
        triumph_pattern = r'`([^`]+\.md)` ⭐ - (.+)'
        for match in re.finditer(triumph_pattern, content):
            self.triumph_songs.append({
                'file': match.group(1),
                'description': match.group(2)
            })

        # Extract additional songs
        additional_pattern = r'`([^`]+\.md)` - \[Check file for details\]'
        for match in re.finditer(additional_pattern, content):
            self.additional_songs.append({'file': match.group(1)})

    def generate_triumph_view(self):
        """Generate Triumph Collection dedicated view"""
        output = []
        output.append("# Triumph & Hustle Collection ⭐")
        output.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(self.triumph_songs)}\n")
        output.append("---\n")

        # Group by genre
        genres = {}
        for song in self.triumph_songs:
            genre = song['file'].split('/')[0]
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(song)

        # Output by genre
        for genre in sorted(genres.keys()):
            output.append(f"## {genre.upper()} ({len(genres[genre])} songs)\n")
            for i, song in enumerate(genres[genre], 1):
                output.append(f"{i}. `{song['file']}` - {song['description']}")
            output.append("")

        # Stats section
        output.append("## Collection Statistics\n")
        output.append("| Genre | Count | Percentage |")
        output.append("|-------|-------|------------|")
        total = len(self.triumph_songs)
        for genre in sorted(genres.keys()):
            count = len(genres[genre])
            pct = (count / total) * 100
            output.append(f"| {genre} | {count} | {pct:.1f}% |")

        # Save file
        output_file = self.base_dir / "TRIUMPH-COLLECTION.md"
        with open(output_file, 'w') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")

    def generate_standalone_view(self):
        """Generate view for non-collection songs"""
        output = []
        output.append("# Standalone Songs (Non-Collection)")
        output.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(self.additional_songs)}\n")
        output.append("---\n")

        # Group by genre
        genres = {}
        for song in self.additional_songs:
            genre = song['file'].split('/')[0]
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(song)

        # Output by genre
        for genre in sorted(genres.keys()):
            output.append(f"## {genre.upper()} ({len(genres[genre])} songs)\n")
            for i, song in enumerate(genres[genre], 1):
                # Extract title from filename
                title = song['file'].split('/')[-1].replace('.md', '')
                title = '-'.join(title.split('-')[1:])  # Remove number prefix
                title = title.replace('-', ' ').title()
                output.append(f"{i}. `{song['file']}` - {title}")
            output.append("")

        # Save file
        output_file = self.base_dir / "STANDALONE-SONGS.md"
        with open(output_file, 'w') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")

if __name__ == "__main__":
    generator = CollectionViewGenerator()
    generator.generate_triumph_view()
    generator.generate_standalone_view()
```

---

## Phase 2: Metadata System Implementation (Days 2-3)

### 2.1 Metadata Extractor

```python
#!/usr/bin/env python3
# extract-metadata.py

import os
import re
import json
from pathlib import Path
from datetime import datetime

class MetadataExtractor:
    def __init__(self, base_dir="generated"):
        self.base_dir = Path(base_dir)
        self.metadata_pattern = {
            'title': r'^#\s+(.+)$',
            'genre': r'\*\*Genre\*\*:\s*(.+)',
            'theme': r'\*\*Theme\*\*:\s*(.+)',
            'personas': r'\*\*Personas\*\*:\s*(.+)',
            'bpm': r'\*\*BPM\*\*:\s*(\d+)',
            'key': r'\*\*Key\*\*:\s*(.+)',
        }

    def extract_from_file(self, filepath):
        """Extract metadata from markdown file"""
        metadata = {
            'id': self.generate_id(filepath),
            'file_path': str(filepath),
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Extract metadata using patterns
        for line in lines[:20]:  # Check first 20 lines
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

        # Extract style prompt and lyrics lengths
        if "## Style Prompt" in content:
            style_start = content.index("## Style Prompt")
            style_end = content.index("## Lyrics", style_start)
            style_content = content[style_start:style_end]
            metadata['style_prompt_length'] = len(style_content.strip())

        if "## Lyrics" in content:
            lyrics_start = content.index("## Lyrics")
            lyrics_end = content.index("## Why This Works", lyrics_start) if "## Why This Works" in content else len(content)
            lyrics_content = content[lyrics_start:lyrics_end]
            metadata['lyrics_length'] = len(lyrics_content.strip())

        # Determine collection membership
        if '⭐' in str(filepath) or self.is_triumph_collection(metadata.get('title', '')):
            metadata['collections'] = ['triumph-collection']
        else:
            metadata['collections'] = []

        return metadata

    def generate_id(self, filepath):
        """Generate 8-character ID from filename"""
        import hashlib
        hash_obj = hashlib.md5(str(filepath).encode())
        return hash_obj.hexdigest()[:8]

    def is_triumph_collection(self, title):
        """Check if song is part of Triumph Collection"""
        # This would check against a known list
        triumph_titles = [
            "No Looking Back", "Empire State", "Forever", "Overtime",
            "Hustle Hard", "Money Motivated", "Grind Never Stops", "Bag Chaser"
            # Add all 45 titles
        ]
        return title in triumph_titles

    def process_all_songs(self):
        """Extract metadata for all songs"""
        all_metadata = {}

        for md_file in self.base_dir.rglob("*.md"):
            # Skip non-song files
            if md_file.parent.name in ['docs', 'archive']:
                continue
            if md_file.name in ['README.md', 'ALL-SONGS-INDEX.md']:
                continue

            print(f"Processing: {md_file}")
            metadata = self.extract_from_file(md_file)

            # Save individual metadata file
            meta_file = md_file.with_suffix('.meta.json')
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            all_metadata[str(md_file)] = metadata

        # Save master index
        index_file = self.base_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(all_metadata, f, indent=2)

        print(f"\n✓ Processed {len(all_metadata)} songs")
        print(f"✓ Generated metadata files")
        print(f"✓ Created master index: {index_file}")

if __name__ == "__main__":
    extractor = MetadataExtractor()
    extractor.process_all_songs()
```

### 2.2 Index Generator

```python
#!/usr/bin/env python3
# generate-indexes.py

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class IndexGenerator:
    def __init__(self, base_dir="generated"):
        self.base_dir = Path(base_dir)
        self.master_index = {}
        self.load_master_index()

    def load_master_index(self):
        """Load master index.json"""
        index_file = self.base_dir / "index.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                self.master_index = json.load(f)
        else:
            print("Master index not found. Run extract-metadata.py first.")

    def generate_all_songs_index(self):
        """Generate comprehensive ALL-SONGS.md"""
        output = []
        output.append("# Complete Song Index")
        output.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(self.master_index)}")
        output.append("\n---\n")

        # Group by genre
        genres = defaultdict(list)
        for path, metadata in self.master_index.items():
            genre = metadata.get('genre', 'unknown')
            genres[genre].append(metadata)

        # Output each genre
        for genre in sorted(genres.keys()):
            songs = genres[genre]
            output.append(f"## {genre.upper()} ({len(songs)} songs)\n")

            # Sort by title
            songs.sort(key=lambda x: x.get('title', ''))

            for i, song in enumerate(songs, 1):
                collections = song.get('collections', [])
                collection_mark = " ⭐" if 'triumph-collection' in collections else ""

                output.append(f"{i}. **{song.get('title', 'Unknown')}**{collection_mark}")
                output.append(f"   - File: `{song.get('file_path', '')}`")
                output.append(f"   - Theme: {', '.join(song.get('theme', []))}")
                output.append(f"   - BPM: {song.get('bpm', 'N/A')} | Key: {song.get('key', 'N/A')}")

                if song.get('personas'):
                    output.append(f"   - Personas: {', '.join(song.get('personas', []))}")
                output.append("")

        # Statistics section
        output.append("## Statistics\n")
        output.append("| Metric | Value |")
        output.append("|--------|-------|")
        output.append(f"| Total Songs | {len(self.master_index)} |")
        output.append(f"| Genres | {len(genres)} |")

        triumph_count = sum(1 for m in self.master_index.values() if 'triumph-collection' in m.get('collections', []))
        output.append(f"| Triumph Collection | {triumph_count} |")
        output.append(f"| Standalone | {len(self.master_index) - triumph_count} |")

        # Save file
        output_file = self.base_dir / "indexes" / "ALL-SONGS.md"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")

    def generate_theme_index(self):
        """Generate THEMES.md index"""
        output = []
        output.append("# Songs by Theme")
        output.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append("\n---\n")

        # Collect all themes
        themes = defaultdict(list)
        for metadata in self.master_index.values():
            for theme in metadata.get('theme', []):
                themes[theme].append(metadata)

        # Sort by popularity
        sorted_themes = sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)

        for theme, songs in sorted_themes[:20]:  # Top 20 themes
            output.append(f"## {theme.title()} ({len(songs)} songs)\n")

            for song in sorted(songs, key=lambda x: x.get('title', ''))[:10]:  # Show first 10
                output.append(f"- **{song.get('title', 'Unknown')}** ({song.get('genre', 'unknown')})")

            if len(songs) > 10:
                output.append(f"- ... and {len(songs) - 10} more")
            output.append("")

        # Save file
        output_file = self.base_dir / "indexes" / "THEMES.md"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")

    def generate_all_indexes(self):
        """Generate all index views"""
        self.generate_all_songs_index()
        self.generate_theme_index()
        # Add more generators as needed

if __name__ == "__main__":
    generator = IndexGenerator()
    generator.generate_all_indexes()
```

### 2.3 Song Creation Wizard

```python
#!/usr/bin/env python3
# create-song.py

import os
import json
import uuid
from pathlib import Path
from datetime import datetime

class SongCreationWizard:
    def __init__(self, base_dir="generated"):
        self.base_dir = Path(base_dir)
        self.genres = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']
        self.collections = ['triumph-collection', 'standalone']

    def generate_id(self):
        """Generate 8-character unique ID"""
        return str(uuid.uuid4()).replace('-', '')[:8]

    def create_slug(self, title):
        """Create URL-safe slug from title"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug

    def run(self):
        """Interactive song creation"""
        print("\n🎵 Song Creation Wizard")
        print("=" * 40)

        # Gather information
        title = input("Song title: ").strip()
        if not title:
            print("Title is required!")
            return

        # Check for duplicates
        from enhanced_duplicate_checker import DuplicateChecker
        checker = DuplicateChecker(self.base_dir)
        duplicates, similar = checker.check_duplicate(title)

        if duplicates:
            print("\n❌ Duplicate song exists!")
            for dup in duplicates:
                print(f"   {dup['path']}")
            return

        if similar:
            print("\n⚠️  Similar songs found:")
            for sim in similar[:3]:
                print(f"   {sim['title']} ({sim['similarity']:.0%} match)")

            proceed = input("\nContinue anyway? (y/n): ")
            if proceed.lower() != 'y':
                return

        # Select genre
        print("\nGenres:")
        for i, genre in enumerate(self.genres, 1):
            print(f"  {i}. {genre}")

        genre_idx = int(input("Select genre (1-8): ")) - 1
        genre = self.genres[genre_idx]

        # Select collection
        print("\nCollection:")
        print("  1. Triumph Collection ⭐")
        print("  2. Standalone")

        collection_idx = int(input("Select collection (1-2): ")) - 1
        collection = self.collections[collection_idx] if collection_idx == 0 else None

        # Theme
        themes = input("Themes (comma-separated): ").strip()
        theme_list = [t.strip() for t in themes.split(',') if t.strip()]

        # Personas
        personas = input("Personas (comma-separated, optional): ").strip()
        persona_list = [p.strip() for p in personas.split(',') if p.strip()]

        # Musical details
        bpm = input("BPM (optional, e.g., 140): ").strip()
        key = input("Key (optional, e.g., minor): ").strip()

        # Generate IDs and paths
        song_id = self.generate_id()
        slug = self.create_slug(title)
        filename = f"{song_id}-{slug}.md"

        # Determine path
        if collection == 'triumph-collection':
            song_dir = self.base_dir / 'songs' / genre / 'collection' / 'triumph'
        else:
            song_dir = self.base_dir / 'songs' / genre / 'standalone'

        song_dir.mkdir(parents=True, exist_ok=True)
        song_path = song_dir / filename

        # Create metadata
        metadata = {
            'id': song_id,
            'title': title,
            'slug': slug,
            'genre': genre,
            'collections': [collection] if collection else [],
            'theme': theme_list,
            'personas': persona_list,
            'bpm': int(bpm) if bpm else None,
            'key': key if key else None,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

        # Save metadata
        meta_path = song_dir / f"{song_id}-{slug}.meta.json"
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Create song template
        template = self.generate_template(metadata)
        with open(song_path, 'w') as f:
            f.write(template)

        print(f"\n✅ Song created successfully!")
        print(f"   File: {song_path}")
        print(f"   Metadata: {meta_path}")
        print(f"\n📝 Next step: Edit {song_path} to add style prompt and lyrics")

    def generate_template(self, metadata):
        """Generate markdown template for new song"""
        template = []
        template.append(f"# {metadata['title']}")
        template.append("")
        template.append(f"**Genre**: {metadata['genre'].title()}")
        template.append(f"**Theme**: {', '.join(metadata['theme'])}")

        if metadata['personas']:
            template.append(f"**Personas**: {', '.join(metadata['personas'])}")

        if metadata['bpm']:
            template.append(f"**BPM**: {metadata['bpm']}")

        if metadata['key']:
            template.append(f"**Key**: {metadata['key']}")

        template.append("\n---\n")
        template.append("## Style Prompt")
        template.append("```")
        template.append("[Add style prompt here - 200-1000 characters]")
        template.append("```\n")
        template.append("## Lyrics")
        template.append("```")
        template.append("[Add formatted lyrics here - 3000-5000 characters]")
        template.append("```\n")
        template.append("## Why This Works")
        template.append("[Explain the creative choices]\n")
        template.append("## Generation Tips")
        template.append("- Generate 6+ variations")
        template.append("- [Add specific tips]")

        return '\n'.join(template)

if __name__ == "__main__":
    wizard = SongCreationWizard()
    wizard.run()
```

---

## Phase 3: Migration Execution (Days 4-5)

### 3.1 Complete Migration Script

```python
#!/usr/bin/env python3
# migrate-to-v2.py

import os
import re
import json
import shutil
import uuid
from pathlib import Path
from datetime import datetime

class SongMigrationV2:
    def __init__(self, source_dir="generated", target_dir="generated-v2"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.migration_log = []
        self.mapping = {}

        # Known Triumph Collection songs (from index)
        self.triumph_songs = [
            "No Looking Back", "Empire State", "Forever", "Overtime",
            "Hustle Hard", "Money Motivated", "Grind Never Stops", "Bag Chaser",
            "Unstoppable", "Dream Big", "On Fire", "Shine",
            "Champion Heart", "Higher Ground",
            # Add all 45 songs
        ]

    def run_migration(self):
        """Execute complete migration"""
        print("🚀 Starting Migration to V2 Structure")
        print("=" * 50)

        # Pre-flight checks
        if not self.pre_flight_check():
            return False

        # Create backup
        self.create_backup()

        # Setup new structure
        self.setup_new_structure()

        # Migrate songs
        self.migrate_all_songs()

        # Generate indexes
        self.generate_indexes()

        # Validate migration
        if self.validate_migration():
            print("\n✅ Migration completed successfully!")
            self.generate_report()
            return True
        else:
            print("\n❌ Migration validation failed!")
            return False

    def pre_flight_check(self):
        """Validate source directory"""
        if not self.source_dir.exists():
            print(f"❌ Source directory not found: {self.source_dir}")
            return False

        # Count songs
        song_count = len(list(self.source_dir.rglob("*.md")))
        print(f"✓ Found {song_count} markdown files")

        # Check if target exists
        if self.target_dir.exists():
            response = input(f"\n⚠️  Target directory exists: {self.target_dir}\n   Overwrite? (y/n): ")
            if response.lower() != 'y':
                return False
            shutil.rmtree(self.target_dir)

        return True

    def create_backup(self):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = Path(f"backup-{timestamp}.tar.gz")

        print(f"\n📦 Creating backup: {backup_path}")
        os.system(f"tar -czf {backup_path} {self.source_dir}")
        print(f"✓ Backup created: {backup_path}")

    def setup_new_structure(self):
        """Create V2 directory structure"""
        print("\n📁 Creating new directory structure...")

        # Create main directories
        dirs = [
            self.target_dir / "docs" / "user-guide",
            self.target_dir / "docs" / "technical",
            self.target_dir / "docs" / "reference",
            self.target_dir / "docs" / "archive",
            self.target_dir / "collections" / "triumph-collection",
            self.target_dir / "indexes",
            self.target_dir / "tools",
            self.target_dir / ".metadata",
        ]

        # Create genre directories
        genres = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']
        for genre in genres:
            dirs.append(self.target_dir / "songs" / genre / "collection" / "triumph")
            dirs.append(self.target_dir / "songs" / genre / "standalone")

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"✓ Created {len(dirs)} directories")

    def migrate_all_songs(self):
        """Migrate all song files with new naming"""
        print("\n📝 Migrating songs...")

        migrated = 0
        for source_file in self.source_dir.rglob("*.md"):
            # Skip non-song files
            if source_file.parent.name in ['docs', 'archive']:
                continue
            if source_file.name in ['README.md', 'ALL-SONGS-INDEX.md',
                                    'SONG-CREATION-WORKFLOW.md', 'QUICK-REFERENCE.md']:
                continue

            # Migrate song
            if self.migrate_song(source_file):
                migrated += 1

        print(f"✓ Migrated {migrated} songs")

    def migrate_song(self, source_file):
        """Migrate individual song file"""
        # Extract metadata
        metadata = self.extract_metadata(source_file)

        # Generate new ID and filename
        new_id = str(uuid.uuid4()).replace('-', '')[:8]
        slug = self.create_slug(metadata['title'])
        new_filename = f"{new_id}-{slug}.md"

        # Determine target location
        genre = source_file.parent.name
        is_triumph = metadata['title'] in self.triumph_songs

        if is_triumph:
            target_dir = self.target_dir / "songs" / genre / "collection" / "triumph"
        else:
            target_dir = self.target_dir / "songs" / genre / "standalone"

        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / new_filename

        # Copy file
        shutil.copy2(source_file, target_file)

        # Create metadata file
        metadata['id'] = new_id
        metadata['slug'] = slug
        metadata['original_path'] = str(source_file)
        metadata['collections'] = ['triumph-collection'] if is_triumph else []

        meta_file = target_dir / f"{new_id}-{slug}.meta.json"
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Log migration
        self.mapping[str(source_file)] = str(target_file)
        self.migration_log.append({
            'source': str(source_file),
            'target': str(target_file),
            'metadata': metadata
        })

        return True

    def extract_metadata(self, filepath):
        """Extract metadata from markdown file"""
        metadata = {
            'title': '',
            'genre': filepath.parent.name,
            'created': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }

        with open(filepath, 'r') as f:
            lines = f.readlines()

        # Extract title
        for line in lines[:5]:
            if line.startswith('#'):
                metadata['title'] = line.replace('#', '').strip()
                break

        # Extract other metadata
        for line in lines[:20]:
            if '**Genre**:' in line:
                metadata['genre_detail'] = line.split(':')[1].strip()
            elif '**Theme**:' in line:
                themes = line.split(':')[1].strip()
                metadata['theme'] = [t.strip() for t in themes.split(',')]
            elif '**BPM**:' in line:
                bpm = re.search(r'\d+', line)
                if bpm:
                    metadata['bpm'] = int(bpm.group())

        return metadata

    def create_slug(self, title):
        """Create URL-safe slug"""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        return slug[:50]  # Limit length

    def generate_indexes(self):
        """Generate all index files"""
        print("\n📊 Generating indexes...")

        # Create master index
        master_index = {}
        for log_entry in self.migration_log:
            master_index[log_entry['target']] = log_entry['metadata']

        index_file = self.target_dir / "indexes" / "index.json"
        with open(index_file, 'w') as f:
            json.dump(master_index, f, indent=2)

        print(f"✓ Generated master index: {index_file}")

        # Generate markdown indexes
        self.generate_markdown_indexes(master_index)

    def generate_markdown_indexes(self, master_index):
        """Generate human-readable markdown indexes"""
        # ALL-SONGS.md
        self.generate_all_songs_md(master_index)

        # COLLECTIONS.md
        self.generate_collections_md(master_index)

        # GENRES.md
        self.generate_genres_md(master_index)

    def generate_all_songs_md(self, master_index):
        """Generate complete song listing"""
        output = []
        output.append("# All Songs - V2 Structure")
        output.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(master_index)}\n")

        # Group by genre
        from collections import defaultdict
        genres = defaultdict(list)

        for path, metadata in master_index.items():
            genre = metadata.get('genre', 'unknown')
            genres[genre].append((path, metadata))

        for genre in sorted(genres.keys()):
            output.append(f"\n## {genre.upper()}")
            for path, metadata in sorted(genres[genre], key=lambda x: x[1].get('title', '')):
                collections = metadata.get('collections', [])
                mark = " ⭐" if collections else ""
                output.append(f"- {metadata.get('title', 'Unknown')}{mark}")

        # Save
        output_file = self.target_dir / "indexes" / "ALL-SONGS.md"
        with open(output_file, 'w') as f:
            f.write('\n'.join(output))

    def validate_migration(self):
        """Validate migration completeness"""
        print("\n🔍 Validating migration...")

        # Check file counts
        source_count = len([f for f in self.source_dir.rglob("*.md")
                           if f.name not in ['README.md', 'ALL-SONGS-INDEX.md']])
        target_count = len(list((self.target_dir / "songs").rglob("*.md")))

        print(f"  Source files: {source_count}")
        print(f"  Target files: {target_count}")

        if source_count != target_count:
            print(f"  ❌ File count mismatch!")
            return False

        # Check metadata files
        meta_count = len(list((self.target_dir / "songs").rglob("*.meta.json")))
        print(f"  Metadata files: {meta_count}")

        if meta_count != target_count:
            print(f"  ❌ Missing metadata files!")
            return False

        print("  ✓ All validations passed")
        return True

    def generate_report(self):
        """Generate migration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'source_dir': str(self.source_dir),
            'target_dir': str(self.target_dir),
            'files_migrated': len(self.migration_log),
            'mapping': self.mapping,
            'summary': {
                'total_songs': len(self.migration_log),
                'triumph_collection': sum(1 for l in self.migration_log
                                         if 'triumph-collection' in l['metadata'].get('collections', [])),
                'standalone': sum(1 for l in self.migration_log
                                 if not l['metadata'].get('collections', []))
            }
        }

        report_file = self.target_dir / "MIGRATION-REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Migration report: {report_file}")

if __name__ == "__main__":
    migrator = SongMigrationV2()
    migrator.run_migration()
```

### 3.2 Post-Migration Validation

```bash
#!/bin/bash
# validate-migration.sh

echo "Post-Migration Validation"
echo "========================="

TARGET_DIR="generated-v2"

# 1. Check directory structure
echo "Checking directory structure..."
required_dirs=(
    "$TARGET_DIR/songs"
    "$TARGET_DIR/collections"
    "$TARGET_DIR/indexes"
    "$TARGET_DIR/tools"
    "$TARGET_DIR/docs"
)

for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ❌ $dir missing!"
        exit 1
    fi
done

# 2. Check file counts
echo ""
echo "Checking file counts..."
song_count=$(find $TARGET_DIR/songs -name "*.md" | wc -l)
meta_count=$(find $TARGET_DIR/songs -name "*.meta.json" | wc -l)

echo "  Songs: $song_count"
echo "  Metadata: $meta_count"

if [ "$song_count" -eq "$meta_count" ]; then
    echo "  ✓ File counts match"
else
    echo "  ❌ File count mismatch!"
    exit 1
fi

# 3. Check indexes
echo ""
echo "Checking indexes..."
if [ -f "$TARGET_DIR/indexes/index.json" ]; then
    echo "  ✓ Master index exists"
else
    echo "  ❌ Master index missing!"
fi

# 4. Validate JSON files
echo ""
echo "Validating JSON files..."
for json_file in $(find $TARGET_DIR -name "*.json"); do
    if python3 -m json.tool "$json_file" > /dev/null 2>&1; then
        echo "  ✓ Valid: $(basename $json_file)"
    else
        echo "  ❌ Invalid JSON: $json_file"
        exit 1
    fi
done

echo ""
echo "✅ All validation checks passed!"
```

---

## Quick Implementation Checklist

### Day 1: Quick Wins
- [ ] Run `reorganize-docs.sh` to restructure documentation
- [ ] Deploy `enhanced-duplicate-checker.py` for better duplicate detection
- [ ] Run `generate-collection-views.py` to create collection-specific views
- [ ] Test new tools with team

### Day 2-3: Metadata System
- [ ] Run `extract-metadata.py` to generate metadata for all songs
- [ ] Deploy `generate-indexes.py` to create automated indexes
- [ ] Test `create-song.py` wizard for new song creation
- [ ] Validate metadata completeness

### Day 4-5: Migration
- [ ] Create full backup of current system
- [ ] Run `migrate-to-v2.py` for complete migration
- [ ] Execute `validate-migration.sh` to verify success
- [ ] Update documentation with new structure
- [ ] Train users on new system

### Post-Migration
- [ ] Monitor for issues
- [ ] Gather user feedback
- [ ] Fine-tune automation scripts
- [ ] Document lessons learned

---

## Support & Troubleshooting

### Common Issues

**Issue**: Migration script fails midway
```bash
# Solution: Resume from backup
tar -xzf backup-[timestamp].tar.gz
# Fix issue and retry
```

**Issue**: Metadata extraction incomplete
```python
# Solution: Manually edit .meta.json files
# Or re-run extraction for specific files
python3 extract-metadata.py --file path/to/song.md
```

**Issue**: Index generation fails
```bash
# Solution: Validate JSON files first
find generated -name "*.meta.json" -exec python3 -m json.tool {} \; > /dev/null
```

### Rollback Procedure

```bash
#!/bin/bash
# rollback.sh

echo "Rolling back to previous version..."

# 1. Remove new structure
rm -rf generated-v2

# 2. Restore from backup
latest_backup=$(ls -t backup-*.tar.gz | head -1)
tar -xzf "$latest_backup"

echo "✓ Rollback complete"
```

---

This implementation guide provides all the code and scripts needed to transform your song generation system into a scalable, maintainable architecture. Start with Phase 1 for immediate improvements, then proceed through the metadata and migration phases as time permits.