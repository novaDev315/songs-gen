#!/usr/bin/env python3
# generate-collection-views.py
# Generate separate views for Triumph Collection and Standalone songs

import os
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class CollectionViewGenerator:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.triumph_songs = []
        self.standalone_songs = []
        self.load_from_index()

    def load_from_index(self):
        """Parse existing ALL-SONGS-INDEX.md"""
        index_file = self.base_dir / "ALL-SONGS-INDEX.md"

        if not index_file.exists():
            print("❌ ALL-SONGS-INDEX.md not found!")
            return

        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        current_genre = None

        # Parse line by line
        for line in content.split('\n'):
            # Detect genre headers
            genre_match = re.match(r'###\s+(.+?)\s+\((\d+)\s+songs?\)', line)
            if genre_match:
                current_genre = genre_match.group(1).split('/')[0].strip().lower()
                continue

            # Extract Triumph Collection songs (with ⭐)
            triumph_match = re.search(r'`([^`]+\.md)`\s+⭐\s+-\s+(.+)', line)
            if triumph_match and current_genre:
                self.triumph_songs.append({
                    'file': triumph_match.group(1),
                    'description': triumph_match.group(2).strip(),
                    'genre': current_genre
                })
                continue

            # Extract standalone songs
            standalone_match = re.search(r'-\s+`([^`]+\.md)`\s+-\s+\[Check file for details\]', line)
            if standalone_match and current_genre:
                file_path = standalone_match.group(1)
                # Extract title from filename
                filename = file_path.split('/')[-1].replace('.md', '')
                # Remove number prefix
                title_parts = filename.split('-', 1)
                if len(title_parts) > 1:
                    title = title_parts[1].replace('-', ' ').title()
                else:
                    title = filename.replace('-', ' ').title()

                self.standalone_songs.append({
                    'file': file_path,
                    'title': title,
                    'genre': current_genre
                })

        print(f"✓ Loaded {len(self.triumph_songs)} Triumph Collection songs")
        print(f"✓ Loaded {len(self.standalone_songs)} standalone songs")

    def generate_triumph_view(self):
        """Generate Triumph Collection dedicated view"""
        if not self.triumph_songs:
            print("⚠️  No Triumph Collection songs found")
            return None

        output = []
        output.append("# Triumph & Hustle Collection ⭐")
        output.append("")
        output.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(self.triumph_songs)}")
        output.append(f"**Theme**: Victory, hustle, grind, elevation, success")
        output.append("")
        output.append("---")
        output.append("")
        output.append("## About This Collection")
        output.append("")
        output.append("The **Triumph & Hustle Collection** is a curated set of 45 songs across")
        output.append("7 genres, all focused on themes of success, perseverance, and achievement.")
        output.append("")
        output.append("All songs in this collection feature multi-singer configurations and")
        output.append("are optimized for Suno AI's music generation platform.")
        output.append("")
        output.append("---")
        output.append("")

        # Group by genre
        genres = defaultdict(list)
        for song in self.triumph_songs:
            genres[song['genre']].append(song)

        # Output by genre
        for genre in sorted(genres.keys()):
            songs = genres[genre]
            output.append(f"## {genre.upper().replace('R-B', 'R&B')} ({len(songs)} songs)")
            output.append("")

            for i, song in enumerate(songs, 1):
                output.append(f"{i}. **`{song['file']}`**")
                output.append(f"   - {song['description']}")
                output.append("")

        # Stats section
        output.append("---")
        output.append("")
        output.append("## Collection Statistics")
        output.append("")
        output.append("| Genre | Count | Percentage |")
        output.append("|-------|-------|------------|")

        total = len(self.triumph_songs)
        for genre in sorted(genres.keys()):
            count = len(genres[genre])
            pct = (count / total) * 100
            genre_display = genre.upper().replace('R-B', 'R&B')
            output.append(f"| {genre_display} | {count} | {pct:.1f}% |")

        output.append("")
        output.append("---")
        output.append("")
        output.append("## Usage")
        output.append("")
        output.append("To use these songs:")
        output.append("1. Navigate to the song file")
        output.append("2. Copy the **Style Prompt** to Suno AI's 'Style of Music' field")
        output.append("3. Copy the **Lyrics** to Suno AI's 'Lyrics' field")
        output.append("4. Generate 6+ variations for best results")
        output.append("")
        output.append("---")
        output.append("")
        output.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
        output.append("")

        # Save file
        output_file = self.base_dir / "TRIUMPH-COLLECTION.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")
        return output_file

    def generate_standalone_view(self):
        """Generate view for non-collection songs"""
        if not self.standalone_songs:
            print("⚠️  No standalone songs found")
            return None

        output = []
        output.append("# Standalone Songs (Non-Collection)")
        output.append("")
        output.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        output.append(f"**Total Songs**: {len(self.standalone_songs)}")
        output.append("")
        output.append("---")
        output.append("")
        output.append("## About These Songs")
        output.append("")
        output.append("These are songs created outside of the Triumph Collection. They cover")
        output.append("a variety of themes and styles, experimenting with different approaches")
        output.append("to multi-singer configurations and genre-specific techniques.")
        output.append("")
        output.append("---")
        output.append("")

        # Group by genre
        genres = defaultdict(list)
        for song in self.standalone_songs:
            genres[song['genre']].append(song)

        # Output by genre
        for genre in sorted(genres.keys()):
            songs = genres[genre]
            output.append(f"## {genre.upper().replace('R-B', 'R&B')} ({len(songs)} songs)")
            output.append("")

            for i, song in enumerate(sorted(songs, key=lambda x: x['file']), 1):
                output.append(f"{i}. **{song['title']}**")
                output.append(f"   - File: `{song['file']}`")
                output.append("")

        # Stats section
        output.append("---")
        output.append("")
        output.append("## Genre Distribution")
        output.append("")
        output.append("| Genre | Count |")
        output.append("|-------|-------|")

        for genre in sorted(genres.keys()):
            count = len(genres[genre])
            genre_display = genre.upper().replace('R-B', 'R&B')
            output.append(f"| {genre_display} | {count} |")

        output.append("")
        output.append("---")
        output.append("")
        output.append(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*")
        output.append("")

        # Save file
        output_file = self.base_dir / "STANDALONE-SONGS.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output))

        print(f"✓ Generated: {output_file}")
        return output_file

    def generate_all_views(self):
        """Generate both collection views"""
        print("\n🎵 Generating Collection Views")
        print("=" * 50)

        triumph_file = self.generate_triumph_view()
        standalone_file = self.generate_standalone_view()

        print("")
        print("✅ Collection views generated successfully!")
        if triumph_file:
            print(f"   - {triumph_file}")
        if standalone_file:
            print(f"   - {standalone_file}")

if __name__ == "__main__":
    generator = CollectionViewGenerator()
    generator.generate_all_views()
