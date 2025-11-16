#!/usr/bin/env python3
# enhanced-duplicate-checker.py
# Enhanced duplicate detection with similarity matching

import os
import re
from difflib import SequenceMatcher
from pathlib import Path

class DuplicateChecker:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.songs = []
        self.load_songs()

    def load_songs(self):
        """Load all song files and extract titles"""
        genres = ['hip-hop', 'pop', 'edm', 'rock', 'country', 'r-b', 'jazz', 'fusion']

        for genre in genres:
            genre_dir = self.base_dir / genre
            if not genre_dir.exists():
                continue

            for md_file in genre_dir.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#'):
                            title = first_line.replace('#', '').strip()
                            self.songs.append({
                                'title': title,
                                'path': str(md_file.relative_to(self.base_dir)),
                                'genre': genre,
                                'filename': md_file.name
                            })
                except Exception as e:
                    print(f"Warning: Could not read {md_file}: {e}")

    def check_duplicate(self, title, threshold=0.8):
        """Check for duplicate or similar titles"""
        duplicates = []
        similar = []

        for song in self.songs:
            # Exact match (case-insensitive)
            if song['title'].lower() == title.lower():
                duplicates.append(song)
            else:
                # Similarity check
                ratio = SequenceMatcher(None, title.lower(), song['title'].lower()).ratio()
                if ratio >= threshold:
                    similar.append({**song, 'similarity': ratio})

        return duplicates, sorted(similar, key=lambda x: x['similarity'], reverse=True)

    def check_by_title(self, title):
        """Check for duplicates and print results"""
        duplicates, similar = self.check_duplicate(title)

        if duplicates:
            print(f"\n❌ EXACT DUPLICATES FOUND:")
            for dup in duplicates:
                print(f"   - {dup['title']}")
                print(f"     Genre: {dup['genre']}")
                print(f"     File: {dup['path']}")
            return True

        if similar:
            print(f"\n⚠️  SIMILAR TITLES FOUND:")
            for sim in similar[:5]:  # Show top 5
                print(f"   - {sim['title']} ({sim['genre']})")
                print(f"     Similarity: {sim['similarity']:.0%}")
                print(f"     File: {sim['path']}")
            return True

        print(f"\n✅ No duplicates found for '{title}'")
        return False

    def list_genre_songs(self, genre):
        """Display all songs in a genre"""
        genre_songs = [s for s in self.songs if s['genre'] == genre]

        if not genre_songs:
            print(f"\nNo songs found in {genre}")
            return

        print(f"\n{genre.upper()} Songs ({len(genre_songs)}):")
        for song in sorted(genre_songs, key=lambda x: x['filename']):
            print(f"   - {song['filename']:40s} | {song['title']}")

    def show_stats(self):
        """Show statistics about all songs"""
        print("\n📊 Song Statistics:")
        print(f"   Total songs: {len(self.songs)}")

        # By genre
        from collections import Counter
        genre_counts = Counter(s['genre'] for s in self.songs)

        print("\n   By Genre:")
        for genre, count in sorted(genre_counts.items()):
            print(f"   - {genre:10s}: {count:3d} songs")

    def interactive_check(self):
        """Interactive duplicate checking"""
        print("\n🎵 Enhanced Duplicate Checker")
        print("=" * 50)
        print(f"Loaded {len(self.songs)} songs")
        print("\nCommands:")
        print("  check [title]  - Check for duplicates")
        print("  list [genre]   - List all songs in genre")
        print("  stats          - Show statistics")
        print("  quit           - Exit")
        print("=" * 50)

        while True:
            try:
                cmd = input("\n> ").strip()

                if not cmd:
                    continue

                if cmd.lower() in ['quit', 'exit', 'q']:
                    break

                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()

                if action == 'check' and len(parts) > 1:
                    self.check_by_title(parts[1])
                elif action == 'list' and len(parts) > 1:
                    self.list_genre_songs(parts[1].lower())
                elif action == 'stats':
                    self.show_stats()
                else:
                    print("Unknown command. Try: check [title], list [genre], stats, or quit")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    import sys

    checker = DuplicateChecker()

    if len(sys.argv) > 1:
        # Command-line mode
        action = sys.argv[1].lower()

        if action == 'check' and len(sys.argv) > 2:
            title = ' '.join(sys.argv[2:])
            checker.check_by_title(title)
        elif action == 'list' and len(sys.argv) > 2:
            checker.list_genre_songs(sys.argv[2].lower())
        elif action == 'stats':
            checker.show_stats()
        else:
            print("Usage:")
            print("  python3 enhanced-duplicate-checker.py check [title]")
            print("  python3 enhanced-duplicate-checker.py list [genre]")
            print("  python3 enhanced-duplicate-checker.py stats")
            print("  python3 enhanced-duplicate-checker.py        (interactive mode)")
    else:
        # Interactive mode
        checker.interactive_check()
