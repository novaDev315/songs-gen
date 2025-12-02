     1→#!/usr/bin/env python3
     2→"""
     3→Songs Generation System - Interactive CLI Menu
     4→Main entry point for all tools and workflows
     5→"""
     6→
     7→import sys
     8→import os
     9→from pathlib import Path
    10→from typing import Optional, List
    11→import logging
    12→
    13→# Setup logging
    14→from tools.core.logging_config import setup_logging
    15→setup_logging()
    16→logger = logging.getLogger(__name__)
    17→
    18→
    19→class MenuSystem:
    20→    """Interactive menu system for Songs Generation tools"""
    21→
    22→    def __init__(self):
    23→        self.base_dir = Path(__file__).parent.parent
    24→        self.running = True
    25→        self.menu_stack = []  # For breadcrumb navigation
    26→
    27→    def clear_screen(self):
    28→        """Cross-platform screen clear"""
    29→        os.system('cls' if os.name == 'nt' else 'clear')
    30→
    31→    def display_header(self, title: str):
    32→        """Display styled header"""
    33→        self.clear_screen()
    34→        print("═" * 70)
    35→        print(f"  {title}")
    36→        print("═" * 70)
    37→        print()
    38→
    39→    def display_breadcrumb(self):
    40→        """Display navigation breadcrumb"""
    41→        if self.menu_stack:
    42→            breadcrumb = " > ".join(self.menu_stack)
    43→            print(f"📍 {breadcrumb}\n")
    44→
    45→    def get_choice(self, options: List[str], allow_back: bool = True) -> Optional[str]:
    46→        """
    47→        Get user choice from options
    48→
    49→        Args:
    50→            options: List of valid option keys
    51→            allow_back: Whether to allow 'B' for back
    52→
    53→        Returns:
    54→            User's choice (uppercase) or None if invalid
    55→        """
    56→        while True:
    57→            if allow_back and self.menu_stack:
    58→                print("\n[B] Back")
    59→            print("[Q] Quit\n")
    60→
    61→            choice = input("Enter your choice: ").strip().upper()
    62→
    63→            if choice == 'Q':
    64→                if self.confirm_quit():
    65→                    sys.exit(0)
    66→                continue
    67→
    68→            if choice == 'B' and allow_back and self.menu_stack:
    69→                return 'BACK'
    70→
    71→            if choice in options:
    72→                return choice
    73→
    74→            print(f"\n❌ Invalid choice '{choice}'. Please try again.")
    75→            input("\nPress Enter to continue...")
    76→            self.display_header(self.menu_stack[-1] if self.menu_stack else "Main Menu")
    77→            if self.menu_stack:
    78→                self.display_breadcrumb()
    79→
    80→    def confirm_quit(self) -> bool:
    81→        """Confirm user wants to quit"""
    82→        response = input("\nAre you sure you want to quit? (y/n): ").strip().lower()
    83→        return response == 'y'
    84→
    85→    def main_menu(self):
    86→        """Display and handle main menu"""
    87→        self.menu_stack = ["Main Menu"]
    88→
    89→        while self.running:
    90→            self.display_header("🎵 Songs Generation System - Main Menu")
    91→
    92→            print("🎵 SONG CREATION")
    93→            print("  [1] Create New Song (Interactive Wizard)")
    94→            print("  [2] Browse Templates")
    95→            print()
    96→            print("📚 SONG MANAGEMENT")
    97→            print("  [3] Browse Generated Songs")
    98→            print("  [4] Search Songs")
    99→            print("  [5] Check for Duplicates")
   100→            print()
   101→            print("✅ VALIDATION & QUALITY")
   102→            print("  [6] Validate All Songs")
   103→            print("  [7] Validate Specific Song")
   104→            print()
   105→            print("📖 DOCUMENTATION")
   106→            print("  [8] Quick Start Guide")
   107→            print("  [9] Troubleshooting")
   108→            print()
   109→            print("📊 ABOUT")
   110→            print("  [10] View Statistics")
   111→
   112→            choice = self.get_choice(
   113→                ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
   114→                allow_back=False
   115→            )
   116→
   117→            if choice == '1':
   118→                self.song_creation_wizard()
   119→            elif choice == '2':
   120→                self.template_browser()
   121→            elif choice == '3':
   122→                self.browse_songs()
   123→            elif choice == '4':
   124→                self.search_songs()
   125→            elif choice == '5':
   126→                self.check_duplicates()
   127→            elif choice == '6':
   128→                self.validate_all()
   129→            elif choice == '7':
   130→                self.validate_song()
   131→            elif choice == '8':
   132→                self.show_quickstart()
   133→            elif choice == '9':
   134→                self.troubleshooting()
   135→            elif choice == '10':
   136→                self.statistics()
   137→
   138→    def song_creation_wizard(self):
   139→        """Interactive song creation wizard"""
   140→        from tools.core.song_creator import SongCreationWizard
   141→
   142→        self.menu_stack.append("Create New Song")
   143→        self.display_header("🎵 Song Creation Wizard")
   144→        self.display_breadcrumb()
   145→
   146→        print("Welcome to the Song Creation Wizard!")
   147→        print("This interactive tool will guide you through creating a new song.\n")
   148→
   149→        try:
   150→            wizard = SongCreationWizard(self.base_dir)
   151→            wizard.run()
   152→        except Exception as e:
   153→            logger.error(f"Error in song creation wizard: {e}")
   154→            print(f"\n❌ Error: {e}")
   155→            input("\nPress Enter to return to menu...")
   156→
   157→        self.menu_stack.pop()
   158→
   159→    def check_duplicates(self):
   160→        """Check for duplicate songs"""
   161→        self.menu_stack.append("Duplicate Checker")
   162→        self.display_header("🔍 Duplicate Song Checker")
   163→        self.display_breadcrumb()
   164→
   165→        print("Enter song title to check (or press Enter to scan all):")
   166→        title = input("> ").strip()
   167→
   168→        try:
   169→            from tools.management.duplicate_checker import DuplicateChecker
   170→            checker = DuplicateChecker(self.base_dir / "generated")
   171→
   172→            if title:
   173→                results = checker.check_title(title)
   174→                if results:
   175→                    print(f"\n⚠️  Found {len(results)} potential duplicates:")
   176→                    for i, result in enumerate(results, 1):
   177→                        similarity = result.get('similarity', 0)
   178→                        print(f"{i}. {result.get('file', 'unknown')} - Similarity: {similarity:.1%}")
   179→                else:
   180→                    print("\n✅ No duplicates found. Title is unique!")
   181→            else:
   182→                print("\n🔍 Scanning all songs for duplicates...")
   183→                duplicates = checker.scan_all()
   184→
   185→                if duplicates:
   186→                    print(f"\n⚠️  Found {len(duplicates)} duplicate groups:")
   187→                    for group in duplicates:
   188→                        print(f"\nGroup: {group.get('title', 'Unknown')}")
   189→                        for file in group.get('files', []):
   190→                            print(f"  - {file}")
   191→                else:
   192→                    print("\n✅ No duplicates found across all songs!")
   193→
   194→        except Exception as e:
   195→            logger.error(f"Error checking duplicates: {e}")
   196→            print(f"\n❌ Error: {e}")
   197→
   198→        input("\nPress Enter to return to menu...")
   199→        self.menu_stack.pop()
   200→
   201→    def validate_all(self):
   202→        """Validate all songs"""
   203→        self.menu_stack.append("Validate All Songs")
   204→        self.display_header("✅ Song Validation")
   205→        self.display_breadcrumb()
   206→
   207→        print("🔍 Validating all songs...\n")
   208→
   209→        try:
   210→            from tools.validation.validator import validate_all_songs
   211→
   212→            results = validate_all_songs(self.base_dir)
   213→
   214→            print(f"📊 Validation Results:")
   215→            print(f"   Total songs: {results['total']}")
   216→            print(f"   ✅ Valid: {results['valid']}")
   217→            print(f"   ❌ Errors: {results['errors']}")
   218→            print(f"   ⚠️  Warnings: {results['warnings']}")
   219→
   220→            if results['details']:
   221→                print(f"\n📋 Issues Found:")
   222→                for detail in results['details'][:10]:  # Show first 10
   223→                    print(f"\n  {detail['file']}:")
   224→                    for error in detail.get('errors', []):
   225→                        print(f"    ❌ {error}")
   226→                    for warning in detail.get('warnings', []):
   227→                        print(f"    ⚠️  {warning}")
   228→
   229→                if len(results['details']) > 10:
   230→                    print(f"\n  ... and {len(results['details']) - 10} more files with issues")
   231→
   232→        except Exception as e:
   233→            logger.error(f"Error validating songs: {e}")
   234→            print(f"\n❌ Error: {e}")
   235→
   236→        input("\nPress Enter to return to menu...")
   237→        self.menu_stack.pop()
   238→
   239→    def browse_songs(self):
   240→        """Browse generated songs by genre"""
   241→        self.menu_stack.append("Browse Songs")
   242→
   243→        while True:
   244→            self.display_header("📚 Browse Generated Songs")
   245→            self.display_breadcrumb()
   246→
   247→            print("Select Genre:")
   248→            print("  [1] Hip-Hop       [2] Pop            [3] EDM")
   249→            print("  [4] Rock          [5] Country        [6] R&B")
   250→            print("  [7] Jazz          [8] Fusion         [9] All Genres")
   251→
   252→            choice = self.get_choice(['1', '2', '3', '4', '5', '6', '7', '8', '9'])
   253→
   254→            if choice == 'BACK':
   255→                break
   256→
   257→            genre_map = {
   258→                '1': 'hip-hop', '2': 'pop', '3': 'edm', '4': 'rock',
   259→                '5': 'country', '6': 'r-b', '7': 'jazz', '8': 'fusion'
   260→            }
   261→
   262→            genre = genre_map.get(choice, 'all')
   263→            self.display_genre_songs(genre)
   264→
   265→        self.menu_stack.pop()
   266→
   267→    def display_genre_songs(self, genre: str):
   268→        """Display songs for a specific genre"""
   269→        self.display_header(f"Songs: {genre.title() if genre != 'all' else 'All Genres'}")
   270→
   271→        songs_dir = self.base_dir / "generated" / "songs"
   272→
   273→        if genre == 'all':
   274→            pattern = "**/*.md"
   275→        else:
   276→            pattern = f"{genre}/**/*.md"
   277→
   278→        songs = list(songs_dir.glob(pattern)) if songs_dir.exists() else []
   279→
   280→        if not songs:
   281→            print(f"No songs found for genre: {genre}")
   282→        else:
   283→            print(f"\nFound {len(songs)} songs:\n")
   284→            for i, song in enumerate(songs[:20], 1):  # Show first 20
   285→                print(f"{i:2d}. {song.stem}")
   286→
   287→            if len(songs) > 20:
   288→                print(f"\n... and {len(songs) - 20} more")
   289→
   290→        input("\nPress Enter to continue...")
   291→
   292→    def show_quickstart(self):
   293→        """Display quick start guide"""
   294→        self.menu_stack.append("Quick Start")
   295→        self.display_header("📖 Quick Start Guide")
   296→        self.display_breadcrumb()
   297→
   298→        quickstart = self.base_dir / "docs" / "QUICKSTART.md"
   299→
   300→        if quickstart.exists():
   301→            try:
   302→                with open(quickstart, 'r') as f:
   303→                    lines = f.readlines()[:30]
   304→                    print(''.join(lines))
   305→                    total_lines = len(open(quickstart).readlines())
   306→                    print(f"\n... (showing first 30 lines of {total_lines} total)")
   307→            except Exception as e:
   308→                print(f"❌ Error reading quick start guide: {e}")
   309→        else:
   310→            print("❌ Quick start guide not found at docs/QUICKSTART.md")
   311→
   312→        print(f"\nFull guide: {quickstart}")
   313→        input("\nPress Enter to return to menu...")
   314→        self.menu_stack.pop()
   315→
   316→    # Placeholder methods
   317→    def template_browser(self): self._placeholder("Template Browser")
   318→    def search_songs(self): self._placeholder("Search Songs")
   319→    def validate_song(self): self._placeholder("Validate Specific Song")
   320→    def troubleshooting(self): self._placeholder("Troubleshooting")
   321→    def statistics(self): self._placeholder("Statistics")
   322→
   323→    def _placeholder(self, feature_name: str):
   324→        """Placeholder for features to be implemented"""
   325→        self.menu_stack.append(feature_name)
   326→        self.display_header(feature_name)
   327→        self.display_breadcrumb()
   328→
   329→        print(f"🚧 {feature_name} - Coming Soon!\n")
   330→        print("This feature will be implemented in a future update.")
   331→
   332→        input("\nPress Enter to return to menu...")
   333→        self.menu_stack.pop()
   334→
   335→
   336→def main():
   337→    """Main entry point"""
   338→    try:
   339→        menu = MenuSystem()
   340→        menu.main_menu()
   341→    except KeyboardInterrupt:
   342→        print("\n\n👋 Goodbye!")
   343→        sys.exit(0)
   344→    except Exception as e:
   345→        logger.exception("Fatal error in menu system")
   346→        print(f"\n❌ Fatal Error: {e}")
   347→        print("Check logs/ directory for details")
   348→        sys.exit(1)
   349→
   350→
   351→if __name__ == "__main__":
   352→    main()
   353→

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>
