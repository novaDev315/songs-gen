# Song Creation Workflow

**Purpose**: This document ensures all new songs are created without duplicates and properly tracked in the index.

---

## ⚠️ MANDATORY Pre-Creation Checklist

**Before creating ANY new song, complete these steps:**

### 1. Check for Duplicates

**Option A: Use Helper Script (Recommended)**
```bash
cd generated/
./check-and-update-index.sh check "Song Title"
```

**Option B: Manual Check**
1. Open `ALL-SONGS-INDEX.md`
2. Press `Ctrl+F` / `Cmd+F`
3. Search for similar titles, themes, or keywords
4. Check the appropriate genre section

### 2. Verify Number Sequence

Check if the song number is available:
```bash
ls -1 [genre]/[number]-*.md
# If no results, the number is available
```

### 3. Review Existing Songs in Genre

```bash
./check-and-update-index.sh list [genre]
```

---

## 📝 Song Creation Process

### Step 1: Design the Song

Before writing anything, determine:
- **Title**: Unique, memorable name
- **Genre**: Which directory (hip-hop, pop, edm, rock, country, r-b, fusion)
- **Theme**: What the song is about
- **Personas**: Which voices (PHOENIX, NEON, REBEL, CYPHER)
- **BPM**: Tempo (60-180 typical)
- **Key**: Major (uplifting) or Minor (intense)
- **Collection**: Is it part of a collection or standalone?

### Step 2: Create the File

**File Naming Convention:**
```
[genre]/[number]-[slug].md

Examples:
hip-hop/21-rise-up.md
pop/25-diamond-dreams.md
edm/26-neon-nights.md
```

**Use the Standard Template:**
```markdown
# [Song Title]

**Genre**: [Genre Name]
**Theme**: [Theme Description]
**Personas**: [Persona List]
**BPM**: [Number]
**Key**: [Major/Minor]

---

## Style Prompt

\```
[4-7 descriptors], [specific vocals], [instrumentation], [BPM], [key], [negative descriptors]
\```

## Lyrics

\```
[Intro tag]
[Verse 1 - PERSONA]
[Lyrics with formatting]
[Chorus - PERSONA]
[Lyrics]
[Additional sections...]
[Outro]
*instrument fade*
\```

## Why This Works

- **[Element 1]**: [Explanation]
- **[Element 2]**: [Explanation]
- **[Element 3]**: [Explanation]
- **[Element 4]**: [Explanation]
- **[Element 5]**: [Explanation]

## Generation Tips

- Generate 6+ variations
- [Specific tip 1]
- [Specific tip 2]
- Perfect for [use case]

---

**File**: \`generated/[path]/[filename]\`
**Part of**: [Collection Name] or Standalone
```

### Step 3: Update the Index

**Immediately after creating the file**, update `ALL-SONGS-INDEX.md`:

1. Open `ALL-SONGS-INDEX.md`
2. Find the appropriate genre section
3. Add the new entry:

**If part of a collection:**
```markdown
X. `genre/##-song-title.md` ⭐ - Brief description
```

**If standalone:**
```markdown
- `genre/##-song-title.md` - Brief description
```

4. Update the statistics:
   - Update song count for genre
   - Update total song count
   - Update "Last Updated" date

### Step 4: Verify the Update

```bash
./check-and-update-index.sh scan
```

This will show if any files are missing from the index.

---

## 🔄 Using the Helper Script

### Check for Duplicates
```bash
./check-and-update-index.sh check "My Song Title"
```

**Output:**
- ✓ Green = Title available
- ⚠️ Red = Duplicate found (shows existing entries)

### List Songs in Genre
```bash
./check-and-update-index.sh list hip-hop
./check-and-update-index.sh list pop
```

### Show Statistics
```bash
./check-and-update-index.sh stats
```

### Scan for Missing Entries
```bash
./check-and-update-index.sh scan
```

### Regenerate Index (Advanced)
```bash
./check-and-update-index.sh update
```

---

## 📋 Quick Reference - Claude Instructions

When asking Claude to create new songs, use this format:

```
Before creating the song, check ALL-SONGS-INDEX.md for:
1. Title duplicates (search for similar names)
2. Theme overlaps (check genre section)
3. Available number sequence

Then create a new song with:
- Title: [Song Title]
- Genre: [hip-hop/pop/edm/rock/country/r-b/fusion]
- Number: [Next available number in that genre]
- Theme: [What it's about]
- Personas: [Which voices to use]

After creation, update ALL-SONGS-INDEX.md with:
- File path entry in appropriate genre section
- Brief description
- Updated statistics
- Updated "Last Updated" date
```

---

## ✅ Quality Control Checklist

Before finalizing any new song:

- [ ] Title is unique (checked in index)
- [ ] File follows naming convention
- [ ] All template sections are complete
- [ ] Style prompt has 4-7 descriptors
- [ ] Lyrics have proper structure tags
- [ ] Formatting applied (CAPS, ellipses, etc.)
- [ ] Persona assignments are clear
- [ ] "Why This Works" has 5+ points
- [ ] Generation tips included
- [ ] Index updated with new entry
- [ ] Statistics updated
- [ ] "Last Updated" date changed
- [ ] Scan shows no missing entries

---

## 🎯 Best Practices

### DO:
✅ Always check index before creating
✅ Update index immediately after creation
✅ Use descriptive, unique titles
✅ Match personas to song content
✅ Include negative descriptors in style prompts
✅ Apply proper formatting to lyrics
✅ Test the helper script regularly

### DON'T:
❌ Skip the duplicate check
❌ Delay updating the index
❌ Use generic titles like "Song 1"
❌ Force persona combinations
❌ Forget negative descriptors
❌ Create files without proper structure
❌ Leave files untracked in the index

---

## 🔧 Troubleshooting

### "I created a song but it's not in the index"
1. Run: `./check-and-update-index.sh scan`
2. Manually add the entry to the appropriate section
3. Update statistics

### "The helper script isn't working"
1. Check if it's executable: `ls -l check-and-update-index.sh`
2. Make it executable: `chmod +x check-and-update-index.sh`
3. Ensure you're in the `generated/` directory

### "I found duplicate filenames"
1. One file should be renamed
2. Choose the one with lower quality or older date
3. Update references in the index
4. Verify no broken links

### "Song count doesn't match"
1. Run: `./check-and-update-index.sh stats`
2. Compare to index statistics
3. Run: `./check-and-update-index.sh scan`
4. Update index with missing entries

---

## 📊 Example Workflow

### Creating "Midnight Hustle" (Hip-Hop Song)

**Step 1: Check for duplicates**
```bash
$ ./check-and-update-index.sh check "Midnight Hustle"
✓ Title is available!
No duplicates found for "Midnight Hustle"
```

**Step 2: Check available number**
```bash
$ ls -1 hip-hop/*.md | tail -5
hip-hop/18-look-at-me-now.md
hip-hop/19-last-laugh.md
hip-hop/20-checkmate.md
# Next available: 21
```

**Step 3: Create the file**
```bash
$ touch hip-hop/21-midnight-hustle.md
# Fill in with template content
```

**Step 4: Update index**
- Open `ALL-SONGS-INDEX.md`
- Add to Hip-Hop section:
  ```markdown
  - `hip-hop/21-midnight-hustle.md` - Atlanta trap, late night grind theme
  ```
- Update Hip-Hop count: 28 → 29
- Update Total count: 86 → 87
- Update date: 2025-10-15 → 2025-10-16

**Step 5: Verify**
```bash
$ ./check-and-update-index.sh scan
✓ All files are indexed!
```

**Done!** ✅

---

## 🚀 Advanced: Batch Creation

When creating multiple songs:

1. **Plan all songs first**
   - List all titles
   - Check ALL for duplicates
   - Assign numbers sequentially

2. **Create files in order**
   - Don't skip steps
   - Update index after EACH song
   - Verify regularly

3. **Final verification**
   ```bash
   ./check-and-update-index.sh stats
   ./check-and-update-index.sh scan
   ```

---

**Remember**: The index is the source of truth. Keep it updated!

**Questions?** Refer to:
- `ALL-SONGS-INDEX.md` - Main index
- `COMPLETE-COLLECTION.md` - Triumph Collection reference
- `VERIFICATION-REPORT.md` - Quality standards
