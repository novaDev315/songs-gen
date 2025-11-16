# Songs-Gen Quick Start Guide

Get started creating AI-generated songs in minutes with Claude Code and Suno AI.

---

## 🚀 3-Minute Quick Start

### 1. Choose Your Path

**Option A: Single-Singer Song (Easiest)**
```bash
# Pick a genre template
templates/pop/pop-template.md          # For pop music
templates/hip-hop/hip-hop-template.md  # For rap/hip-hop
templates/edm/edm-template.md          # For electronic
templates/rock/rock-template.md        # For rock music
templates/country/country-template.md  # For country
templates/jazz/jazz-template.md        # For jazz
```

**Option B: Multi-Singer Song (Advanced)**
```bash
templates/multi-singer/multi-singer-template.md  # Professional multi-voice songs
```

### 2. Ask Claude to Create Your Song

**Simple Prompt:**
```
"Create a [GENRE] song about [TOPIC] with [MOOD/STYLE]"
```

**Example:**
```
"Create a pop song about summer romance with upbeat, dreamy vibes"
```

**Detailed Prompt:**
```
"Using the [GENRE] template, create a song about [TOPIC] that:
- Has a [MOOD] mood
- Includes [SPECIFIC ELEMENTS]
- Uses [INSTRUMENTATION]
- Is [TEMPO/ENERGY LEVEL]"
```

**Example:**
```
"Using the pop template, create a song about overcoming anxiety that:
- Has an empowering, uplifting mood
- Includes a powerful chorus and vulnerable verses
- Uses electronic production with piano
- Is mid-tempo building to high energy"
```

### 3. Claude Generates Complete Song

Claude will create:
- ✅ Optimized style prompt (4-7 descriptors)
- ✅ Complete formatted lyrics with structure tags
- ✅ Performance directions and emphasis
- ✅ Sound effects and vocal instructions
- ✅ Ready to paste into Suno AI

### 4. Copy to Suno AI

1. Go to Suno AI
2. Select **Custom Mode**
3. Paste **Style Prompt** into the "Style of Music" field
4. Paste **Lyrics** into the "Lyrics" field
5. Add your title
6. Click Create

### 5. Generate Multiple Variations

**Important:** Always generate 6+ variations!
- Same prompt = different results (AI randomization)
- Test variations to find the best version

---

## 📚 What's in This System?

### Templates (Your Starting Point)
```
templates/
├── pop/            # Pop music (most beginner-friendly)
├── hip-hop/        # Rap and hip-hop
├── edm/            # Electronic and dance
├── rock/           # Rock music all styles
├── country/        # Country and Americana
├── jazz/           # Jazz (1920s-1950s works best)
└── multi-singer/   # Advanced multi-voice songs
```

### Reference Guides (Deep Knowledge)
```
reference/
├── Mastering Suno AI Prompt Engineering...md  # Complete guide
└── Suno AI Multi-Singer Song Creation Guide.md  # Multi-voice guide
```

### Personas (For Multi-Singer Songs)
```
personas/
├── persona-library.md         # Complete persona catalog
└── persona-selection-guide.md # Choose based on YOUR lyrics
```

### Workflows (Step-by-Step Processes)
```
workflows/
└── song-creation-workflow.md  # Detailed creation process
```

### Examples (Learn from Success)
```
examples/
└── example-songs.md  # 5 complete example songs with analysis
```

---

## 🎯 Choose Your Skill Level

### Beginner: Start Here

1. **Read**: `templates/pop/pop-template.md` (simplest structure)
2. **Study**: `examples/example-songs.md` → "Neon Hearts" example
3. **Ask Claude**:
   ```
   "Create a simple pop song about [YOUR TOPIC] with [YOUR MOOD].
   Use the pop template and keep it beginner-friendly."
   ```
4. **Generate**: 6+ variations in Suno AI
5. **Track**: What worked in the template's iteration section

**Expected Time:** 90 minutes for first song

### Intermediate: Level Up

1. **Choose Genre**: Pick the template matching your style
2. **Study Multiple Examples**: Read 2-3 examples from `examples/example-songs.md`
3. **Use Detailed Prompt**:
   ```
   "Create a [GENRE] song about [TOPIC] that:
   - Mood: [SPECIFIC MOOD]
   - Structure: [VERSE-CHORUS or custom]
   - Instrumentation: [LIST INSTRUMENTS]
   - Special elements: [LIST TECHNIQUES]

   Use the [GENRE] template and apply these techniques:
   [LIST SPECIFIC FORMATTING/TECHNIQUES]"
   ```
4. **Iterate**: Use `workflows/song-creation-workflow.md` → Standard Workflow
5. **Refine**: Use Replace Section for problem areas

**Expected Time:** 4-6 hours for polished song

### Advanced: Pro Level

1. **Multi-Singer Songs**: Use `templates/multi-singer/multi-singer-template.md`
2. **Read Persona Guide**: `personas/persona-selection-guide.md` → Match personas to YOUR lyrics
3. **Study Complex Examples**: "Electric Dreams" or "Beyond the Orion Spur"
4. **Ask Claude**:
   ```
   "Create a multi-singer [GENRE] song about [TOPIC].

   Lyrics should have:
   - [EMOTIONAL JOURNEY]
   - [STRUCTURAL ELEMENTS]
   - [RAP OR NO RAP]

   Based on the lyrical content and theme, suggest the optimal
   persona combination from the persona library and assign them
   strategically to sections. Use the persona-selection-guide to
   choose based on these specific lyrics, not a formula."
   ```
5. **Follow**: `workflows/song-creation-workflow.md` → Advanced Workflow
6. **Iterate Systematically**: A/B testing, sectional optimization

**Expected Time:** 8+ hours for commercial-quality production

---

## 🤖 Working with Claude Code

### What Claude Can Do

Claude will help you:
1. **Generate Complete Songs** from your concepts
2. **Apply Suno Best Practices** automatically
3. **Format Lyrics Properly** with tags and emphasis
4. **Create Optimized Style Prompts** (4-7 descriptors)
5. **Suggest Iterations** based on what didn't work
6. **Match Personas to Lyrics** for multi-singer songs
7. **Troubleshoot Issues** when results aren't right

### Sample Claude Conversation

**You:**
```
"I want to create an empowerment anthem about overcoming self-doubt.
It should start vulnerable and build to a powerful, confident ending.
Genre: Pop with electronic elements. What personas should I use?"
```

**Claude:**
```
Based on your lyrics' emotional journey (vulnerable → powerful), I recommend:

PERSONAS: PHOENIX + NEON (skip REBEL - no rap needed)
- PHOENIX: Power for main message (70%)
- NEON: Vulnerability in verses/bridge (30%)

Structure:
Verse 1 (NEON soft): Doubting, uncertain
Pre-Chorus (NEON → PHOENIX): Building confidence
Chorus (PHOENIX powerful): "I AM ENOUGH!"
Verse 2 (NEON → PHOENIX): Gaining strength
Bridge (NEON vulnerable): Last moment of doubt
Final Chorus (PHOENIX + NEON): Unified, triumphant

Style Prompt:
Pop, Electronic, empowering journey, PHOENIX powerful female lead,
NEON vulnerable male bridge, synth pads, building drums, 125 BPM,
C major, glossy production

[Complete formatted lyrics follow...]
```

### Iteration with Claude

**You:**
```
"The chorus isn't powerful enough. How can I make it hit harder?"
```

**Claude:**
```
Try these changes:
1. Use ALL CAPS on key words: "I AM ENOUGH! I AM STRONG!"
2. Add vocal runs: "I'm stro-o-o-ong!"
3. Include sound effect: *bass drop* before chorus
4. Update style prompt: add "explosive choruses, anthemic"
5. Add emphasis in formatting: (PHOENIX POWERFUL: lyrics)

Updated chorus section:
[Shows revised version with changes]
```

---

## 🎵 Key Principles (From the Guides)

### The 4-7 Descriptor Rule
```
❌ Too vague: "Good pop song"
❌ Too many: "Pop, rock, jazz, blues, happy, sad, fast, slow, loud, quiet..."
✅ Perfect: "Pop, upbeat, synth-heavy, catchy female vocals, 125 BPM, major key"
```

### Always Use Structure Tags
```
❌ Without tags: "First verse lyrics... Chorus lyrics..."
✅ With tags: "[Verse 1] First verse lyrics... [Chorus] Chorus lyrics..."
```

### Format for Effect
```
CAPS = Power/Volume
ellipses... = Slow pacing
Lo-o-o-ng = Sustained notes
! = Energy/Excitement
*asterisks* = Sound effects
(parentheses) = Performance directions
```

### The 6+ Variations Rule
- Same prompt = different results (AI randomization)
- Professional creators generate 6-15 variations
- Don't settle for first result
- Track what works in iteration notes

### Persona Selection Based on Lyrics
- No rap content? Don't use REBEL
- Simple song? Use 1-2 personas, not 3
- Conversation/duet? Use 2 distinct voices
- Match personas to YOUR specific lyrics and theme
- See `personas/persona-selection-guide.md` for detailed matching

---

## 🔍 Common Issues & Quick Fixes

### "Output doesn't match my style prompt"
- **Fix**: Add "no [unwanted element]" to style prompt
- **Example**: "no rock, no acoustic" for pure electronic

### "Vocals aren't right"
- **Fix**: Be more specific in vocal description
- **Change**: "female vocals" → "powerful belting female vocals, emotional runs"

### "Song is too repetitive"
- **Fix**: Use `[Verse 2]` not `[Verse]` for second verse
- **Add**: `[Bridge]` for contrast

### "Chorus isn't catchy enough"
- **Fix**: Use CAPS on key phrases
- **Add**: Vocal runs "lo-o-o-ve"
- **Include**: Repetition and "Oooh" / "Ahhh"

### "Can't get right accent/region"
- **Fix**: Add regional markers to style prompt
- **Example**: "Memphis trap", "West Coast hip-hop", "Vermont storytelling"

### "Multi-singer voices blend together"
- **Fix**: Make persona descriptions MORE different
- **Add**: Strategic placement - don't use all personas everywhere
- **Check**: `personas/persona-selection-guide.md` → Red Flags section

---

## 📖 Recommended Learning Path

### Week 1: Foundations
1. Create 3-5 simple pop songs using pop template
2. Study "Neon Hearts" example
3. Practice formatting and structure tags
4. Learn the 4-7 descriptor rule

### Week 2: Genre Exploration
1. Try 2-3 different genre templates
2. Study corresponding examples
3. Understand genre-specific formatting
4. Learn instrumentation specifications

### Week 3: Iteration & Refinement
1. Follow Standard Workflow for one song
2. Generate 10+ variations, track patterns
3. Use Replace Section for refinement
4. Study what makes versions successful

### Week 4: Advanced Techniques
1. Attempt first multi-singer song
2. Use persona-selection-guide for YOUR lyrics
3. Apply advanced formatting techniques
4. Aim for commercial-quality production

---

## 💡 Pro Tips

1. **Start Simple**: Master single-singer pop before multi-singer complexity
2. **Copy & Modify**: Use example songs as starting templates
3. **Track Success**: Document what works in iteration notes
4. **Generate Off-Peak**: 3-4 AM local time for better quality (community tip)
5. **Be Specific**: Vague prompts = generic results
6. **Use Negative Descriptors**: Tell Suno what NOT to include
7. **Let Lyrics Guide Personas**: Don't force formula if it doesn't fit your content
8. **Iterate Systematically**: Change one thing at a time to isolate improvements
9. **Study the Guides**: The reference docs have deep knowledge
10. **Have Fun**: Experimentation leads to discovery

---

## 🎓 Next Steps

After your first successful song:

1. **Document Your Process**: What worked? Add to iteration notes
2. **Try Another Genre**: Expand your skills
3. **Experiment with Personas**: Multi-singer songs (if ready)
4. **Share & Learn**: Community feedback helps improvement
5. **Build Your Library**: Create reusable style prompts for your signature sound

---

## 📞 Quick Reference

| I Want To... | Go Here |
|--------------|---------|
| Create my first song | `templates/pop/pop-template.md` |
| See complete examples | `examples/example-songs.md` |
| Understand multi-singer | `personas/persona-selection-guide.md` |
| Learn the full workflow | `workflows/song-creation-workflow.md` |
| Deep dive into technique | `reference/Mastering Suno AI...md` |
| Match personas to my lyrics | `personas/persona-selection-guide.md` |
| Troubleshoot issues | This doc → Common Issues section |

---

## ✨ You're Ready!

Pick a template, ask Claude to create a song, and start generating!

**Remember:**
- Keep it simple at first
- Generate 6+ variations
- Let your lyrics guide persona choices
- Track what works
- Have fun creating!

---

**Version**: 1.0
**Difficulty**: All Levels (Beginner → Advanced)
**Time to First Song**: 30-90 minutes
**System**: Claude Code + Suno AI
