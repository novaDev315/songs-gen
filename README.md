# Songs Generation System

A comprehensive system for creating AI-generated songs using Suno AI, optimized for Claude Code integration.

## 📁 Folder Structure

```
songs-gen/
├── README.md                    # This file
├── templates/                   # Genre-specific templates
│   ├── pop/                    # Pop music templates
│   ├── hip-hop/                # Hip-hop/Rap templates
│   ├── edm/                    # Electronic/EDM templates
│   ├── rock/                   # Rock music templates
│   ├── country/                # Country music templates
│   ├── jazz/                   # Jazz music templates
│   └── multi-singer/           # Multi-persona templates
├── generated/                   # Your created songs
│   ├── pop/
│   ├── hip-hop/
│   ├── edm/
│   ├── rock/
│   ├── country/
│   ├── jazz/
│   └── experimental/
├── reference/                   # Comprehensive guides
│   ├── Mastering Suno AI Prompt Engineering...md
│   └── Suno AI Multi-Singer Song Creation Guide.md
├── personas/                    # Voice persona library
│   └── persona-library.md
├── examples/                    # Example songs from guides
└── workflows/                   # Generation workflows
    └── song-creation-workflow.md
```

## 🎯 Quick Start

### 1. Choose Your Approach

**Single-Singer Song:**
```bash
# Use genre-specific template
cp templates/pop/pop-template.md generated/pop/my-song.md
# Edit and generate
```

**Multi-Singer Song:**
```bash
# Use multi-singer template
cp templates/multi-singer/multi-singer-template.md generated/experimental/my-collab.md
# Edit with persona assignments
```

### 2. Generate with Claude

```bash
# Ask Claude to create a song
"Using the [GENRE] template, create a song about [TOPIC]
with [MOOD/STYLE] that [SPECIFIC REQUIREMENTS]"
```

### 3. Iterate & Refine

- Generate 6+ variations
- Use Replace Section for problem areas
- Track successful prompts in your song file

## 🎨 Key Principles (from guides)

1. **4-7 Descriptor Rule**: Optimal style prompt length
2. **Artist-Inspired Anchoring**: Describe characteristics, not names
3. **Structure Tags**: Always use [Verse], [Chorus], etc.
4. **Format for Effect**: CAPS for power, ellipses for pacing, *asterisks* for sound effects
5. **Multi-Singer Magic**: PHOENIX + NEON + REBEL = Commercial quality

## 📚 Resources

- **Full Prompt Engineering Guide**: `reference/Mastering Suno AI Prompt Engineering...md`
- **Multi-Singer Guide**: `reference/Suno AI Multi-Singer Song Creation Guide.md`
- **Persona Library**: `personas/persona-library.md`
- **Workflow Guide**: `workflows/song-creation-workflow.md`

## 🎵 Supported Genres

Each genre has optimized templates with:
- Style prompt formulas
- Structure patterns
- Instrumentation guides
- Best practices
- Example prompts

## 🤖 Claude Integration

Claude Code can help you:
1. Generate lyrics following Suno best practices
2. Create style prompts with optimal descriptor count
3. Format with proper tags and emphasis
4. Suggest iterations and variations
5. Track successful patterns

## 🚀 Advanced Features

- **Persona System**: Pre-defined voice characteristics (PHOENIX, NEON, REBEL, etc.)
- **Dynamic Templates**: Genre-specific with proven structures
- **Iteration Tracking**: Document what works for your style
- **Multi-Singer Coordination**: Complex voice arrangements made simple

## 📈 Success Metrics

Track your songs:
- Generation count (aim for 6+ variations)
- Successful prompt patterns
- Best persona combinations
- Genre-specific discoveries

---

**Version**: 1.0
**Last Updated**: 2025-10-15
**Based on**: Comprehensive Suno AI community research and testing
