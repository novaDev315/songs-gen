#!/bin/bash
# Helper script to check for duplicate songs and update ALL-SONGS-INDEX.md
# Usage: ./check-and-update-index.sh [action] [song-title] [genre]

set -e

INDEX_FILE="ALL-SONGS-INDEX.md"
BACKUP_FILE="ALL-SONGS-INDEX.backup.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [action] [arguments]"
    echo ""
    echo "Actions:"
    echo "  check <title>           - Check if a song title already exists"
    echo "  list <genre>            - List all songs in a genre"
    echo "  stats                   - Show current statistics"
    echo "  scan                    - Scan all directories and show missing entries"
    echo "  update                  - Regenerate entire index from files"
    echo ""
    echo "Examples:"
    echo "  $0 check \"No Looking Back\""
    echo "  $0 list hip-hop"
    echo "  $0 stats"
    echo "  $0 scan"
    echo "  $0 update"
    exit 1
}

# Function to check if a song exists
check_song() {
    local title="$1"
    echo -e "${BLUE}Checking for song: \"$title\"${NC}"
    echo ""

    if grep -i "$title" "$INDEX_FILE" > /dev/null 2>&1; then
        echo -e "${RED}⚠️  DUPLICATE FOUND!${NC}"
        echo ""
        echo "Existing entries:"
        grep -i "$title" "$INDEX_FILE" | grep -v "^#" | grep -v "^$"
        echo ""
        echo -e "${YELLOW}Consider using a different title or verify this is a different song.${NC}"
        return 1
    else
        echo -e "${GREEN}✓ Title is available!${NC}"
        echo "No duplicates found for \"$title\""
        return 0
    fi
}

# Function to list songs in a genre
list_genre() {
    local genre="$1"
    echo -e "${BLUE}Songs in genre: $genre${NC}"
    echo ""

    if [ -d "$genre" ]; then
        echo "Files in directory:"
        ls -1 "$genre"/*.md 2>/dev/null | wc -l
        ls -1 "$genre"/*.md 2>/dev/null | sed 's|^.*/||'
    else
        echo -e "${RED}Directory $genre not found${NC}"
    fi
}

# Function to show statistics
show_stats() {
    echo -e "${BLUE}=== CURRENT STATISTICS ===${NC}"
    echo ""

    for dir in hip-hop pop edm rock country r-b fusion; do
        if [ -d "$dir" ]; then
            count=$(ls -1 "$dir"/*.md 2>/dev/null | wc -l)
            printf "%-20s: %3d songs\n" "$dir" "$count"
        fi
    done

    echo ""
    total=$(find hip-hop pop edm rock country r-b fusion -name "*.md" 2>/dev/null | wc -l)
    echo -e "${GREEN}Total: $total songs${NC}"
}

# Function to scan for missing entries
scan_missing() {
    echo -e "${BLUE}=== SCANNING FOR MISSING INDEX ENTRIES ===${NC}"
    echo ""

    missing=0
    for file in $(find hip-hop pop edm rock country r-b fusion -name "*.md" 2>/dev/null | sort); do
        filename=$(basename "$file")
        if ! grep -q "$filename" "$INDEX_FILE"; then
            echo -e "${YELLOW}⚠️  Not in index: $file${NC}"
            ((missing++))
        fi
    done

    if [ $missing -eq 0 ]; then
        echo -e "${GREEN}✓ All files are indexed!${NC}"
    else
        echo ""
        echo -e "${RED}Found $missing files not in index${NC}"
        echo -e "${YELLOW}Run '$0 update' to regenerate the index${NC}"
    fi
}

# Function to update the entire index
update_index() {
    echo -e "${BLUE}=== REGENERATING INDEX ===${NC}"
    echo ""

    # Create backup
    if [ -f "$INDEX_FILE" ]; then
        cp "$INDEX_FILE" "$BACKUP_FILE"
        echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"
    fi

    # Get current date
    current_date=$(date +%Y-%m-%d)

    # Count total files
    total=$(find hip-hop pop edm rock country r-b fusion -name "*.md" 2>/dev/null | wc -l)

    echo "Scanning directories..."
    echo "Total songs found: $total"
    echo ""
    echo -e "${YELLOW}Note: You'll need to manually categorize songs into collections${NC}"
    echo -e "${YELLOW}and add descriptions. This only updates the file list.${NC}"
    echo ""

    # Generate file list
    echo "Files by genre:"
    for dir in hip-hop pop edm rock country r-b fusion; do
        if [ -d "$dir" ]; then
            count=$(ls -1 "$dir"/*.md 2>/dev/null | wc -l)
            echo "  $dir: $count files"
        fi
    done

    echo ""
    echo -e "${GREEN}✓ Index scan complete${NC}"
    echo ""
    echo "To complete the update:"
    echo "1. Open ALL-SONGS-INDEX.md"
    echo "2. Update the 'Last Updated' date to: $current_date"
    echo "3. Update the 'Total Songs' count to: $total"
    echo "4. Review new files and add them to appropriate sections"
}

# Main script logic
case "${1:-}" in
    check)
        if [ -z "${2:-}" ]; then
            echo "Error: Song title required"
            usage
        fi
        check_song "$2"
        ;;
    list)
        if [ -z "${2:-}" ]; then
            echo "Error: Genre required"
            usage
        fi
        list_genre "$2"
        ;;
    stats)
        show_stats
        ;;
    scan)
        scan_missing
        ;;
    update)
        update_index
        ;;
    *)
        usage
        ;;
esac
