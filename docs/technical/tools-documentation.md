# Tools Documentation

**Songs Generation System Tools Reference**

---

## Table of Contents

1. [Overview](#overview)
2. [Main Menu System](#main-menu-system)
3. [Core Tools](#core-tools)
4. [Management Tools](#management-tools)
5. [Validation Tools](#validation-tools)
6. [Running Tests](#running-tests)

---

## Overview

The Songs Generation System provides a comprehensive set of tools for creating and managing AI-generated music:

- **Interactive Menu** - User-friendly CLI interface
- **Song Creation** - Wizard for creating new songs
- **Management** - Index, duplicate checking, metadata extraction
- **Validation** - Comprehensive quality assurance
- **Testing** - Full test suite

---

## Main Menu System

### Entry Point

```bash
python3 tools/menu.py
```

### Menu Options

```
🎵 SONG CREATION
  [1] Create New Song (Interactive Wizard)
  [2] Browse Templates

📚 SONG MANAGEMENT
  [3] Browse Generated Songs
  [4] Search Songs
  [5] Check for Duplicates

✅ VALIDATION & QUALITY
  [6] Validate All Songs
  [7] Validate Specific Song

📖 DOCUMENTATION
  [8] Quick Start Guide
  [9] Troubleshooting

📊 ABOUT
  [10] View Statistics
```

### Architecture

**File**: `tools/menu.py`

**Key Classes**:
- `MenuSystem` - Main menu controller

**Features**:
- Interactive navigation
- Breadcrumb tracking
- Cross-platform terminal support
- Integrated help system

---

## Core Tools

### 1. Song Creation Wizard

**File**: `tools/core/song_creator.py`

**Class**: `SongCreationWizard`

**Purpose**: Interactive 6-step song creation process

**Steps**:
1. Genre selection (8 genres)
2. Song title entry
3. Theme/mood input
4. Persona selection (multi-singer)
5. Content generation
6. Save to disk

**Usage**:
```python
from tools.core.song_creator import SongCreationWizard
from pathlib import Path

wizard = SongCreationWizard(Path('.'))
wizard.run()
```

**Output**:
- `generated/songs/[genre]/[song-id]-[title].md`
- `generated/songs/[genre]/[song-id]-[title].meta.json`

---

### 2. UUID Generator

**File**: `tools/core/uuid_generator.py`

**Class**: `UUIDGenerator`

**Purpose**: Generate unique 12-character UUIDs with collision detection

**Features**:
- 12-character hex UUIDs (281 trillion combinations)
- Collision detection (< 0.000018% collision for 10k songs)
- UUID validation
- Load existing IDs from metadata

**Usage**:
```python
from tools.core.uuid_generator import UUIDGenerator
from pathlib import Path

gen = UUIDGenerator()
uuid = gen.generate()  # Returns: "a1b2c3d4e5f6"

# Validate
is_valid = gen.validate_uuid("a1b2c3d4e5f6")  # True

# Load existing IDs
existing = gen.load_existing_ids(Path('./generated'))
```

---

### 3. Logging System

**File**: `tools/core/logging_config.py`

**Functions**:
- `setup_logging()` - Configure logging system
- `SafeFileOperations` - Safe file operations with error handling

**Usage**:
```python
from tools.core.logging_config import setup_logging
from pathlib import Path

# Setup logging
setup_logging(Path('./logs'), 'DEBUG')

# Use logging
import logging
logger = logging.getLogger(__name__)
logger.info("Message to log")
```

**Log Files**:
- `logs/songs-gen-YYYYMMDD.log` - All logs
- `logs/errors-YYYYMMDD.log` - Errors only
- Console output - INFO level and above

---

## Management Tools

### 1. Duplicate Checker

**File**: `tools/management/duplicate_checker.py`

**Class**: `DuplicateChecker`

**Purpose**: Detect duplicate or similar song titles

**Methods**:
```python
from tools.management.duplicate_checker import DuplicateChecker
from pathlib import Path

checker = DuplicateChecker(Path('./generated'))

# Check specific title
results = checker.check_title("Summer Love", threshold=0.8)
# Returns: [{'file': '...', 'title': '...', 'similarity': 0.95}]

# Scan all for duplicates
duplicates = checker.scan_all()
# Returns: [{'title': '...', 'files': [...], 'count': 2}]

# Get statistics
stats = checker.get_statistics()
# Returns: {'total': 86, 'by_genre': {'pop': 21, ...}}
```

---

### 2. Metadata Extractor

**File**: `tools/management/metadata_extractor.py`

**Class**: `MetadataExtractor`

**Purpose**: Extract and search song metadata

**Methods**:
```python
from tools.management.metadata_extractor import MetadataExtractor
from pathlib import Path

extractor = MetadataExtractor(Path('./generated'))

# Search by title, theme, or persona
results = extractor.search("victory")
# Returns: [{'id': '...', 'title': '...', 'genre': '...'}]

# Get songs by genre
pop_songs = extractor.get_by_genre("pop")
# Returns: [song1, song2, ...]

# Get statistics
stats = extractor.get_statistics()
# Returns: {'total_songs': 86, 'by_genre': {...}}

# Export metadata
extractor.export_metadata(Path('./metadata.json'))

# Validate metadata
issues = extractor.validate_metadata()
# Returns: {'missing_fields': [...], 'invalid_genres': [...]}
```

---

### 3. Index Manager

**File**: `tools/management/index_manager.py`

**Class**: `IndexManager`

**Purpose**: Manage song indexes and collections

**Methods**:
```python
from tools.management.index_manager import IndexManager
from pathlib import Path

manager = IndexManager(Path('./generated'))

# Scan and get statistics
stats = manager.scan_songs()

# Validate index
issues = manager.validate_index()

# Generate collection views
manager.generate_collection_views()
# Creates: TRIUMPH-COLLECTION.md, STANDALONE-SONGS.md

# Update all songs index
manager.update_all_songs_index()
# Creates/Updates: ALL-SONGS-INDEX.md
```

---

### 4. Atomic Migrator

**File**: `tools/management/atomic_migrator.py`

**Class**: `AtomicMigrator`

**Purpose**: Safe two-phase song migration with validation and rollback

**Three Phases**:

1. **Phase 1**: Create staging area
   - Copy all songs to staging directory
   - Generate UUIDs for each song
   - Create metadata files

2. **Phase 2**: Validate staging
   - Verify all files migrated
   - Check metadata completeness
   - Validate song structure

3. **Phase 3**: Atomic swap
   - Create backup of current state
   - Move staging to production
   - Rollback on failure

**Usage**:
```python
from tools.management.atomic_migrator import AtomicMigrator
from pathlib import Path

migrator = AtomicMigrator(
    Path('./generated/songs'),
    Path('./generated/songs-v2')
)

success = migrator.execute_migration()
if success:
    print("Migration successful!")
else:
    print("Migration failed, rolled back")
```

**Features**:
- ✅ Collision-safe UUID generation
- ✅ Comprehensive validation
- ✅ Automatic rollback on failure
- ✅ Migration logging

---

## Validation Tools

### Song Validator

**File**: `tools/validation/validator.py`

**Classes**:
- `SongValidator` - Validate song markdown files
- `MetadataValidator` - Validate JSON metadata
- `validate_all_songs()` - Bulk validation

**Usage**:
```python
from tools.validation.validator import SongValidator, validate_all_songs
from pathlib import Path

# Validate single song
validator = SongValidator()
is_valid, errors, warnings = validator.validate_song_file(
    Path('./generated/songs/pop/song.md')
)

# Validate all songs
results = validate_all_songs(Path('./generated'))
# Returns:
# {
#   'total': 86,
#   'valid': 85,
#   'errors': 1,
#   'warnings': 5,
#   'details': [...]
# }
```

**Validation Checks**:
- ✅ Required fields present
- ✅ Valid genre
- ✅ Style prompt quality (4-7 descriptors)
- ✅ Lyrics structure tags
- ✅ Metadata file existence
- ✅ File integrity

---

## Running Tests

### Install Test Dependencies

```bash
pip install -e ".[test]"
```

### Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=tools --cov-report=html

# Run specific test file
pytest tests/test_uuid_generator.py -v

# Run specific test
pytest tests/test_uuid_generator.py::TestUUIDGeneration::test_uuid_length -v
```

### Test Files

```
tests/
├── __init__.py
├── test_uuid_generator.py      # UUID generation tests
├── test_validator.py           # Validation tests
└── test_logging.py             # Logging system tests
```

### Sample Test Output

```
tests/test_uuid_generator.py::TestUUIDGeneration::test_uuid_length PASSED
tests/test_uuid_generator.py::TestUUIDGeneration::test_uuid_is_hex PASSED
tests/test_uuid_generator.py::TestUUIDGeneration::test_uuid_uniqueness PASSED
tests/test_validator.py::TestSongValidator::test_validator_init PASSED
tests/test_logging.py::TestLoggingSetup::test_logging_initialization PASSED

======================== 15 passed in 0.42s ========================
```

---

## Integration Example

### Complete Workflow

```python
#!/usr/bin/env python3
"""Complete songs-gen workflow example"""

from pathlib import Path
from tools.core.song_creator import SongCreationWizard
from tools.management.duplicate_checker import DuplicateChecker
from tools.management.index_manager import IndexManager
from tools.validation.validator import validate_all_songs

def main():
    base_dir = Path('.')

    # 1. Create new song
    wizard = SongCreationWizard(base_dir)
    wizard.run()

    # 2. Check for duplicates
    checker = DuplicateChecker(base_dir / 'generated')
    duplicates = checker.scan_all()
    print(f"Found {len(duplicates)} duplicate groups")

    # 3. Update indexes
    manager = IndexManager(base_dir / 'generated')
    manager.update_all_songs_index()
    manager.generate_collection_views()

    # 4. Validate all songs
    results = validate_all_songs(base_dir)
    print(f"Validation: {results['valid']}/{results['total']} valid")

    if results['errors'] > 0:
        print("⚠️  Errors found:")
        for detail in results['details']:
            for error in detail['errors']:
                print(f"  - {error}")

if __name__ == '__main__':
    main()
```

---

## Troubleshooting Tools

### Enable Debug Logging

```bash
export SONGS_GEN_LOG_LEVEL=DEBUG
python3 tools/menu.py
```

### Check Tool Status

```bash
python3 -c "
from tools.core.logging_config import setup_logging
from tools.core.uuid_generator import UUIDGenerator
from tools.validation.validator import SongValidator

setup_logging()
print('✓ Logging configured')

uuid_gen = UUIDGenerator()
print(f'✓ UUID generator ready: {uuid_gen.generate()}')

validator = SongValidator()
print('✓ Validator ready')
"
```

### Manual Tool Usage

```bash
# Create test UUIDs
python3 -c "from tools.core.uuid_generator import UUIDGenerator; gen = UUIDGenerator(); print(gen.generate())"

# Validate all songs
python3 -c "from tools.validation.validator import validate_all_songs; from pathlib import Path; print(validate_all_songs(Path('.')))"

# Extract metadata
python3 -c "from tools.management.metadata_extractor import MetadataExtractor; from pathlib import Path; ext = MetadataExtractor(Path('./generated')); print(ext.get_statistics())"
```

---

## Version Information

- **Version**: 2.0.0
- **Last Updated**: October 16, 2025
- **Python**: 3.8+
- **Platform**: Windows, macOS, Linux

---

## Related Documentation

- [Main Documentation Hub](./README.md)
- [API Architecture](./ARCHITECTURE.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [FAQ](../guides/faq.md)
