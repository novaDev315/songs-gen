# Quick Reference Card

**Keep this open while creating songs!**

---

## ⚡ Before Creating ANY Song

```bash
# 1. Check for duplicates
./check-and-update-index.sh check "Song Title"

# 2. List existing songs in genre
./check-and-update-index.sh list [genre]

# 3. Check current stats
./check-and-update-index.sh stats
```

---

## 📁 File Naming

```
[genre]/[number]-[slug].md

Examples:
hip-hop/21-midnight-hustle.md
pop/25-diamond-sky.md
edm/26-neon-pulse.md
```

---

## 📝 Must-Have Sections

1. ✅ Metadata (Genre, Theme, Personas, BPM, Key)
2. ✅ Style Prompt (4-7 descriptors + negatives)
3. ✅ Complete Lyrics (with tags and formatting)
4. ✅ Why This Works (5+ points)
5. ✅ Generation Tips (4+ tips)

---

## 🎤 Persona Quick Guide

| Persona | Voice Type | Use For |
|---------|-----------|---------|
| **PHOENIX** | Powerful female | Choruses, empowerment, rock vocals |
| **NEON** | Smooth male | Hooks, R&B, melodic sections |
| **REBEL** | Aggressive female | Rap, hype, adlibs |
| **CYPHER** | Storytelling rap | Verses, narrative, flow |

**Rule**: Match personas to content, don't force formulas!

---

## 🎵 Style Prompt Formula

```
[Genre], [subgenre], [mood], [personas with voice descriptions],
[instrumentation], [BPM] BPM, [key] key, [special elements],
no [unwanted element], no [unwanted element]
```

**Example**:
```
Atlanta trap, dark hip-hop, triumphant, CYPHER aggressive rap,
NEON auto-tune hooks, heavy 808 bass, 140 BPM, minor key,
no pop, no acoustic
```

---

## ✏️ Lyrics Formatting

| Format | Effect | Example |
|--------|--------|---------|
| `CAPS` | Louder/emphasis | `I'M UNSTO-O-OPPABLE!` |
| `ellipses...` | Slower/pause | `feeling grateful...` |
| `extended vo-o-owels` | Sustained notes | `lo-o-o-ve` |
| `!` | Energy/excitement | `Let's go!` |
| `(directions)` | Performance hint | `(powerful)` `(smooth)` |
| `*effects*` | Sound effects | `*bass drop*` `*guitar fade*` |
| `[Structure]` | Song sections | `[Verse 1]` `[Chorus]` |
| `[Intro - PERSONA]` | Assign to voice | `[Verse 1 - PHOENIX]` |
| `(PERSONA: text)` | Adlib/backing | `(NEON: yeah!)` |

---

## 📊 After Creation Checklist

```bash
# 1. Update ALL-SONGS-INDEX.md
- [ ] Add file entry to genre section
- [ ] Update genre song count
- [ ] Update total song count
- [ ] Update "Last Updated" date

# 2. Verify
./check-and-update-index.sh scan

# 3. Should show:
✓ All files are indexed!
```

---

## 🎯 Common Numbers by Genre

**Hip-Hop**: Next available usually in 20s range
**Pop**: Next available usually in 20s range
**EDM**: Next available around 26+
**Rock**: Next available around 31+
**Country**: 31-35 (Triumph Collection)
**R&B**: 36-40 (Triumph Collection)
**Fusion**: Next available around 46+

*Always verify with `ls -1 [genre]/*.md | tail -5`*

---

## 🚫 Common Mistakes

❌ Not checking for duplicates
❌ Forgetting to update index
❌ Using generic titles
❌ Skipping negative descriptors
❌ Missing structure tags
❌ Wrong persona assignments
❌ Incomplete lyrics formatting

---

## ✅ Quality Standards

- **Style Prompt**: 4-7 descriptors minimum
- **Lyrics Length**: 100-150 lines typical
- **File Length**: 130-160 lines total
- **Sections**: All 5 required sections complete
- **Format**: Follows exact template structure

---

## 🔧 Helper Script Commands

```bash
# Check duplicate
./check-and-update-index.sh check "Title"

# List genre
./check-and-update-index.sh list hip-hop

# Show stats
./check-and-update-index.sh stats

# Find missing
./check-and-update-index.sh scan

# Regenerate (advanced)
./check-and-update-index.sh update
```

---

## 📖 Full Documentation

- **`ALL-SONGS-INDEX.md`** - Complete song catalog (CHECK FIRST!)
- **`SONG-CREATION-WORKFLOW.md`** - Detailed workflow
- **`COMPLETE-COLLECTION.md`** - Triumph Collection reference
- **`VERIFICATION-REPORT.md`** - Quality standards

---

## 🎵 Generation Tips (Universal)

1. **Always generate 6+ variations** per song
2. **Use exact style prompts** as written
3. **Copy lyrics exactly** with all formatting
4. **Try off-peak hours** (3-4 AM local time)
5. **One change at a time** when iterating
6. **Replace sections** on nearly-perfect songs

---

**⚠️ GOLDEN RULE**: Check index BEFORE creating. Update index AFTER creating!

---

**Print this page and keep it visible while working!**
