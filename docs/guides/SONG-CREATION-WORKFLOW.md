     1→# Song Creation Workflow
     2→
     3→**Purpose**: This document ensures all new songs are created without duplicates and properly tracked in the index.
     4→
     5→---
     6→
     7→## ⚠️ MANDATORY Pre-Creation Checklist
     8→
     9→**Before creating ANY new song, complete these steps:**
    10→
    11→### 1. Check for Duplicates
    12→
    13→**Option A: Use Helper Script (Recommended)**
    14→```bash
    15→cd generated/
    16→./check-and-update-index.sh check "Song Title"
    17→```
    18→
    19→**Option B: Manual Check**
    20→1. Open `ALL-SONGS-INDEX.md`
    21→2. Press `Ctrl+F` / `Cmd+F`
    22→3. Search for similar titles, themes, or keywords
    23→4. Check the appropriate genre section
    24→
    25→### 2. Verify Number Sequence
    26→
    27→Check if the song number is available:
    28→```bash
    29→ls -1 [genre]/[number]-*.md
    30→# If no results, the number is available
    31→```
    32→
    33→### 3. Review Existing Songs in Genre
    34→
    35→```bash
    36→./check-and-update-index.sh list [genre]
    37→```
    38→
    39→---
    40→
    41→## 📝 Song Creation Process
    42→
    43→### Step 1: Design the Song
    44→
    45→Before writing anything, determine:
    46→- **Title**: Unique, memorable name
    47→- **Genre**: Which directory (hip-hop, pop, edm, rock, country, r-b, fusion)
    48→- **Theme**: What the song is about
    49→- **Personas**: Which voices (PHOENIX, NEON, REBEL, CYPHER)
    50→- **BPM**: Tempo (60-180 typical)
    51→- **Key**: Major (uplifting) or Minor (intense)
    52→- **Collection**: Is it part of a collection or standalone?
    53→
    54→### Step 2: Create the File
    55→
    56→**File Naming Convention:**
    57→```
    58→[genre]/[number]-[slug].md
    59→
    60→Examples:
    61→hip-hop/21-rise-up.md
    62→pop/25-diamond-dreams.md
    63→edm/26-neon-nights.md
    64→```
    65→
    66→**Use the Standard Template:**
    67→```markdown
    68→# [Song Title]
    69→
    70→**Genre**: [Genre Name]
    71→**Theme**: [Theme Description]
    72→**Personas**: [Persona List]
    73→**BPM**: [Number]
    74→**Key**: [Major/Minor]
    75→
    76→---
    77→
    78→## Style Prompt
    79→
    80→\```

<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>
