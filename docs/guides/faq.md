# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is Songs Generation System?

**A**: Songs Generation System is a comprehensive toolkit for creating AI-generated music with Suno AI. It provides:
- Interactive song creation wizard
- Best practices templates for 7+ genres
- Persona matching system for multi-singer songs
- Metadata management and validation
- Song indexing and duplicate checking

---

### Q: Do I need any special software?

**A**: You need:
- Python 3.8 or higher
- A text editor (VS Code, Sublime, etc.)
- Suno AI account (for generating actual music)

The system is cross-platform (Windows, macOS, Linux).

---

### Q: Is this official Suno AI software?

**A**: No. This is an unofficial community project designed to optimize workflows with Suno AI. It's not affiliated with Suno AI.

---

## Getting Started

### Q: How do I create my first song?

**A**:
1. Run `python3 tools/menu.py`
2. Select "Create New Song (Interactive Wizard)"
3. Follow the wizard steps (genre, title, theme, mood)
4. System generates a template with style prompt and lyrics structure
5. Copy both to Suno AI Custom Mode
6. Click Generate!

---

### Q: What's the 4-7 descriptor rule?

**A**: Style prompts work best with 4-7 descriptive phrases:
- **Too few** (<4): Generic output
- **4-7**: Perfect! Best results
- **Too many** (>10): Confuses the AI

**Example**:
```
✅ Good (5 descriptors):
Pop, upbeat, female vocals, synth pads, 125 BPM

❌ Too few (2):
Pop, happy

❌ Too many (10):
Pop, upbeat, energetic, happy, female, vocals, synth, electronic, fast, 125 BPM
```

---

### Q: What are personas and why do I need them?

**A**: Personas are voice characteristics for multi-singer songs:
- **PHOENIX**: Powerful, emotional (lead vocals)
- **NEON**: Smooth, soulful (harmonies, bridges)
- **REBEL**: Edgy, rap-focused (verses, energy)

Don't force all three together! Match personas to YOUR lyrics' emotional journey.

---

### Q: What's the difference between templates?

**A**: Each genre has optimized templates with:
- Genre-specific structure patterns
- Instrumentation guidance
- BPM ranges
- Vocal style recommendations
- Best practices for that genre

---

## Song Creation

### Q: How many songs can I create?

**A**: Unlimited! Create as many as you want. Each gets a unique ID.

---

### Q: Can I edit songs after creating them?

**A**: Yes! Edit the `.md` files in `generated/songs/[genre]/` directly, then:
1. Update the metadata `.meta.json` file to match
2. Increment the version number
3. Re-generate in Suno AI

---

### Q: What if two people create songs with the same title?

**A**: Each song gets a unique UUID, so titles can repeat. The system won't consider them duplicates (they're in metadata, not just filename).

---

### Q: How do I organize my songs?

**A**: Songs are organized by:
- **Genre**: `generated/songs/[genre]/`
- **Collection**: `generated/songs/[genre]/triumph/` or `standalone/`

Edit the `.meta.json` file's `collection` field to change categories.

---

### Q: Should I generate one version or multiple?

**A**: **Always generate 6+ variations!**
- Same prompt = different results (AI randomization)
- Professional creators generate 10-15+
- Pick the best version and iterate from there

---

## Style Prompts

### Q: Why doesn't my style prompt work?

**A**: Check:
1. **4-7 descriptors**? Follow the rule!
2. **Specific enough**? "Pop, catchy, good" is too vague
3. **Negative descriptors**? Add "no [unwanted style]" to prevent drift
4. **Spell check**? Typos confuse AI

---

### Q: Can I reuse style prompts?

**A**: Absolutely! If a prompt worked well:
1. Save it to `docs/reference/style-prompt-library.md`
2. Reuse for similar songs
3. Tweak slightly for variations

---

### Q: What about regional accents?

**A**: For hip-hop specifically, include region:
- "Memphis trap" (southern bounce)
- "West Coast hip-hop" (smooth, funky)
- "East Coast hip-hop" (boom-bap, aggressive)

---

## Lyrics & Structure

### Q: What structure tags do I need?

**A**: Essential tags:
- `[Intro]` - Opening
- `[Verse]` - Main lyrical content
- `[Chorus]` - Hook (most important!)
- `[Bridge]` - Contrast/mood shift
- `[Outro]` - Ending

Optional:
- `[Pre-Chorus]` - Build-up to chorus
- `[Interlude]` - Instrumental break

---

### Q: How do I make a chorus more powerful?

**A**: Use:
- `CAPS` on key phrases
- Repeated words: "Love, love, love!"
- Vocal techniques: "Lo-o-o-ve" (sustained)
- Sound effects: `*bass drop*`
- Performance cues: `(PHOENIX POWERFUL:)`

---

### Q: What if my song is too long?

**A**: Suno generates ~3-4 minute songs. If yours is longer:
1. Split into two songs (Part 1, Part 2)
2. Combine strong verses/chorus into one
3. Use shorter structure (drop bridge, etc.)

---

## Validation & Quality

### Q: What does the validation check?

**A**: It verifies:
- Required fields present (title, genre, etc.)
- Valid genre selected
- Style prompt follows best practices
- Lyrics have proper structure tags
- Metadata file exists and is valid
- Song and metadata files match

---

### Q: Should I fix all warnings?

**A**: **Errors**: Yes, always fix these!

**Warnings**: Usually OK to ignore, but:
- "Style prompt too short" = might be generic
- "No [Chorus]" = song might be confusing

---

## Technical Questions

### Q: Where are my songs stored?

**A**:
```
generated/songs/[genre]/[collection]/[uuid]-[title].md
generated/songs/[genre]/[collection]/[uuid]-[title].meta.json
```

Example:
```
generated/songs/pop/triumph/a1b2c3d4e5f6-summer-love.md
generated/songs/pop/triumph/a1b2c3d4e5f6-summer-love.meta.json
```

---

### Q: What is the metadata file for?

**A**: The `.meta.json` stores:
- **id**: Unique UUID for the song
- **title**: Song title
- **genre**: Genre category
- **theme**: What the song is about
- **mood**: Emotional tone
- **personas**: Voice characteristics (multi-singer)
- **version**: Track iterations
- **created_by**: How it was created (wizard, manual, etc.)

This enables searching, sorting, and duplicate detection.

---

### Q: Can I backup my songs?

**A**: Yes!
```bash
# Backup all songs
tar -czf backup-$(date +%Y%m%d).tar.gz generated/songs/

# Restore
tar -xzf backup-*.tar.gz
```

---

## Integration with Suno AI

### Q: How do I use these in Suno AI?

**A**:
1. Copy the **Style Prompt** (between ```)
2. Go to Suno AI → Custom Mode
3. Paste into "Style of Music" field
4. Copy the **Lyrics** (everything after `## Lyrics`)
5. Paste into "Lyrics" field
6. Add title
7. Click Generate!

---

### Q: Can I use both Simple and Custom modes?

**A**:
- **Simple Mode**: Good for quick tries
- **Custom Mode**: Better control, recommended for this system

Use Custom for best results with your style prompts.

---

## Troubleshooting

### Q: Songs aren't showing in the menu

**A**:
1. Verify `generated/songs/` exists
2. Check song files end with `.md`
3. Regenerate indexes:
   ```bash
   python3 tools/management/index_manager.py --regenerate
   ```

---

### Q: I'm getting UUID errors

**A**: This is extremely rare. If you see UUID collision warnings:
1. Restart the menu system
2. Check system has sufficient entropy
3. Report if persists

---

### Q: How do I update my system?

**A**:
```bash
git pull origin main
python3 tools/menu.py
```

---

## Best Practices

### Q: What's the workflow for best results?

**A**:
1. **Choose genre** - Pick template matching your style
2. **Create song** - Use interactive wizard
3. **Generate variations** - 6-15+ in Suno AI
4. **Compare versions** - Listen to all
5. **Pick best** - Select the winner
6. **Refine** - Use "Replace Section" for problem areas
7. **Document** - Save notes on what worked

---

### Q: How often should I generate?

**A**:
- **Off-peak hours** (3-4 AM) often have better quality
- **Batch similar songs** - Different takes on same concept
- **Space out long projects** - Don't burn out system resources

---

### Q: Any tips for multi-singer songs?

**A**:
1. Read `personas/persona-selection-guide.md`
2. Match personas to YOUR lyrics (don't force formula)
3. Use 2-3 personas max
4. Give each persona distinct sections
5. Test with 6-10 variations

---

## More Help?

- **Documentation**: Check `docs/` directory
- **Troubleshooting**: See `docs/guides/troubleshooting.md`
- **Templates**: Browse `templates/[genre]/`
- **Examples**: See `examples/example-songs.md`
- **Personas**: Read `personas/persona-selection-guide.md`

---

**Last Updated**: 2025-10-16
