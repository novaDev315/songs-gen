# Song Creation Workflow Guide
## Complete Guide to Creating Songs with Suno AI and Claude Code

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Recommended Models**: Suno V4.5, V5 (for best results)

---

## Table of Contents
1. [Quick Start Workflow](#quick-start-workflow-5-steps)
2. [Standard Workflow](#standard-workflow-detailed-10-step-process)
3. [Advanced Workflow](#advanced-workflow-iteration-and-refinement)
4. [Claude Code Integration](#claude-code-integration-guide)
5. [Iteration Strategies](#iteration-strategies)
6. [Quality Checklist](#quality-checklist)
7. [Troubleshooting](#troubleshooting-common-issues)

---

## Quick Start Workflow (5 Steps)

### Perfect for: First-time users, simple songs, rapid prototyping

### Step 1: Choose Your Foundation (5 minutes)
```bash
# Pick a template based on your genre
Pop → templates/pop/pop-template.md
Hip-Hop → templates/hip-hop/hip-hop-template.md
Multi-Singer → templates/multi-singer/multi-singer-template.md
```

**Quick decision guide:**
- Want catchy, radio-ready? → **Pop**
- Want rap/flow-focused? → **Hip-Hop**
- Want multiple voices/personas? → **Multi-Singer**

### Step 2: Define Your Concept (10 minutes)
Answer these 4 questions:
1. **Theme**: What's your song about? (love, heartbreak, success, adventure)
2. **Mood**: How should it feel? (upbeat, melancholic, aggressive, dreamy)
3. **Style**: What genre/subgenre? (dance-pop, trap, synth-pop, boom bap)
4. **Speed**: Fast or slow? (120 BPM = moderate, 140 = fast, 90 = slow)

**Example:**
```
Theme: Overcoming obstacles
Mood: Confident and energetic
Style: Trap with pop hooks
Speed: 140 BPM (fast)
```

### Step 3: Create Your Style Prompt (15 minutes)
Use the **4-7 descriptor rule**:

```
[PRIMARY GENRE], [SUBGENRE/MOOD], [VOCAL STYLE],
[INSTRUMENTATION], [PRODUCTION], [BPM], [NEGATIVE DESCRIPTORS]
```

**Good example:**
```
Trap, confident and energetic, powerful female vocals,
808 bass, hi-hat rolls, glossy production, 140 BPM, no rock
```

**Bad example (too vague):**
```
Make a good trap song
```

### Step 4: Write Your Lyrics (30 minutes)
Follow the template structure with these formatting rules:

**Structure tags are mandatory:**
```
[Intro]
[Verse 1]
[Pre-Chorus]
[Chorus]
[Verse 2]
[Chorus]
[Bridge]
[Final Chorus]
[Outro]
```

**Formatting for emphasis:**
- `CAPS` = Louder/powerful delivery
- `ellipses...` = Slower pacing
- `!` = Energy/excitement
- `Lo-o-o-ng` = Sustained notes
- `(whispered: "text")` = Performance cues
- `*bass drop*` = Sound effects

### Step 5: Generate and Evaluate (20 minutes)
1. Go to Suno AI (suno.com)
2. Use **Custom Mode** (not Simple Mode)
3. Paste your style prompt in Style field
4. Paste your lyrics in Lyrics field
5. Click Generate
6. Wait 2-3 minutes for 2 versions
7. **Generate 6+ variations** (AI is random, need multiple attempts)

**Evaluation criteria:**
- Does it match your mood/theme?
- Are the vocals clear and fitting?
- Does the structure flow well?
- Any pronunciation issues?

**Total Time: ~90 minutes**

---

## Standard Workflow (Detailed 10-Step Process)

### Perfect for: Serious projects, original songs, commercial releases

### Step 1: Research and Inspiration (15-30 minutes)

**Define your vision clearly:**
```
Song Concept Template:
- Title: [Working title]
- Theme/Story: [What's the song about?]
- Emotional Arc: [How should listener feel? Start → Middle → End]
- Target Audience: [Who is this for?]
- Reference Artists: [Describe their style, don't name directly]
- Unique Elements: [What makes this special?]
```

**Example filled out:**
```
Song Concept:
- Title: "Midnight Voltage"
- Theme: Finding energy and connection in urban nightlife
- Emotional Arc: Introspective → Building excitement → Euphoric
- Target Audience: Young adults, club/festival listeners
- Reference Style: Uplifting electro-pop with atmospheric synths,
  anthemic melodies, emotional vocals, 103 BPM style
- Unique Elements: Contrast between intimate verses and explosive choruses,
  rap breakdown for modern edge
```

### Step 2: Genre and Template Selection (10 minutes)

**Primary genres Suno excels at:**
- ✅ Pop (all subgenres)
- ✅ Electronic/EDM (house, trap, synth-pop, dubstep)
- ✅ Hip-Hop/Trap
- ✅ Country/Folk
- ✅ Jazz (especially 1920s-1950s with female vocals)
- ✅ Indie
- ⚠️ Rock (specify guitar types clearly)
- ⚠️ Metal (use strong negative descriptors: "no pop")

**Choose your template and make a copy:**
```bash
# Copy template to your working file
cp templates/[genre]/[genre]-template.md generated/my-song.md
```

### Step 3: Craft Your Style Prompt (30-45 minutes)

**The Taxonomic Approach (recommended):**
List elements from broad to specific, with **first genre having most influence**.

```
Structure:
1. Primary Genre (most influence)
2. Secondary Genre/Subgenre
3. Emotional Descriptors
4. Vocal Style (specific)
5. Instrumentation (2-4 key instruments)
6. Production Style
7. Tempo/BPM
8. Key (optional but helpful)
9. Negative Descriptors (what to avoid)
```

**Examples by complexity:**

**Simple (4 descriptors - minimum):**
```
Indie-folk, raw male vocals, acoustic guitar, fast-paced
```

**Standard (6 descriptors - recommended):**
```
Synth-Pop, Dream Pop, futuristic love theme, ethereal powerful female vocals,
retro synths, modern drums, 122 BPM, nostalgic future vibe, no acoustic
```

**Advanced (7+ descriptors - for complex productions):**
```
Electronic, Electro-Pop, mysterious and dreamy, sweet female voice,
eerie atmosphere, melodic composition, sub-bass, atmospheric synths,
wide stereo imaging, sidechain compression, 115 BPM, A minor, no rock elements
```

**Pro techniques:**
- **Comma-separated** = Distinct layers (recommended)
- **No commas** = Blended fusion ("stoner space rock shoegaze")
- **Repeat 3x for difficult genres**: "Drum and bass, drum and bass, drum and bass, fast breakbeats..."
- **Artist-inspired anchoring**: Describe characteristics, not names
- **Decade specifications**: "80s synth-pop", "90s grunge", "2000s indie"
- **Regional markers**: "Memphis trap", "Atlanta trap", "Vermont storytelling"

### Step 4: Structure Your Song (20-30 minutes)

**Standard pop structure (safe choice):**
```
[Intro] (4-8 bars instrumental)
[Verse 1] (16 bars)
[Pre-Chorus] (8 bars)
[Chorus] (16 bars)
[Verse 2] (16 bars)
[Pre-Chorus] (8 bars)
[Chorus] (16 bars)
[Bridge] (8-16 bars)
[Final Chorus] (16-24 bars with variations)
[Outro] (4-8 bars fade)
```

**Advanced structure options:**
```
[Long Mellow Intro]
[Whispered Verse 1]
[Building Pre-Chorus]
[EXPLOSIVE CHORUS]
[Rap Breakdown]
[Soaring Lead Guitar Solo]
[Emotional Bridge]
[FINAL CHORUS - MAXIMUM ENERGY]
[Fade to End]
```

**Structure tag modifiers you can use:**
- Emotional: Whispered, Gentle, Aggressive, Soaring, Melancholic
- Dynamic: Building, Explosive, Intimate, Maximum Energy
- Instrumental: Lead Guitar Solo, Piano Interlude, Bass Solo
- Ending: Fade to End, Fade Out, Hard Stop

### Step 5: Write Your Lyrics (45-90 minutes)

**Content guidelines:**
- **Verse**: Tell story, establish situation (4-8 lines)
- **Pre-Chorus**: Build tension, setup hook (2-4 lines)
- **Chorus**: Main message, most memorable (4-8 lines)
- **Bridge**: Change perspective or mood (4-8 lines)

**Formatting for Suno interpretation:**

```
EMPHASIS TECHNIQUES:
CAPS = Louder, powerful ("WE ARE UNSTOPPABLE!")
ellipses... = Slower, contemplative ("waiting... for you...")
! = Energy, excitement ("Let's go!")
Extended vowels = Sustained notes ("lo-o-o-o-ove")

VOCAL CUES:
(whispered: "under the moonlight")
(shouted: "RISE UP!")
(building: "getting stronger")
(Background: "yeah yeah yeah")

VOCALIZATIONS (write explicitly):
"Oooooohhh whoaaa ahhhh!"
"Mmmmmmmmm oh..."
"La la la la la"
"Yeah, yeah, uh, let's go!"

SOUND EFFECTS (asterisks):
*bass drop*
*thunder*
*vinyl crackle*
*crowd cheering*
*synth build*
```

**Rhyme scheme options:**
- **AABB** (simple): "stars/scars, zone/alone"
- **ABAB** (standard): "hand/understand/planned/stand"
- **ABCABC** (complex): "back/track/slack/intact/slack/fact"

**Hip-hop specific:**
- Break lines where you want pauses/breathing
- Include regional slang for accent guidance
- Write ad-libs in parentheses: "(yeah!)", "(uh!)", "(skrrrt!)"
- Specify "Phonk Drum" in style for authentic beats

### Step 6: Apply Advanced Formatting (20 minutes)

**Layered formatting example:**
```
[Intro - Long Atmospheric Build]
*synth arpeggio*
[High-fidelity stereo sound with wide spatial imaging]

[Verse 1 - Whispered Female]
(softly: "In the shadows of the city lights...")
Purple rain on windows, looking in...
Lost inside this technological maze
Living life in ultraviolet haze

[Pre-Chorus - Building Intensity]
Close your eyes and meet me there!
In the static of the midnight air!!

[Chorus - EXPLOSIVE POWER]
WE'RE LIVING IN ELECTRIC DREAMS! (dreams!)
Nothing's ever what it seems! (what it seems)
Neon love in laser beams
DANCING THROUGH ELECTRIC DREAMS!!

[Rap Breakdown - Aggressive Female]
Lost in translation, pixel romance (yeah)
Binary emotions, take a chance (chance)
Upload my heart into your drive (upload)
In this matrix, we're alive! (ALIVE!)

[Bridge - Emotional Male]
(soft and vulnerable)
When the power goes out...
And the screens go dark...
(building emotion)
Will you still find me?

[Final Chorus - ALL VOICES MAXIMUM]
WE'RE LIVING IN ELECTRIC DREAMS!!!
(Background: "Dreams! Dreams! Dreams!")
*bass drop*
DANCING THROUGH ELECTRIC DREAMS!!!
```

**Instrumental sections with rhythmic notation:**
```
[Melodic Interlude]
. . . ! . .
. ! . . . !

[Aggressive Solo]
!! . ! !! !
! !! . ! !!
```

### Step 7: Multi-Singer Setup (Optional - Advanced)

**If using multiple personas:**

**The proven PHOENIX/NEON/REBEL formula:**
```
Style Prompt Addition:
PHOENIX powerful female lead vocals, NEON smooth male harmonies,
REBEL edgy female rap section
```

**Lyrics persona assignment:**
```
[Verse 1 - PHOENIX]
[PHOENIX establishes song with power]

[Pre-Chorus - PHOENIX + NEON]
(PHOENIX: Main melody line)
(NEON: Harmony underneath)

[Chorus - PHOENIX lead, NEON harmony]
(PHOENIX: WE ARE UNSTOPPABLE!)
(NEON: unstoppable, unstoppable)

[Rap Break - REBEL]
[REBEL brings attitude and edge]

[Bridge - NEON emotional solo]
(NEON soft: "When everything falls apart...")

[Final Chorus - ALL]
(PHOENIX: POWER BELT!)
(NEON: High harmonies!)
(REBEL: Yeah! Let's go!)
```

**Distribution percentages:**
- **Pop**: PHOENIX 60%, NEON 25%, REBEL 15%
- **Hip-Hop Pop**: REBEL 50%, PHOENIX 30%, NEON 20%
- **EDM**: PHOENIX 40%, NEON 30%, REBEL 30%

### Step 8: Generation Strategy (30-60 minutes)

**Optimal generation approach:**

1. **Test with short clips first** (15-30 seconds)
   - Verify style before committing to full song
   - Saves credits on experimentation

2. **Generate during off-peak hours**
   - 3:00-4:30 AM local timezone = better quality
   - Less server load = more computational resources

3. **Generate 6+ variations**
   - AI seed randomization = different results each time
   - Exceptional results appear unexpectedly
   - Don't settle for first attempt

4. **Use Custom Mode exclusively**
   - Simple Mode = quick experiments only
   - Custom Mode = superior control

5. **Track your generations:**
   ```
   Generation Log:
   1. [Time] - Style tweaks: [notes] - Result: [rating]
   2. [Time] - Lyrics variation: [notes] - Result: [rating]
   3. [Time] - Changed BPM from 120→125 - Result: [rating]
   ...
   Best: Generation #[X] - [Why it worked]
   ```

### Step 9: Evaluation and Selection (20 minutes)

**Quality assessment criteria:**

**Audio Quality (40%):**
- [ ] Clear vocals without distortion
- [ ] Balanced mix (vocals not drowned by instruments)
- [ ] Good stereo imaging
- [ ] Professional production quality

**Creative Execution (40%):**
- [ ] Matches intended mood/theme
- [ ] Structure flows logically
- [ ] Dynamics (quiet/loud variation)
- [ ] Hook is memorable and catchy

**Technical Accuracy (20%):**
- [ ] Correct genre interpretation
- [ ] Proper pronunciation
- [ ] Tempo/BPM feels right
- [ ] No awkward transitions

**Thumbnail quality tip**: Best-looking thumbnails often correlate with best audio quality

### Step 10: Documentation and Archiving (10 minutes)

**Save your work:**
```
generated/my-song-v1.md:
- Final style prompt
- Final lyrics
- Generation notes
- Suno link
- What worked / what didn't
- Lessons learned
```

**Build your knowledge base:**
- Track successful prompt patterns
- Note model versions used (V4, V4.5, V5)
- Record persona combinations that worked
- Save for future reference and iteration

**Total Time: 4-6 hours for polished result**

---

## Advanced Workflow (Iteration and Refinement)

### Perfect for: Professional projects, album tracks, commercial releases

### The 6-Take Minimum Rule

**Why 6+ variations are essential:**
- Suno applies different random seeds each generation
- Identical prompts yield varying results
- Exceptional quality appears unpredictably
- Need statistical sample to find the best

**Systematic variation approach:**
1. Generate 2 with exact same prompt (baseline)
2. Generate 2 with slight style variations
3. Generate 2 with slight lyric variations
4. Compare and identify best elements
5. Combine best elements in new generation
6. Repeat until satisfied

### The Modular Testing Approach

**Test ONE component at a time:**

```
Test 1: Genre variations (keep mood/instruments constant)
- Synth-Pop → Electro-Pop → Dream Pop
- Track which genre interpretation works best

Test 2: Instrumentation variations (keep genre/mood constant)
- "retro synths" → "analog synthesizers" → "modern digital synths"
- Track which instruments sound best

Test 3: Vocal variations (keep everything else constant)
- "powerful female vocals" → "ethereal female vocals" → "sultry female vocals"
- Track which vocal style fits best

Test 4: BPM variations (keep style constant)
- 115 BPM → 120 BPM → 125 BPM
- Track which tempo feels right
```

**Document your findings:**
```
Component Test Results:
Genre: "Electro-Pop" > "Synth-Pop" > "Dream Pop"
Instruments: "analog synthesizers" worked best
Vocals: "ethereal" perfect for verses, "powerful" for chorus
BPM: 122 BPM is the sweet spot

Final optimal combination: Electro-Pop, ethereal-to-powerful vocals,
analog synthesizers, 122 BPM
```

### The Refinement Ladder

**Build complexity incrementally:**

```
Pass 1 - Foundation (simple):
"Electro-Pop, dreamy"

Pass 2 - Add instrumentation:
"Electro-Pop, dreamy, retro synths, modern drums"

Pass 3 - Add specificity:
"Electro-Pop, Dream Pop, futuristic romance, retro synths, modern drums, 122 BPM"

Pass 4 - Add production details:
"Electro-Pop, Dream Pop, futuristic romance, ethereal female vocals,
retro synths, modern drums, sidechain compression, 122 BPM, A minor"

Pass 5 - Add negatives and polish:
"Electro-Pop, Dream Pop, futuristic romance theme, ethereal powerful female vocals,
retro analog synths, modern electronic drums, sidechain compression, wide stereo,
122 BPM, A minor, nostalgic future vibe, no acoustic instruments, no rock"
```

### Replace Section Workflow

**For 90% perfect songs with problem areas:**

1. **Identify problem section**: "Verse 2 sounds off"
2. **Highlight just that section** in Suno
3. **Click "Replace Section"**
4. **Generate 3-5 variations** of just that section
5. **Keep best variation**
6. **Preserve other perfect sections**

**When to use Replace Section:**
- One verse has pronunciation issues
- Bridge doesn't fit the mood
- Chorus energy is too low/high
- Specific lyrics need adjustment

**Don't regenerate entire song if only one section needs work!**

### A/B Testing for Optimization

**Isolate variables scientifically:**

```
Test A: Capitalization impact
Prompt A: "EDM, Dark Ambient, Cinematic"
Prompt B: "EDM, DARK AMBIENT, CINEMATIC"
Result: [Track which sounds better]

Test B: Descriptor order
Prompt A: "Aggressive trap with gospel vocals"
Prompt B: "Gospel-influenced aggressive trap"
Result: [Track which interpretation works better]

Test C: Detail level
Prompt A: "Rock song with guitar"
Prompt B: "Rock song with distorted electric guitar, tight drums, palm-muted riffs"
Result: [Track which has better production]
```

**Build a personal optimization database:**
```
Optimization Database:
- ALL CAPS genres = stronger interpretation
- Comma separation = better than no commas for distinct layers
- First genre listed = 60% influence on final sound
- BPM specification = crucial for tempo accuracy
- Negative descriptors = essential to avoid "pop gravity well"
- Instrumentation detail = directly improves production quality
```

### The Timestamp Seed Technique (Advanced)

**For creating albums with consistent sonic identity:**

1. Generate a track with excellent vocal timbre and production
2. Note the timestamp where best qualities appear (e.g., 2.5 seconds)
3. Use that timestamp as initialization "seed" for new tracks
4. Maintains vocal character and production style
5. Creates cohesive album/EP with unified sound

**Application:**
- Full albums with consistent artist "voice"
- EPs with unified sonic branding
- Multiple songs in same "universe"

### Post-Generation Refinement

**Hybrid AI + Human approach:**

1. **Export stems** using Moises.ai or Lalal.ai
2. **Isolate problem tracks** (usually vocals)
3. **Edit in DAW** (Ableton, Logic, FL Studio)
4. **Fix pronunciation** with manual edits
5. **Adjust timing** of specific phrases
6. **Re-mix** for perfect balance
7. **Master** for final polish

**This hybrid approach achieves quality neither AI nor human alone can reach**

---

## Claude Code Integration Guide

### How to Use Claude Code for Song Creation

Claude Code can assist with every step of the song creation process. Here's how to collaborate effectively:

### Quick Generation Prompts for Claude

**Basic song request:**
```
Create a [genre] song about [theme] with [mood] vibe.
Use the [template name] template.
Target BPM: [number]
Key elements: [list 2-3 key features]
```

**Example:**
```
Create a synth-pop song about futuristic romance with a dreamy,
nostalgic vibe. Use the pop template. Target BPM: 122
Key elements: ethereal vocals, retro synths, contrast between
intimate verses and powerful chorus
```

**Advanced song request with constraints:**
```
Create a multi-singer [genre] song about [theme].

Requirements:
- Theme: [detailed theme]
- Mood arc: [start mood] → [middle mood] → [end mood]
- Personas: PHOENIX for [role], NEON for [role], REBEL for [role]
- Structure: [specific structure]
- Special features: [rap break, key change, etc.]
- BPM: [number]
- Style inspiration: [describe style, not artist names]
- Must avoid: [elements to exclude]
```

### Example Claude Conversation Workflow

**User:**
```
I want to create an electro-pop song about finding connection in a
digital world. It should feel dreamy but also energetic, with a
female lead vocal that starts soft and builds to powerful. Can you
help me structure this using the pop template?
```

**Claude Response Pattern:**
```
I'll help you create this electro-pop song. Let me break this down:

[Analyzes requirements and suggests structure]
[Creates style prompt with 4-7 descriptors]
[Writes lyrics with proper formatting]
[Explains choices and formatting techniques used]
[Provides generation tips]
```

**User (iterating):**
```
This is great! Can you make the rap breakdown more aggressive and
add a vulnerable bridge with a male vocal? Also increase the BPM
to 128 for more energy.
```

**Claude Response Pattern:**
```
I'll modify the song with those changes:

[Updates style prompt to include male vocal for bridge]
[Rewrites rap breakdown with more aggressive tone]
[Adds vulnerable male bridge section]
[Updates BPM to 128]
[Notes what changed and why]
```

### Specific Claude Prompt Templates

**For brainstorming:**
```
Help me brainstorm song concepts for [genre] about [general theme].
I want something that feels [mood] and targets [audience].
Give me 5 different angles or approaches.
```

**For style prompt refinement:**
```
Review this style prompt and suggest improvements:
[paste your style prompt]

Criteria:
- Does it follow the 4-7 descriptor rule?
- Are there conflicting elements?
- Could it be more specific?
- Will it avoid the "pop gravity well"?
```

**For lyric improvement:**
```
Review these lyrics for Suno AI optimization:
[paste your lyrics]

Check for:
- Proper structure tags [Verse], [Chorus], etc.
- Formatting for emphasis (CAPS, ellipses, !)
- Performance cues and directions
- Rhythm and flow
- Memorable hook quality
```

**For multi-singer orchestration:**
```
Convert this single-singer song to a multi-singer version using
PHOENIX/NEON/REBEL:

[paste single-singer version]

Follow these guidelines:
- PHOENIX should dominate at 60%
- NEON for harmonies and bridge
- REBEL for rap break
- Build energy: solo → duet → trio
```

**For troubleshooting:**
```
I generated this song but [specific problem].
Style prompt: [paste prompt]
Problem section: [paste lyrics section]

What should I change to fix this?
```

### Claude Code Commands for This Project

**Using this repository with Claude:**

```bash
# To create a new song
"Create a new [genre] song about [theme] in generated/[song-name].md"

# To iterate on existing song
"Improve the song at generated/[song-name].md by [specific changes]"

# To create variations
"Create 3 variations of generated/[song-name].md testing different
[genre/mood/tempo/etc] options"

# To convert between formats
"Convert generated/[song-name].md from single-singer to multi-singer
using PHOENIX/NEON/REBEL"

# To analyze and optimize
"Analyze generated/[song-name].md and suggest optimizations for
better Suno AI generation"
```

### What Claude Can Help With

**✅ Claude excels at:**
- Creating initial song concepts and structure
- Writing lyrics with proper formatting
- Crafting detailed style prompts
- Generating variations and iterations
- Converting between single/multi-singer formats
- Analyzing and optimizing existing songs
- Explaining why certain techniques work
- Providing genre-specific guidance
- Troubleshooting generation issues

**⚠️ Claude cannot:**
- Actually generate the audio (that's Suno AI's job)
- Listen to results and provide audio feedback
- Know your personal taste preferences
- Predict exact Suno AI behavior (it's random)

**Best practice: Use Claude for planning and structure, Suno for audio generation**

---

## Iteration Strategies

### Strategy 1: The Progressive Refinement Method

**Start broad, narrow down:**

```
Round 1: Test 3 genre variations
→ "Synth-Pop" vs "Electro-Pop" vs "Dream Pop"
→ Pick best: "Electro-Pop"

Round 2: Test 3 mood variations with winning genre
→ "dreamy" vs "energetic" vs "mysterious"
→ Pick best: "dreamy with energetic chorus"

Round 3: Test 3 vocal styles with winners
→ "ethereal" vs "powerful" vs "sultry"
→ Pick best: "ethereal verses, powerful chorus"

Round 4: Test 3 instrumentation combos
→ "retro synths, modern drums" vs "analog synths, acoustic drums" vs "digital synths, electronic drums"
→ Pick best: "analog synths, modern drums"

Round 5: Final polish with all winners combined
→ Generate 6 variations of optimal combination
→ Select THE ONE
```

**Total: ~21 generations, systematic optimization**

### Strategy 2: The A/B Comparison Method

**Side-by-side testing:**

```
Create Matched Pairs:
Pair 1: Differs only in BPM
- Version A: 120 BPM
- Version B: 125 BPM
- Winner: [Select based on energy]

Pair 2: Differs only in vocal style
- Version A: "powerful female vocals"
- Version B: "ethereal female vocals"
- Winner: [Select based on fit]

Pair 3: Differs only in production
- Version A: "glossy production"
- Version B: "lo-fi aesthetic"
- Winner: [Select based on vibe]

Final: Combine all winners
```

**Total: ~8-12 generations, efficient comparison**

### Strategy 3: The Sectional Optimization Method

**Perfect each section independently:**

```
Phase 1: Optimize Intro
- Generate 4 variations of intro only (15-30 sec clips)
- Select best intro

Phase 2: Optimize Verse 1
- Generate 4 variations of verse 1
- Select best verse 1

Phase 3: Optimize Chorus
- Generate 6 variations of chorus (most important!)
- Select best chorus

Phase 4: Optimize other sections
- Bridge, Verse 2, etc.

Phase 5: Combine best sections
- Use Replace Section to build perfect song from best parts
```

**Total: ~20-25 generations, highest quality potential**

### Strategy 4: The Rapid Variation Method

**For when you need lots of options fast:**

```
Generate 10 variations with:
- Same style prompt
- Same core lyrics
- Small random elements (different ad-libs, slight word changes)

Then:
- Quick-listen to all 10
- Shortlist top 3
- Deep-listen to top 3
- Select winner
- Generate 3 more similar to winner
- Final selection
```

**Total: ~13 generations, fast creative exploration**

### Tracking Success Patterns

**Build a personal database:**

```markdown
# My Successful Patterns

## Style Prompts That Work
1. "Electro-Pop, Dream Pop, [mood], ethereal powerful female, retro synths, 122 BPM, no acoustic"
   - Used in: Song A, Song C
   - Success rate: 85%
   - Best for: Dreamy, energetic pop

2. "Trap, Atlanta trap, confident flow, 808 bass, hi-hat rolls, 140 BPM, Phonk Drum"
   - Used in: Song B, Song D
   - Success rate: 90%
   - Best for: High-energy hip-hop

## Formatting Techniques That Work
- Building structure: lowercase verse → Normal pre-chorus → CAPS chorus
- Performance cues: (soft: ), (building: ), (POWER: )
- Sound effects: *bass drop* at chorus start = energy boost

## Persona Combinations That Work
- PHOENIX 60% + NEON 25% + REBEL 15% = perfect pop blend
- REBEL 50% + PHOENIX 30% + NEON 20% = great hip-hop pop

## BPM Sweet Spots by Genre
- Pop: 120-125 BPM
- Trap: 135-145 BPM
- EDM: 125-130 BPM
- Ballad: 70-85 BPM
```

### When to Stop Iterating

**Quality indicators that mean you're done:**
- [ ] Song matches your original vision 90%+
- [ ] Hook is immediately memorable
- [ ] No pronunciation or technical issues
- [ ] Professional mix quality
- [ ] Emotional impact is strong
- [ ] Friends/test audience give positive feedback
- [ ] You've found yourself humming it later
- [ ] Multiple generations haven't improved it further

**Don't over-iterate**: After 20+ generations with no improvement, you've probably found the best version

---

## Quality Checklist

### Pre-Generation Checklist

**Before clicking generate, verify:**

**Style Prompt:**
- [ ] 4-7 descriptors (not too few, not too many)
- [ ] Primary genre listed first
- [ ] Specific vocal style described
- [ ] Key instrumentation mentioned (2-4 instruments)
- [ ] BPM specified
- [ ] Mood/emotion clear
- [ ] Production style noted
- [ ] Negative descriptors included ("no pop", "no rock")
- [ ] Under 1000 characters (for V4.5+) or 200 (for V3.5/V4)

**Lyrics Structure:**
- [ ] All sections have [Tags]
- [ ] Structure flows logically (Intro→Verse→Chorus→etc)
- [ ] Tag modifiers used where appropriate [Whispered Verse], [EXPLOSIVE CHORUS]
- [ ] Under 5000 characters (V4.5+) or 3000 (V3.5/V4)

**Lyrics Formatting:**
- [ ] CAPS used for emphasis on key words/phrases
- [ ] Ellipses... used for slow/contemplative sections
- [ ] ! marks for energy/excitement
- [ ] Extended vowels for sustained notes (lo-o-o-ve)
- [ ] Performance cues in parentheses (whispered: ), (shouted: )
- [ ] Sound effects marked with *asterisks*
- [ ] Vocalizations explicitly written ("Oooohhh!", "Yeah!")

**Multi-Singer (if applicable):**
- [ ] All personas described in style prompt
- [ ] Persona assignments clear in lyrics (PHOENIX:, NEON:)
- [ ] 2-3 personas only (not more)
- [ ] Strategic placement (not everyone singing everything)
- [ ] Energy builds through persona additions

**Content Quality:**
- [ ] Theme/message is clear
- [ ] Emotional arc progresses (quiet→loud or happy→sad, etc)
- [ ] Hook is catchy and repeatable
- [ ] Lyrics have rhythm and flow
- [ ] Rhyme scheme is consistent (or intentionally varied)
- [ ] No awkward phrasing or word choices

### Post-Generation Checklist

**After receiving results, evaluate:**

**Technical Quality:**
- [ ] Audio is clear (no distortion/artifacts)
- [ ] Vocals are prominent and understandable
- [ ] Mix is balanced (instruments don't drown vocals)
- [ ] Tempo matches your BPM specification
- [ ] No pronunciation errors
- [ ] Structure follows your tags correctly

**Creative Quality:**
- [ ] Genre interpretation is accurate
- [ ] Mood matches your vision
- [ ] Vocal style fits the song
- [ ] Instrumentation sounds right
- [ ] Energy/dynamics work well
- [ ] Hook is memorable

**Artistic Quality:**
- [ ] Emotional impact is strong
- [ ] Transitions flow smoothly
- [ ] Build-ups and drops land well
- [ ] Overall coherence and polish
- [ ] "Radio-ready" feel (if that's your goal)

**Comparison Quality:**
- [ ] Better than previous generation (if iterating)
- [ ] Best of current batch
- [ ] Worth continuing with (or start over?)

---

## Troubleshooting Common Issues

### Issue 1: "Sounds too generic/poppy even though I specified other genre"

**Cause**: Suno's "pop gravity well" - nearly all genres pull toward pop

**Solutions:**
1. **Use strong negative descriptors**: "no pop", "no pop elements", "no pop production"
2. **Repeat genre 3 times**: "metal, metal, metal" for difficult genres
3. **Use hyphenated fusion names**: "emo-metal" instead of "emo metal"
4. **Add production specifics**: "raw production, no polish" vs "glossy production"
5. **Reference era**: "90s grunge" specifies sound better than just "grunge"

**Example fix:**
```
Before: "Metal, dark, aggressive"
After: "Metal, metal, heavy metal, dark aggressive tone, distorted guitars,
double bass drums, raw production, no pop, no synth, 1990s sound"
```

### Issue 2: "Vocals don't match the style I wanted"

**Cause**: Vague vocal descriptions

**Solutions:**
1. **Be hyper-specific**: Not just "female vocals" but "powerful belting female mezzo-soprano"
2. **Add performance modifiers**: "with emotional runs", "with raw edge", "with sultry tone"
3. **Reference era/style**: "90s R&B style", "operatic", "Broadway-style"
4. **Use persona system**: PHOENIX, NEON, REBEL for consistent results
5. **Add effects if wanted**: "with auto-tune", "with vocoder", "with reverb"

**Example fix:**
```
Before: "female vocals"
After: "powerful female lead vocals, belting mezzo-soprano, emotional runs,
dynamic range from soft whispers to explosive high notes"
```

### Issue 3: "Wrong accent or pronunciation"

**Cause**: Suno's interpretation of text, regional defaults

**Solutions for accent:**
1. **Add regional markers**: "Memphis trap", "Atlanta trap", "West Coast hip-hop"
2. **Include regional slang** in lyrics
3. **Specify accent**: "Southern drawl", "British accent", "New York accent"
4. **Mix with genre that has that accent**: "Hip-hop with country" for Southern accent

**Solutions for pronunciation:**
1. **Hyphenate syllables**: "EL PUEN-TE" instead of "EL PUENTE"
2. **Phonetic spelling**: "Ar-can-jel" instead of "Arcanjel"
3. **Use Replace Section** to regenerate just problem lines
4. **Capitalize for emphasis**: Can help with pronunciation priority

**Example fix:**
```
Before:
Style: "Trap"
Lyrics: "El puente bajo el agua"

After:
Style: "Trap, Memphis trap, Southern flow"
Lyrics: "EL PUEN-TE BA-JO EL A-GUA (yeah!)"
```

### Issue 4: "Structure is jumbled or ignores my tags"

**Cause**: Missing tags, unclear structure, too many custom tags

**Solutions:**
1. **Use standard tags**: [Intro], [Verse], [Chorus], [Bridge], [Outro]
2. **Every section needs a tag**: Don't leave any lyrics without tags
3. **Don't over-customize**: [Whispered Verse] good, [Super Quiet Contemplative Whispered Female Only Verse] bad
4. **Clear line breaks** between sections
5. **Repeat chorus tag**: [Chorus] multiple times, don't assume it knows to repeat

**Example fix:**
```
Before:
Intro music
Verse about love
Chorus hook here
More verses

After:
[Intro]
*synth build*

[Verse 1]
Falling in love under city lights

[Chorus]
WE'RE FLYING HIGH!
```

### Issue 5: "Energy/dynamics are flat"

**Cause**: No dynamic formatting, same energy throughout

**Solutions:**
1. **Use progression formatting**:
   - Verse: lowercase or normal
   - Pre-Chorus: Normal with ! marks
   - Chorus: STRATEGIC CAPS
   - Bridge: back to soft
   - Final Chorus: ALL CAPS
2. **Performance cues**: (whispered), (building), (EXPLOSIVE)
3. **Tag modifiers**: [Gentle Verse], [POWERFUL CHORUS]
4. **Structure builds**: Start intimate, end maximum
5. **Sound effects**: *bass drop* at energy peaks

**Example fix:**
```
Before:
[Verse 1]
WE ARE THE CHAMPIONS
WE WILL WIN

[Chorus]
CHAMPIONS FOREVER

After:
[Verse 1 - Intimate]
(softly: "We started from the bottom...")
Fighting every day to rise above...

[Pre-Chorus - Building]
Feel the power growing!
Getting stronger!!

[Chorus - EXPLOSIVE]
(POWER: "WE ARE THE CHAMPIONS!")
WE WILL WIN!!!

[Bridge - Vulnerable]
(quiet contemplation)
When the lights go out...
Will we still shine...

[Final Chorus - MAXIMUM ENERGY]
WE ARE THE CHAMPIONS!!!
*crowd roaring*
WE WILL WIN FOREVER!!!
```

### Issue 6: "Repetitive or boring chorus"

**Cause**: V4.5 repetition issue, lack of variation

**Solutions:**
1. **Add variations each time chorus appears**:
   ```
   [Chorus]
   Main hook line

   [Chorus - Bigger]
   Main hook line
   (Background: "yeah yeah yeah")

   [Final Chorus]
   Main hook line
   (ALL: Extended "Oooohhh!")
   MAIN HOOK LINE CAPS!
   ```
2. **Add ad-libs and vocalizations** to later choruses
3. **Change instrumentation** via tags: [Chorus - Stripped], [Final Chorus - Full Band]
4. **Layer vocals**: Add harmonies, background vocals in later versions
5. **Use Replace Section** to create variations if needed

### Issue 7: "Multi-singer personas blend together/can't distinguish"

**Cause**: Not enough contrast, all singing everything

**Solutions:**
1. **Strategic placement**: Each persona gets showcase moments
2. **Performance modifiers**: (PHOENIX powerful), (NEON soft), (REBEL aggressive)
3. **Different sections**: PHOENIX verses, REBEL rap, NEON bridge
4. **Clear contrast**: Don't have soft and aggressive simultaneously
5. **Build through personas**: Start solo → duet → all three
6. **Limit to 2-3 personas**: More = muddy

**Example fix:**
```
Before:
[Chorus]
(PHOENIX, NEON, REBEL: We are together!)

After:
[Chorus]
(PHOENIX power lead: WE ARE TOGETHER!)
(NEON soft harmony: together, together)
(REBEL hype ad-libs: Yeah! Let's go!)
```

### Issue 8: "Not enough bass/specific instrument missing"

**Cause**: Didn't specify instrument explicitly

**Solutions:**
1. **Name it in style prompt**: "808 bass", "sub-bass", "bass guitar"
2. **Add production terms**: "heavy bassline", "bass-heavy mix"
3. **Genre includes it**: "Trap" implies 808s, "Dubstep" implies wobble bass
4. **Tag it in lyrics**: [Bass Drop], [808 Hit]
5. **Sound effects**: *bass drop*, *808 hit*

**Example fix:**
```
Before: "Trap, energetic, 140 BPM"
After: "Trap, heavy 808 bass, sub-bass emphasis, bass-heavy mix, 140 BPM"
```

### Issue 9: "Generated different length than expected"

**Cause**: Suno decides length based on content

**Solutions:**
1. **Use Extend feature** if too short
2. **Use Crop feature** if too long
3. **Specify in tags**: [Long Intro], [Extended Outro]
4. **More sections = longer**: Add [Verse 3], [Interlude], etc.
5. **Fewer sections = shorter**: Skip bridge, shorten verses

### Issue 10: "Used all my credits, still not satisfied"

**Cause**: Inefficient iteration, not tracking what works

**Prevention strategies:**
1. **Test with short clips first** (15-30 sec)
2. **Use Replace Section** not full regeneration
3. **Track what works** in a document
4. **Batch testing**: Test multiple variables in one generation session
5. **Study examples** before generating
6. **Plan more, generate less**

**Credit efficiency workflow:**
1. Short clip test (2 credits)
2. If good, full song (5 credits)
3. Replace problem section only (3 credits)
4. Final version (5 credits)
5. Total: ~15 credits vs 50+ for trial-and-error

---

## Quick Reference Cards

### The 4-7 Descriptor Formula
```
[PRIMARY GENRE], [SUBGENRE/MOOD], [VOCAL STYLE],
[INSTRUMENTATION], [PRODUCTION], [BPM], [NEGATIVES]

Example:
Synth-Pop, Dream Pop, nostalgic romance, ethereal powerful female,
retro synths, modern drums, 122 BPM, no acoustic
```

### Essential Formatting Quick Guide
```
CAPS = Louder/powerful
ellipses... = Slower pacing
! = Energy/excitement
Lo-o-o-ng = Sustained notes
(whispered: ) = Performance cue
*bass drop* = Sound effect
[Verse] = Structure tag
```

### Multi-Singer Quick Formula
```
PHOENIX (Power) + NEON (Smooth) + REBEL (Edge) = Hit
Distribution: 60% / 25% / 15% for pop
Energy Arc: Solo → Duet → Trio → Solo → All
```

### Standard Song Structure
```
[Intro] → [Verse 1] → [Pre-Chorus] → [Chorus] →
[Verse 2] → [Pre-Chorus] → [Chorus] → [Bridge] →
[Final Chorus] → [Outro]
```

### Generation Workflow
```
1. Define concept (theme, mood, style)
2. Write style prompt (4-7 descriptors)
3. Structure song with tags
4. Write and format lyrics
5. Generate 6+ variations
6. Evaluate and select best
7. Iterate with Replace Section if needed
8. Document what worked
```

---

## Final Tips for Success

1. **Patience is key**: First generation is rarely the best
2. **Document everything**: Track what works for future songs
3. **Use Custom Mode**: Always, for serious work
4. **Generate during off-peak**: 3-4 AM local time
5. **6+ variations minimum**: Account for randomness
6. **Test short first**: Save credits, verify style
7. **Replace not regenerate**: Fix sections, not whole songs
8. **Study examples**: Learn from successful songs
9. **Build a library**: Templates, prompts, personas that work for you
10. **Iterate systematically**: Change one thing at a time

**Remember**: Suno AI is a creative collaborator, not a magic button. Success comes from:
- Clear vision and planning
- Specific, detailed prompts
- Systematic iteration
- Learning from each generation
- Combining AI generation with human curation

**Happy creating! 🎵**

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Maintained by**: Songs-Gen Project
**For**: Suno AI V3.5, V4, V4.5, V5
**License**: Open for personal and commercial use
