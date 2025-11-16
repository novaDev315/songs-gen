#!/usr/bin/env python3
"""
Songs Generation System - Interactive CLI Menu
Main entry point for all tools and workflows
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
import logging

# Setup logging
from tools.core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


class MenuSystem:
    """Interactive menu system for Songs Generation tools"""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.running = True
        self.menu_stack = []  # For breadcrumb navigation

    def clear_screen(self):
        """Cross-platform screen clear"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title: str):
        """Display styled header"""
        self.clear_screen()
        print("═" * 70)
        print(f"  {title}")
        print("═" * 70)
        print()

    def display_breadcrumb(self):
        """Display navigation breadcrumb"""
        if self.menu_stack:
            breadcrumb = " > ".join(self.menu_stack)
            print(f"📍 {breadcrumb}\n")

    def get_choice(self, options: List[str], allow_back: bool = True) -> Optional[str]:
        """
        Get user choice from options

        Args:
            options: List of valid option keys
            allow_back: Whether to allow 'B' for back

        Returns:
            User's choice (uppercase) or None if invalid
        """
        while True:
            if allow_back and self.menu_stack:
                print("\n[B] Back")
            print("[Q] Quit\n")

            choice = input("Enter your choice: ").strip().upper()

            if choice == 'Q':
                if self.confirm_quit():
                    sys.exit(0)
                continue

            if choice == 'B' and allow_back and self.menu_stack:
                return 'BACK'

            if choice in options:
                return choice

            print(f"\n❌ Invalid choice '{choice}'. Please try again.")
            input("\nPress Enter to continue...")
            self.display_header(self.menu_stack[-1] if self.menu_stack else "Main Menu")
            if self.menu_stack:
                self.display_breadcrumb()

    def confirm_quit(self) -> bool:
        """Confirm user wants to quit"""
        response = input("\nAre you sure you want to quit? (y/n): ").strip().lower()
        return response == 'y'

    def main_menu(self):
        """Display and handle main menu"""
        self.menu_stack = ["Main Menu"]

        while self.running:
            self.display_header("🎵 Songs Generation System - Main Menu")

            print("🎵 SONG CREATION")
            print("  [1] Create New Song (Interactive Wizard)")
            print("  [2] Browse Templates")
            print()
            print("📚 SONG MANAGEMENT")
            print("  [3] Browse Generated Songs")
            print("  [4] Search Songs")
            print("  [5] Check for Duplicates")
            print()
            print("✅ VALIDATION & QUALITY")
            print("  [6] Validate All Songs")
            print("  [7] Validate Specific Song")
            print()
            print("📖 DOCUMENTATION")
            print("  [8] Quick Start Guide")
            print("  [9] Troubleshooting")
            print()
            print("📊 ABOUT")
            print("  [10] View Statistics")

            choice = self.get_choice(
                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                allow_back=False
            )

            if choice == '1':
                self.song_creation_wizard()
            elif choice == '2':
                self.template_browser()
            elif choice == '3':
                self.browse_songs()
            elif choice == '4':
                self.search_songs()
            elif choice == '5':
                self.check_duplicates()
            elif choice == '6':
                self.validate_all()
            elif choice == '7':
                self.validate_song()
            elif choice == '8':
                self.show_quickstart()
            elif choice == '9':
                self.troubleshooting()
            elif choice == '10':
                self.statistics()

    def song_creation_wizard(self):
        """Interactive song creation wizard"""
        from tools.core.song_creator import SongCreationWizard

        self.menu_stack.append("Create New Song")
        self.display_header("🎵 Song Creation Wizard")
        self.display_breadcrumb()

        print("Welcome to the Song Creation Wizard!")
        print("This interactive tool will guide you through creating a new song.\n")

        try:
            wizard = SongCreationWizard(self.base_dir)
            wizard.run()
        except Exception as e:
            logger.error(f"Error in song creation wizard: {e}")
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to return to menu...")

        self.menu_stack.pop()

    def check_duplicates(self):
        """Check for duplicate songs"""
        self.menu_stack.append("Duplicate Checker")
        self.display_header("🔍 Duplicate Song Checker")
        self.display_breadcrumb()

        print("Enter song title to check (or press Enter to scan all):")
        title = input("> ").strip()

        try:
            from tools.management.duplicate_checker import DuplicateChecker
            checker = DuplicateChecker(self.base_dir / "generated")

            if title:
                results = checker.check_title(title)
                if results:
                    print(f"\n⚠️  Found {len(results)} potential duplicates:")
                    for i, result in enumerate(results, 1):
                        similarity = result.get('similarity', 0)
                        print(f"{i}. {result.get('file', 'unknown')} - Similarity: {similarity:.1%}")
                else:
                    print("\n✅ No duplicates found. Title is unique!")
            else:
                print("\n🔍 Scanning all songs for duplicates...")
                duplicates = checker.scan_all()

                if duplicates:
                    print(f"\n⚠️  Found {len(duplicates)} duplicate groups:")
                    for group in duplicates:
                        print(f"\nGroup: {group.get('title', 'Unknown')}")
                        for file in group.get('files', []):
                            print(f"  - {file}")
                else:
                    print("\n✅ No duplicates found across all songs!")

        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            print(f"\n❌ Error: {e}")

        input("\nPress Enter to return to menu...")
        self.menu_stack.pop()

    def validate_all(self):
        """Validate all songs"""
        self.menu_stack.append("Validate All Songs")
        self.display_header("✅ Song Validation")
        self.display_breadcrumb()

        print("🔍 Validating all songs...\n")

        try:
            from tools.validation.validator import validate_all_songs

            results = validate_all_songs(self.base_dir)

            print(f"📊 Validation Results:")
            print(f"   Total songs: {results['total']}")
            print(f"   ✅ Valid: {results['valid']}")
            print(f"   ❌ Errors: {results['errors']}")
            print(f"   ⚠️  Warnings: {results['warnings']}")

            if results['details']:
                print(f"\n📋 Issues Found:")
                for detail in results['details'][:10]:  # Show first 10
                    print(f"\n  {detail['file']}:")
                    for error in detail.get('errors', []):
                        print(f"    ❌ {error}")
                    for warning in detail.get('warnings', []):
                        print(f"    ⚠️  {warning}")

                if len(results['details']) > 10:
                    print(f"\n  ... and {len(results['details']) - 10} more files with issues")

        except Exception as e:
            logger.error(f"Error validating songs: {e}")
            print(f"\n❌ Error: {e}")

        input("\nPress Enter to return to menu...")
        self.menu_stack.pop()

    def browse_songs(self):
        """Browse generated songs by genre"""
        self.menu_stack.append("Browse Songs")

        while True:
            self.display_header("📚 Browse Generated Songs")
            self.display_breadcrumb()

            print("Select Genre:")
            print("  [1] Hip-Hop       [2] Pop            [3] EDM")
            print("  [4] Rock          [5] Country        [6] R&B")
            print("  [7] Jazz          [8] Fusion         [9] All Genres")

            choice = self.get_choice(['1', '2', '3', '4', '5', '6', '7', '8', '9'])

            if choice == 'BACK':
                break

            genre_map = {
                '1': 'hip-hop', '2': 'pop', '3': 'edm', '4': 'rock',
                '5': 'country', '6': 'r-b', '7': 'jazz', '8': 'fusion'
            }

            genre = genre_map.get(choice, 'all')
            self.display_genre_songs(genre)

        self.menu_stack.pop()

    def display_genre_songs(self, genre: str):
        """Display songs for a specific genre"""
        self.display_header(f"Songs: {genre.title() if genre != 'all' else 'All Genres'}")

        songs_dir = self.base_dir / "generated" / "songs"

        if genre == 'all':
            pattern = "**/*.md"
        else:
            pattern = f"{genre}/**/*.md"

        songs = list(songs_dir.glob(pattern)) if songs_dir.exists() else []

        if not songs:
            print(f"No songs found for genre: {genre}")
        else:
            print(f"\nFound {len(songs)} songs:\n")
            for i, song in enumerate(songs[:20], 1):  # Show first 20
                print(f"{i:2d}. {song.stem}")

            if len(songs) > 20:
                print(f"\n... and {len(songs) - 20} more")

        input("\nPress Enter to continue...")

    def show_quickstart(self):
        """Display quick start guide"""
        self.menu_stack.append("Quick Start")
        self.display_header("📖 Quick Start Guide")
        self.display_breadcrumb()

        quickstart = self.base_dir / "docs" / "QUICKSTART.md"

        if quickstart.exists():
            try:
                with open(quickstart, 'r') as f:
                    lines = f.readlines()[:30]
                    print(''.join(lines))
                    total_lines = len(open(quickstart).readlines())
                    print(f"\n... (showing first 30 lines of {total_lines} total)")
            except Exception as e:
                print(f"❌ Error reading quick start guide: {e}")
        else:
            print("❌ Quick start guide not found at docs/QUICKSTART.md")

        print(f"\nFull guide: {quickstart}")
        input("\nPress Enter to return to menu...")
        self.menu_stack.pop()

    # Placeholder methods
    def template_browser(self): self._placeholder("Template Browser")
    def search_songs(self): self._placeholder("Search Songs")
    def validate_song(self): self._placeholder("Validate Specific Song")
    def troubleshooting(self): self._placeholder("Troubleshooting")
    def statistics(self): self._placeholder("Statistics")

    def _placeholder(self, feature_name: str):
        """Placeholder for features to be implemented"""
        self.menu_stack.append(feature_name)
        self.display_header(feature_name)
        self.display_breadcrumb()

        print(f"🚧 {feature_name} - Coming Soon!\n")
        print("This feature will be implemented in a future update.")

        input("\nPress Enter to return to menu...")
        self.menu_stack.pop()


def main():
    """Main entry point"""
    try:
        menu = MenuSystem()
        menu.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.exception("Fatal error in menu system")
        print(f"\n❌ Fatal Error: {e}")
        print("Check logs/ directory for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
