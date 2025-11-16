# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Repository Purpose

This is a **song generation system** for creating AI-generated music with Suno AI. The repository contains templates, guides, and workflows to help users (and Claude) create professional-quality song lyrics and style prompts optimized for Suno AI's music generation platform.

## Core Workflow: Song Creation with Claude

When users ask you to create songs, follow this process:

### 1. Analyze the Request

Determine:
- **Genre**: Pop, hip-hop, EDM, rock, country, jazz, or multi-singer
- **Theme/Topic**: What the song is about
- **Mood/Energy**: Emotional tone and energy level
- **Rap Content**: Is there rap? How much?
- **Vocal Style**: Single voice or multi-singer?

### 2. Choose Template & Personas

**For Single-Singer Songs:**
- Use genre-specific template from `templates/[genre]/[genre]-template.md`
- One consistent voice throughout

**For Multi-Singer Songs:**
- Use `templates/multi-singer/multi-singer-template.md`
- **CRITICAL**: Read `personas/persona-selection-guide.md` to match personas to the user's specific lyrics
- **DO NOT default to PHOENIX+NEON+REBEL formula** unless it fits the content
- Match personas based on:
  - Rap content (no rap = no REBEL)
  - Emotional journey (vulnerable = NEON, powerful = PHOENIX)
  - Theme (storytelling = single voice or duet)
  - Energy level (party = all three, intimate = 1-2)

### 3. Generate Song Components

Create two parts:

**Style Prompt (200-1000 characters for Suno's "Style of Music" field):**
```
[GENRE], [subgenre], [mood], [vocal style], [instrumentation], [BPM], [key]
```
- **4-7 descriptors rule**: Not too few, not too many
- Include "no [unwanted element]" to avoid style drift
- For multi-singer: Include persona descriptions: "PHOENIX powerful female vocals, NEON smooth male harmonies, REBEL edgy rap"

**Formatted Lyrics (3000-5000 characters for Suno's "Lyrics" field):**
- Use structure tags: `[Verse 1]`, `[Chorus]`, `[Bridge]`, `[Outro]`
- Apply formatting:
  - `CAPS` = louder/powerful delivery
  - `ellipses...` = slower pacing
  - `Lo-o-o-ng` = sustained notes
  - `!` = energy/excitement
  - `*asterisks*` = sound effects
  - `(parentheses)` = performance directions
  - `(PERSONA: lyrics)` = assign to specific voice (multi-singer only)

### 4. Present Complete Output

Format as:
```markdown
# [Song Title]

## Style Prompt
[Complete style prompt ready to paste into Suno]

## Lyrics
[Complete formatted lyrics ready to paste into Suno]

## Why This Works
[Brief explanation of choices made]

## Generation Tips
- Generate 6+ variations (Suno randomization means different results)
- [Any specific advice for this song]
```

## Key Principles from Reference Guides

### The 4-7 Descriptor Rule
- Too few descriptors = generic output
- Too many descriptors = confused AI
- Sweet spot: 4-7 clear, specific descriptors

### Structure Tags Are Mandatory
Suno needs explicit markers:
- `[Intro]` - Opening (instrumental by default)
- `[Verse]` - Lyrical storytelling
- `[Pre-Chorus]` - Building tension
- `[Chorus]` - Main hook
- `[Bridge]` - Mood shift
- `[Outro]` - Conclusion

Can modify with descriptors: `[Whispered Verse]`, `[Powerful Chorus]`, `[Guitar Solo]`

### Formatting Controls Vocal Delivery
- **Capitalization hierarchy**:
  - `ALL CAPS` = Highest priority, loudest
  - `Title Case` = Secondary emphasis
  - `lowercase` = Tertiary/background
- **Punctuation affects pacing**:
  - Ellipses create slower delivery
  - Exclamation marks add urgency
  - Extended vowels produce sustained notes

### The 6+ Variations Rule
Always remind users to generate **at least 6 variations** in Suno. Same prompt = different results due to AI randomization.

### Persona Selection Based on Lyrics (Multi-Singer)

**Critical Rule**: Don't force the PHOENIX+NEON+REBEL formula. Choose personas that fit the specific song:

- **No rap content?** → Don't use REBEL
- **Simple song?** → Use 1-2 personas, not 3
- **Intimate/vulnerable?** → NEON or PHOENIX soft
- **Powerful/empowerment?** → PHOENIX lead
- **Conversation/duet?** → 2 distinct voices (PHOENIX + NEON)
- **Party/hype with rap?** → REBEL + PHOENIX
- **Storytelling?** → Often best with single voice

**Reference**: `personas/persona-selection-guide.md` has detailed matching logic by theme, mood, and content.

### Common Suno AI Quirks to Combat

1. **Pop Gravity Well**: Nearly all genres drift toward pop. Combat with "no pop, no synth" in style prompt
2. **Regional Accents**: For hip-hop, specify region: "Memphis trap", "Atlanta trap", "West Coast hip-hop"
3. **Jazz Sweet Spot**: 1920s-1950s jazz with female vocals works best
4. **Instrumental Sections**: Use rhythmic notation: `. . . ! . .` or specify instruments: `[Lead Guitar Solo]`

## Repository Structure

```
docs/
├── templates/      # Genre-specific templates (pop, hip-hop, edm, rock, country, jazz, multi-singer)
├── personas/       # Voice persona library and selection guide
├── reference/      # Comprehensive Suno AI guides (read for deep knowledge)
├── workflows/      # Step-by-step creation processes
├── examples/       # 5 complete example songs with analysis
├── guides/         # User guides (FAQ, troubleshooting)
├── technical/      # Technical documentation (architecture, tools)
└── archive/        # Historical documentation

generated/          # User's created songs (organized by genre) - DATA FILES ONLY
```

## Common User Requests

### "Create a [genre] song about [topic]"
1. Choose appropriate template
2. Analyze theme/mood/energy
3. Select personas if multi-singer (based on content, not formula)
4. Generate style prompt (4-7 descriptors)
5. Write formatted lyrics with structure tags
6. Present complete output

### "Make the chorus more powerful"
- Use `ALL CAPS` on key words
- Add vocal runs: `"lo-o-o-ve"`
- Include sound effects: `*bass drop*`
- Add performance direction: `(PHOENIX POWERFUL: lyrics)`

### "Add a rap verse"
- If single-singer song: Keep same voice, format as rap flow
- If multi-singer: Use REBEL persona for rap section
- Break lines for breathing/pauses
- Include ad-libs: `(yeah! uh! let's go!)`

### "Choose personas for my lyrics"
1. Read their lyrics/concept
2. Analyze: rap content? emotional journey? theme?
3. Reference `personas/persona-selection-guide.md`
4. Match personas to THEIR content, not a formula
5. Explain WHY these personas fit their song

### "The output doesn't match my style"
- Add negative descriptors: "no pop", "no rock", "no acoustic"
- Be more specific in vocal description
- Specify instrumentation in detail
- Include production terms: "glossy production", "lo-fi aesthetic"

## Files to Reference

When creating songs, consider reading:

- **Genre template**: `docs/templates/[genre]/[genre]-template.md` - Structure and formatting for genre
- **Persona selection**: `docs/personas/persona-selection-guide.md` - ALWAYS check this for multi-singer songs
- **Persona library**: `docs/personas/persona-library.md` - Full persona descriptions
- **Examples**: `docs/examples/example-songs.md` - Complete working examples to learn from
- **Master guide**: `docs/reference/Mastering Suno AI Prompt Engineering...md` - Deep knowledge (18KB)
- **Multi-singer guide**: `docs/reference/Suno AI Multi-Singer Song Creation Guide.md` - Multi-voice details

## Important: What NOT to Do

- ❌ Don't use REBEL persona if there's no rap content
- ❌ Don't force PHOENIX+NEON+REBEL formula without analyzing if it fits
- ❌ Don't create vague style prompts like "good pop song"
- ❌ Don't forget structure tags `[Verse]`, `[Chorus]`, etc.
- ❌ Don't use emojis in song lyrics unless explicitly requested
- ❌ Don't skip the "why this works" explanation
- ❌ Don't forget to remind about 6+ variations

## Success Metrics

A good song generation includes:
- ✅ Style prompt with 4-7 specific descriptors
- ✅ All structure tags present and properly formatted
- ✅ Emphasis formatting applied (CAPS, ellipses, !, extended vowels)
- ✅ Sound effects and performance directions included
- ✅ Personas (if multi-singer) matched to lyrical content
- ✅ Ready to paste directly into Suno AI
- ✅ Brief explanation of choices made
- ✅ Reminder about generating 6+ variations

## Pro Tips for Generation

1. **Off-Peak Generation**: Suggest generating 3-4 AM local time (community reports better quality)
2. **Iteration Strategy**: Change ONE element at a time to isolate improvements
3. **Replace Section**: For 90% perfect songs, regenerate only problem sections
4. **Negative Descriptors**: Use "no pop, no rock" etc. to prevent style drift
5. **Regional Specificity**: For hip-hop accents, be very specific about region
6. **Decade Specifications**: "80s synth-pop", "90s grunge" provide instant context
7. **Production Terminology**: Use genre-specific terms (supersaw leads, sidechain compression, wobble bass)

---

## Command-Based Workflow System

This project uses **slash commands** for streamlined development workflows. Available commands are in `.claude/commands/`.

### Available Commands

- **`/implement`** - Complete implementation workflow with adaptive tier selection
  - Tier 1 (Simple): ≤3 files, <30 minutes
  - Tier 2 (Standard): 4-10 files, 30-120 minutes
  - Tier 3 (Complex): >10 files, >120 minutes
  - Automatically detects complexity and recommends tier
  - Uses specialized agents (code-implementer, solution-architect, test-specialist, etc.)

### Using the /implement Command

```bash
# Let it auto-detect complexity
/implement Build the file watcher service for monitoring generated/ folder

# Force a specific tier
/implement [Tier 2] Create FastAPI backend with auth endpoints

# With context from planning
# 1. First create .project/plan.md (optional)
# 2. Then run:
/implement Build Suno integration service
```

The `/implement` command will:
1. Read `AUTOMATION_PIPELINE_PLAN.md` for context
2. Detect complexity and recommend tier
3. Launch appropriate specialized agents
4. Execute implementation with validation
5. Create tests and documentation
6. Report completion with next steps

### Specialized Agents Available

The following agents are configured in `.claude/agents/` for use by workflows:

**Core Implementation Agents:**
- **solution-architect** - System design, architecture decisions, tech stack choices
- **code-implementer** - Write FastAPI, Streamlit, service code with best practices
- **code-reviewer** - Review code quality, security, and maintainability
- **test-specialist** - Create unit, integration, and e2e tests

**Quality & Security Agents:**
- **security-auditor** - Security assessment, vulnerability scanning, compliance
- **database-migration-specialist** - SQLite schema, migrations, data integrity
- **deployment-orchestrator** - Docker setup, deployment pipelines, rollback
- **ui-designer** - Streamlit UI design, mobile responsiveness, accessibility

**When to Use Each Agent:**

```bash
# Architecture & Planning
/implement [solution-architect] Design Suno integration architecture

# Code Implementation
/implement [code-implementer] Build file watcher service

# Code Review
/implement [code-reviewer] Review authentication implementation

# Testing
/implement [test-specialist] Create tests for evaluation service

# Security
/implement [security-auditor] Audit JWT authentication system

# Database
/implement [database-migration-specialist] Create SQLite schema

# Deployment
/implement [deployment-orchestrator] Set up Docker Compose

# UI/UX
/implement [ui-designer] Design mobile-friendly review page
```

The workflow will automatically select and coordinate these agents based on the task.

---

## Automation Pipeline Development

This repository also includes an **automation pipeline** project to streamline the workflow from song creation to YouTube upload. When working on automation features, follow these guidelines:

### Project Structure

The automation system consists of:

```
songs-gen/
├── backend/          # FastAPI backend (to be built)
├── frontend/         # Streamlit web UI (to be built)
├── data/             # SQLite database and tokens
├── downloads/        # Generated audio from Suno
├── generated/        # Song files from Claude Code CLI (existing)
├── tools/            # Existing CLI tools (keep these)
└── docs/
    └── AUTOMATION_PIPELINE_PLAN.md  # Complete implementation plan
```

### Development Workflow

When the user asks you to work on the automation pipeline:

1. **ALWAYS read the plan first**:
   ```
   docs/AUTOMATION_PIPELINE_PLAN.md
   ```
   This contains the complete architecture, tech stack, and implementation phases.

2. **Follow the phase-based approach**:
   - Phase 1: Core Infrastructure (Docker, database, basic backend)
   - Phase 2: Backend Core (API endpoints, services)
   - Phase 3: Suno Integration (upload automation)
   - Phase 4: Evaluation System (auto-quality checks)
   - Phase 5: YouTube Integration (upload to YouTube)
   - Phase 6: Web UI (Streamlit interface with auth)
   - Phase 7: Testing (end-to-end validation)

3. **Tech Stack to Use**:
   - **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite
   - **Frontend**: Streamlit (NOT React/Next.js for cost savings)
   - **Auth**: JWT tokens with bcrypt password hashing
   - **Queue**: Python threading (NO Redis/Celery - cost optimization)
   - **Browser**: Playwright (for Suno if no API exists)
   - **YouTube**: Google API Python Client with OAuth 2.0
   - **Container**: Docker + Docker Compose

4. **Key Principles**:
   - **Cost-optimized**: Use SQLite not PostgreSQL, threading not Celery
   - **Simple**: 2 Docker containers (backend + frontend), not 6+
   - **Local-first**: Runs on user's machine, no cloud hosting
   - **Mobile-friendly**: Streamlit is auto-responsive
   - **Secure**: JWT auth, bcrypt passwords, environment variables

5. **What NOT to Use** (saves costs):
   - ❌ PostgreSQL → Use SQLite
   - ❌ Redis → Use Python threading
   - ❌ Celery → Use background threads
   - ❌ Next.js → Use Streamlit
   - ❌ S3 → Use local file storage
   - ❌ Cloud hosting → Docker on local machine

### Implementation Guidelines

#### When Creating Backend Code:
```python
# Use FastAPI with async/await
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Always use type hints
async def get_song(song_id: str, db: Session = Depends(get_db)) -> Song:
    song = db.query(Song).filter(Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

# Use Pydantic for validation
class SongCreate(BaseModel):
    title: str
    genre: str
    style_prompt: str
    lyrics: str
```

#### When Creating Frontend Code:
```python
# Use Streamlit's simple API
import streamlit as st

st.title("Song Automation Pipeline")

# Authentication
if not st.session_state.get("authenticated"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Call backend API
        pass

# Mobile-friendly layout
col1, col2 = st.columns(2)
with col1:
    st.button("Approve", use_container_width=True)
with col2:
    st.button("Reject", use_container_width=True)
```

#### When Creating Services:
```python
# File watcher service
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SongFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.md'):
            # Parse song file and add to database
            pass

# Suno client (if using Playwright)
from playwright.async_api import async_playwright

class SunoClient:
    async def upload_song(self, style_prompt: str, lyrics: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Navigate to Suno, login, upload
            pass
```

### Database Schema Reference

Always follow the schema in `AUTOMATION_PIPELINE_PLAN.md`:

- `users` - Authentication (username, password_hash, role)
- `songs` - Song metadata and status tracking
- `suno_jobs` - Suno upload/generation tracking
- `evaluations` - Quality scores and manual reviews
- `youtube_uploads` - YouTube upload tracking

### Status Flow

Songs move through these statuses:
```
pending → uploading → generating → downloaded → evaluated → uploaded
```

Track status in the `songs.status` column and update as each step completes.

### Security Requirements

1. **Never commit sensitive data**:
   - API keys → `.env` file (gitignored)
   - Passwords → Hashed with bcrypt
   - Tokens → Encrypted in database

2. **Always validate input**:
   - Use Pydantic schemas for API input
   - Validate file paths (prevent path traversal)
   - Limit file sizes

3. **Implement authentication**:
   - JWT tokens for API access
   - Role-based access (admin vs user)
   - Secure password hashing (bcrypt)

### Testing Approach

1. **Unit tests** for services:
   ```python
   def test_file_watcher_detects_new_song():
       # Test that file watcher picks up new .md files
       pass
   ```

2. **Integration tests** for API:
   ```python
   def test_song_creation_endpoint():
       response = client.post("/api/songs", json=song_data)
       assert response.status_code == 200
   ```

3. **End-to-end tests** for workflows:
   ```python
   def test_complete_pipeline():
       # Create song → Upload to Suno → Download → Evaluate → Upload to YouTube
       pass
   ```

### Common Development Tasks

#### "Build the file watcher service"
1. Read `docs/AUTOMATION_PIPELINE_PLAN.md` Phase 2
2. Create `backend/app/services/file_watcher.py`
3. Use `watchdog` library to monitor `generated/songs/` folder
4. Parse `.md` and `.meta.json` files
5. Insert into `songs` table
6. Trigger upload to Suno queue

#### "Implement Suno integration"
1. Read `docs/AUTOMATION_PIPELINE_PLAN.md` Phase 3
2. Research if Suno has API (check docs, forums)
3. If no API: Use Playwright for browser automation
4. Create `backend/app/services/suno_client.py`
5. Implement login, upload, status check, download
6. Add retry logic and error handling

#### "Create the web UI"
1. Read `docs/AUTOMATION_PIPELINE_PLAN.md` Phase 6
2. Create `frontend/streamlit_app.py` as main entry
3. Create pages in `frontend/pages/`:
   - `1_📊_Dashboard.py` - Stats and overview
   - `2_📋_Queue.py` - Upload queue status
   - `3_⭐_Review.py` - Manual song review
   - `4_🎬_YouTube.py` - YouTube uploads
   - `5_⚙️_Settings.py` - Configuration
4. Implement JWT authentication
5. Make mobile-friendly (large buttons, responsive layout)

#### "Set up Docker environment"
1. Read `docs/AUTOMATION_PIPELINE_PLAN.md` Phase 1
2. Create `docker-compose.yml` with 2 services
3. Create `backend/Dockerfile` for FastAPI
4. Create `frontend/Dockerfile` for Streamlit
5. Create `.env.example` with all required variables
6. Test with `docker-compose up`

### Debugging Tips

1. **Backend not starting**:
   ```bash
   docker logs songs-backend
   # Check for import errors, missing env vars
   ```

2. **File watcher not detecting files**:
   ```bash
   docker exec songs-backend ls -la /app/generated/songs
   # Verify volume mount is correct
   ```

3. **YouTube auth failing**:
   ```bash
   cat data/youtube_tokens.json
   # Check if tokens are valid
   # Re-run OAuth flow if expired
   ```

4. **Database locked**:
   ```bash
   # SQLite write lock - restart backend
   docker restart songs-backend
   ```

### Integration with Existing CLI

The automation pipeline **COMPLEMENTS** the existing CLI tools in `tools/`:

- **CLI tools** remain for manual song creation
- **Automation pipeline** handles mechanical tasks (upload, download, evaluate, publish)
- Both systems share the `generated/` folder
- CLI writes `.md` files → Automation detects and processes them

**DO NOT** remove or replace existing CLI tools. Keep them functional.

### Mobile Access

User wants to access from phone. Recommend:

1. **Local network**: `http://192.168.1.X:8501` (same WiFi)
2. **Tailscale** (recommended): Secure remote access
3. **Cloudflare Tunnel**: Public HTTPS URL
4. **ngrok**: Quick temporary URL for testing

### File Organization Standards

Follow the global `~/.claude/CLAUDE.md` standards:

- Keep project root clean
- All documentation in `docs/`
- Archive old docs in `docs/archive/`
- Update `docs/README.md` when adding new docs

---

**Remember**:

For **song creation tasks**: Follow the song generation guidelines above.

For **automation development tasks**: Follow the automation pipeline guidelines, always reference `AUTOMATION_PIPELINE_PLAN.md`, use cost-optimized tech stack, and maintain compatibility with existing CLI tools.
