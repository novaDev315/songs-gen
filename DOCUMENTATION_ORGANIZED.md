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
