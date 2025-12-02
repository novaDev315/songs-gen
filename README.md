# Song Generation System

A comprehensive AI-powered song generation and publishing platform that integrates with Suno AI for music creation and YouTube for automated video publishing.

## Features

- **AI Song Generation**: Create songs using Suno AI with customizable style prompts
- **Mini YouTube Studio**: Edit covers, sync lyrics, generate videos
- **Automated Pipeline**: Watch folder detection, evaluation, and publishing
- **Beat-Synced Lyrics**: Automatic lyric timing using audio analysis
- **Cover Art Generation**: Templates and AI-powered cover generation via OpenRouter
- **YouTube Integration**: Direct upload with metadata management

## Architecture

```
songs-gen/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   └── tests/              # Unit and integration tests
├── frontend/               # Vue.js frontend (+ Streamlit legacy)
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # Vue components
│   │   ├── stores/        # Pinia stores
│   │   └── views/         # Page views
│   └── pages/             # Streamlit pages (legacy)
├── tools/                  # Utility scripts
└── generated/             # Generated song files
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg (for video generation)
- SQLite or PostgreSQL

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example ../.env
# Edit .env with your settings

# Run the backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup (Vue.js)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Environment Variables

Key environment variables (see `.env.example` for full list):

```env
# Security
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/songs.db

# Suno AI (session-based)
SUNO_SESSION_FILE=./data/suno_session.json

# YouTube OAuth
YOUTUBE_CLIENT_ID=your-client-id
YOUTUBE_CLIENT_SECRET=your-client-secret

# OpenRouter (for AI covers)
OPENROUTER_API_KEY=your-api-key
```

## API Endpoints

### Songs
- `GET /api/v1/songs` - List all songs
- `POST /api/v1/songs` - Create a song
- `GET /api/v1/songs/{id}` - Get song details
- `PUT /api/v1/songs/{id}` - Update song
- `DELETE /api/v1/songs/{id}` - Delete song

### Studio
- `POST /api/v1/studio/projects` - Create video project
- `GET /api/v1/studio/projects/{id}` - Get project details
- `POST /api/v1/studio/projects/{id}/cover/template` - Generate template cover
- `POST /api/v1/studio/projects/{id}/cover/ai` - Generate AI cover
- `POST /api/v1/studio/projects/{id}/render` - Render full video

### YouTube
- `GET /api/v1/youtube/auth-url` - Get OAuth URL
- `POST /api/v1/youtube/callback` - Handle OAuth callback
- `POST /api/v1/youtube/upload` - Upload video to YouTube

## Development

### Running Tests

```bash
cd backend
pytest                    # All tests
pytest tests/unit         # Unit tests only
pytest tests/integration  # Integration tests only
pytest -v --tb=short     # Verbose with short traceback
```

### Code Quality

```bash
# Backend
ruff check .              # Linting
ruff format .             # Formatting
mypy app                  # Type checking

# Frontend
npm run lint              # ESLint
npm run type-check        # TypeScript
```

## Pipeline Stages

1. **Song Creation**: Create song metadata with style prompts
2. **Suno Generation**: Upload to Suno AI for audio generation
3. **Download**: Fetch generated audio files
4. **Evaluation**: Analyze audio quality and features
5. **Video Creation**: Generate lyric videos with covers
6. **Publishing**: Upload to YouTube with metadata

## License

MIT License - See LICENSE file for details.
