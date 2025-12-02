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
