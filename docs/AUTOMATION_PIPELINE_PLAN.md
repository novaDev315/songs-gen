# Song Automation Pipeline - Implementation Plan

**Last Updated**: 2025-11-16
**Status**: Approved and Ready for Implementation
**Timeline**: 8 weeks
**Estimated Cost**: $0-20/month

---

## Executive Summary

Build a cost-optimized Docker-based automation system that integrates with the existing Claude Code CLI song generation system. The pipeline automates the mechanical tasks of uploading to Suno.com, downloading generated audio, evaluating quality, and uploading to YouTube - while keeping the creative song generation with Claude Code CLI.

### Simplified Workflow

```
Claude Code CLI → Create song prompts (.md files) in generated/
    ↓
File Watcher → Auto-detect new songs
    ↓
Suno Uploader → Upload to Suno.com (API or browser automation)
    ↓
Download Manager → Auto-fetch generated audio files
    ↓
Evaluator → Auto-analysis + manual review via Web UI
    ↓
YouTube Uploader → Upload approved songs to YouTube
```

---

## Cost Optimizations

### What We're NOT Building (Saves Time & Money)

- ❌ **NO PostgreSQL** → Using SQLite (file-based, no container needed)
- ❌ **NO Redis + Celery** → Simple Python threading (adequate for single user)
- ❌ **NO Complex Frontend** → Streamlit (Python-based, auto-mobile-friendly)
- ❌ **NO S3** → Local file storage
- ❌ **NO Cloud Hosting** → Runs locally in Docker
- ❌ **NO AI Song Generation Automation** → Keep using Claude Code CLI

### What We ARE Building (Lean & Efficient)

- ✅ **Simple Docker Compose** → 2 containers only
- ✅ **SQLite Database** → Zero infrastructure cost
- ✅ **FastAPI Backend** → Modern, fast, async Python
- ✅ **Streamlit Frontend** → Python-based UI, mobile-friendly
- ✅ **JWT Authentication** → Username/password for you + team
- ✅ **File-based Queue** → Built-in Python threading

**Estimated Savings**: $50-200/month + 90% less development complexity

---

## Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1 (async, modern, auto-docs)
- **Database**: SQLite 3 (file-based, zero-cost)
- **Auth**: JWT tokens + bcrypt password hashing
- **Queue**: Python threading (no Redis needed)
- **File Watching**: watchdog library
- **Browser Automation**: Playwright (for Suno if no API)
- **Audio Analysis**: librosa + pydub
- **YouTube**: Google API Python Client

### Frontend
- **Framework**: Streamlit 1.28.2 (Python-based, auto-responsive)
- **Auth**: streamlit-authenticator
- **API Client**: requests library

### Infrastructure
- **Container**: Docker + Docker Compose
- **Services**: 2 containers (backend + frontend)
- **Storage**: Local filesystem
- **Database File**: ./data/songs.db

### Total Dependencies
- **Backend**: ~15 packages
- **Frontend**: ~3 packages
- **Complexity**: LOW (vs HIGH for microservices)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      User (You + Team)                       │
└───────────┬─────────────────────────────────┬───────────────┘
            │                                 │
            │ (Create Songs)                  │ (Manage via Web)
            ▼                                 ▼
    ┌───────────────┐               ┌──────────────────┐
    │  Claude Code  │               │  Streamlit UI    │
    │      CLI      │               │  (Port 8501)     │
    └───────┬───────┘               └────────┬─────────┘
            │                                │
            │ (Writes .md files)             │ (API Calls)
            ▼                                ▼
    ┌────────────────────────────────────────────────────┐
    │           FastAPI Backend (Port 8000)              │
    │  ┌──────────────────────────────────────────────┐  │
    │  │  File Watcher → Detects new songs            │  │
    │  │  Suno Client → Uploads to Suno.com           │  │
    │  │  Download Manager → Fetches audio            │  │
    │  │  Evaluator → Analyzes quality                │  │
    │  │  YouTube Uploader → Uploads to YouTube       │  │
    │  └──────────────────────────────────────────────┘  │
    └────────┬─────────────────────────────┬─────────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐          ┌──────────────────┐
    │  SQLite DB      │          │  File Storage    │
    │  (songs.db)     │          │  - generated/    │
    │                 │          │  - downloads/    │
    └─────────────────┘          └──────────────────┘
```

### Docker Services

```yaml
services:
  backend:
    # FastAPI + SQLite + Background workers
    # Handles:
    #   - REST API
    #   - File watching (watchdog)
    #   - Suno uploads (Playwright)
    #   - Downloads (HTTP)
    #   - Evaluation (librosa)
    #   - YouTube uploads (Google API)
    ports:
      - "8000:8000"
    volumes:
      - ./generated:/app/generated
      - ./downloads:/app/downloads
      - ./data:/app/data

  frontend:
    # Streamlit Web UI
    # Handles:
    #   - Authentication
    #   - Song review interface
    #   - YouTube management
    ports:
      - "8501:8501"
    volumes:
      - ./downloads:/app/downloads
```

---

## Database Schema (SQLite)

### Tables

#### 1. `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',  -- admin, user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**Purpose**: Multi-user authentication
**Initial Data**: Admin user created on first run

#### 2. `songs`
```sql
CREATE TABLE songs (
    id TEXT PRIMARY KEY,  -- UUID from .md filename
    title TEXT NOT NULL,
    genre TEXT,
    style_prompt TEXT,
    lyrics TEXT,
    file_path TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, uploading, generating, downloaded, evaluated, uploaded, failed
    metadata_json TEXT,  -- JSON blob from .meta.json
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Track songs from creation through YouTube upload
**Status Flow**: pending → uploading → generating → downloaded → evaluated → uploaded

#### 3. `suno_jobs`
```sql
CREATE TABLE suno_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL REFERENCES songs(id),
    suno_job_id TEXT,  -- Suno's internal tracking ID
    status TEXT DEFAULT 'queued',  -- queued, processing, completed, failed
    audio_url TEXT,  -- Download URL from Suno
    downloaded_path TEXT,  -- Local file path
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Purpose**: Track Suno generation jobs and retry logic
**Retry Logic**: Max 3 attempts before marking as failed

#### 4. `evaluations`
```sql
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL REFERENCES songs(id),
    audio_quality_score REAL,  -- 0-100 from auto-analysis
    duration_seconds REAL,
    file_size_mb REAL,
    sample_rate INTEGER,
    bitrate INTEGER,
    manual_rating INTEGER,  -- 1-5 stars (NULL if not reviewed)
    approved BOOLEAN DEFAULT 0,
    notes TEXT,
    evaluated_by INTEGER REFERENCES users(id),
    evaluated_at TIMESTAMP
);
```

**Purpose**: Store both auto and manual evaluations
**Auto Metrics**: File size, duration, sample rate, bitrate, quality score
**Manual**: Star rating, approval, notes

#### 5. `youtube_uploads`
```sql
CREATE TABLE youtube_uploads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL REFERENCES songs(id),
    video_id TEXT,  -- YouTube video ID (e.g., "dQw4w9WgXcQ")
    video_url TEXT,  -- Full YouTube URL
    upload_status TEXT DEFAULT 'queued',  -- queued, uploading, completed, failed
    title TEXT,
    description TEXT,
    tags TEXT,  -- Comma-separated
    privacy TEXT DEFAULT 'public',  -- public, unlisted, private
    error_message TEXT,
    uploaded_by INTEGER REFERENCES users(id),
    uploaded_at TIMESTAMP
);
```

**Purpose**: Track YouTube uploads and video metadata
**Video URL**: https://youtube.com/watch?v={video_id}

### Indexes

```sql
CREATE INDEX idx_songs_status ON songs(status);
CREATE INDEX idx_songs_created_at ON songs(created_at);
CREATE INDEX idx_suno_jobs_status ON suno_jobs(status);
CREATE INDEX idx_suno_jobs_song_id ON suno_jobs(song_id);
CREATE INDEX idx_evaluations_song_id ON evaluations(song_id);
CREATE INDEX idx_youtube_uploads_song_id ON youtube_uploads(song_id);
CREATE INDEX idx_youtube_uploads_status ON youtube_uploads(upload_status);
```

---

## Directory Structure

```
songs-gen/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Configuration from env vars
│   │   ├── database.py               # SQLite connection & models
│   │   ├── worker.py                 # Background worker threads
│   │   │
│   │   ├── api/                      # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # Login, logout, JWT
│   │   │   ├── songs.py              # Song CRUD
│   │   │   ├── queue.py              # Queue status
│   │   │   ├── review.py             # Evaluation endpoints
│   │   │   └── youtube.py            # YouTube operations
│   │   │
│   │   ├── models/                   # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── song.py
│   │   │   ├── suno_job.py
│   │   │   ├── evaluation.py
│   │   │   └── youtube_upload.py
│   │   │
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── song.py
│   │   │   ├── evaluation.py
│   │   │   └── youtube.py
│   │   │
│   │   └── services/                 # Business Logic
│   │       ├── __init__.py
│   │       ├── file_watcher.py       # Monitor generated/ folder
│   │       ├── suno_client.py        # Suno.com integration
│   │       ├── download_manager.py   # Auto-download songs
│   │       ├── evaluator.py          # Audio analysis
│   │       └── youtube_uploader.py   # YouTube API client
│   │
│   ├── Dockerfile                    # Backend container
│   ├── requirements.txt              # Python dependencies
│   └── alembic/                      # Database migrations (optional)
│
├── frontend/                         # Streamlit UI
│   ├── streamlit_app.py              # Main entry point
│   ├── auth.py                       # Auth helpers
│   ├── api_client.py                 # Backend API client
│   │
│   ├── pages/                        # Streamlit pages
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_📋_Queue.py
│   │   ├── 3_⭐_Review.py
│   │   ├── 4_🎬_YouTube.py
│   │   └── 5_⚙️_Settings.py
│   │
│   ├── components/                   # Reusable UI components
│   │   ├── __init__.py
│   │   ├── audio_player.py
│   │   ├── song_card.py
│   │   └── stats_widget.py
│   │
│   ├── Dockerfile                    # Frontend container
│   └── requirements.txt              # Streamlit dependencies
│
├── data/                             # SQLite database & app data
│   ├── songs.db                      # Main database
│   ├── tokens.json                   # YouTube OAuth tokens
│   └── logs/                         # Application logs
│
├── downloads/                        # Generated audio files from Suno
│   └── [song-id].mp3
│
├── generated/                        # Existing Claude Code CLI output
│   └── songs/
│       └── [genre]/
│           ├── [song-id].md
│           └── [song-id].meta.json
│
├── tools/                            # Keep existing CLI tools
│   └── [existing Python CLI]
│
├── docs/                             # Documentation
│   ├── AUTOMATION_PIPELINE_PLAN.md   # This file
│   ├── SETUP_GUIDE.md                # Installation instructions
│   ├── API_DOCUMENTATION.md          # API reference
│   └── [existing docs]
│
├── docker-compose.yml                # Docker orchestration
├── .env.example                      # Environment template
├── .env                              # Local environment (gitignored)
├── .gitignore                        # Git ignore rules
├── pyproject.toml                    # Existing project config
└── README.md                         # Updated with new features
```

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Goal**: Set up Docker environment, database, and basic backend

#### Tasks:
1. ✅ Create directory structure
2. ✅ Set up Docker Compose configuration
3. ✅ Create SQLite database schema
4. ✅ Create `.env.example` file
5. ✅ Build FastAPI backend skeleton
6. ✅ Implement basic JWT authentication
7. ✅ Create health check endpoints
8. ✅ Test Docker containers start successfully

#### Deliverables:
- Working Docker Compose setup
- SQLite database with all tables
- FastAPI backend with `/health` endpoint
- JWT authentication working
- Environment configuration template

---

### Phase 2: Backend Core (Week 2)

**Goal**: Build API endpoints and core services

#### Tasks:
1. ✅ Implement song CRUD API endpoints
2. ✅ Create file watcher service
3. ✅ Build queue management API
4. ✅ Add evaluation API endpoints
5. ✅ Create YouTube API endpoints
6. ✅ Implement background worker manager
7. ✅ Add logging and error handling
8. ✅ Write unit tests for API endpoints

#### Deliverables:
- Complete REST API for song management
- File watcher detecting new `.md` files
- API endpoints for all operations
- Background worker framework
- Comprehensive error handling

---

### Phase 3: Suno Integration (Week 3)

**Goal**: Connect to Suno.com for song generation

#### Tasks:
1. 🔍 Research Suno.com integration options
   - Check for official/unofficial API
   - Test browser automation with Playwright
   - Document authentication mechanism
   - Identify rate limits

2. ✅ Implement Suno client
   - Login/session management
   - Upload song (style prompt + lyrics)
   - Check generation status
   - Download audio file

3. ✅ Build upload queue system
   - Queue pending songs
   - Respect rate limits
   - Retry failed uploads
   - Track job status

4. ✅ Test end-to-end upload flow

#### Deliverables:
- Working Suno client (API or Playwright)
- Upload queue with rate limiting
- Status polling mechanism
- Error handling and retries

**Note**: This phase depends on Suno.com's available integration methods

---

### Phase 4: Evaluation System (Week 4)

**Goal**: Auto-evaluate downloaded songs

#### Tasks:
1. ✅ Implement download manager
   - Poll Suno jobs for completion
   - Download audio files
   - Save to `downloads/` folder
   - Update database

2. ✅ Build auto-evaluator
   - File size validation
   - Duration check
   - Sample rate detection
   - Bitrate analysis
   - Calculate quality score (0-100)

3. ✅ Create evaluation API
   - Get pending evaluations
   - Submit manual ratings
   - Approve/reject songs
   - Bulk operations

4. ✅ Test evaluation workflow

#### Deliverables:
- Automatic download of completed songs
- Audio quality analysis
- Evaluation API endpoints
- Manual review capability

---

### Phase 5: YouTube Integration (Week 5)

**Goal**: Upload approved songs to YouTube

#### Tasks:
1. 📝 Set up Google Cloud project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials
   - Configure redirect URIs
   - Download credentials file

2. ✅ Implement YouTube uploader
   - OAuth 2.0 authentication flow
   - Token storage and refresh
   - Video upload from audio file
   - Metadata generation (title, description, tags)
   - Privacy settings

3. ✅ Build upload queue
   - Queue approved songs
   - Upload with retry logic
   - Track upload status
   - Store video IDs

4. ✅ Test YouTube upload flow

#### Deliverables:
- Working YouTube OAuth flow
- Automatic video uploads
- Metadata generation
- Upload tracking

**Prerequisites**: Google Cloud account (free tier sufficient)

---

### Phase 6: Web UI with Auth (Week 6-7)

**Goal**: Build mobile-friendly web interface

#### Week 6 Tasks:
1. ✅ Set up Streamlit app structure
2. ✅ Implement authentication page
3. ✅ Create API client for backend
4. ✅ Build Dashboard page
   - Stats widgets
   - Recent activity
   - Quick actions
5. ✅ Build Queue page
   - List pending songs
   - Status indicators
   - Retry buttons

#### Week 7 Tasks:
1. ✅ Build Review page (most important!)
   - Filter by status
   - Audio player
   - Rating system
   - Approve/reject buttons
   - Notes field
   - Batch operations

2. ✅ Build YouTube page
   - List uploaded videos
   - Video previews
   - Upload status
   - Links to YouTube

3. ✅ Build Settings page
   - User management (admin only)
   - Configure credentials
   - Set preferences

4. ✅ Mobile optimization
   - Responsive layout
   - Touch-friendly buttons
   - Bottom navigation

#### Deliverables:
- Complete web UI with 5 pages
- Authentication flow
- Mobile-friendly design
- All features accessible via UI

---

### Phase 7: Integration & Testing (Week 8)

**Goal**: End-to-end testing and documentation

#### Tasks:
1. ✅ End-to-end workflow testing
   - Create song with Claude Code CLI
   - Verify file detection
   - Confirm Suno upload
   - Monitor generation
   - Check auto-download
   - Review in web UI
   - Approve and upload to YouTube
   - Verify video on channel

2. ✅ Error scenario testing
   - Failed Suno uploads
   - Download failures
   - YouTube upload errors
   - Network issues
   - Rate limiting

3. ✅ Performance testing
   - Multiple simultaneous uploads
   - Large batch processing
   - Long-running sessions

4. ✅ Create documentation
   - Setup guide
   - User manual
   - API documentation
   - Troubleshooting guide

5. ✅ Code cleanup and optimization

#### Deliverables:
- Fully tested system
- Comprehensive documentation
- Deployment guide
- Known issues and workarounds

---

## Dependencies

### Backend (backend/requirements.txt)

```txt
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database
sqlalchemy==2.0.23
aiosqlite==0.19.0

# Authentication
pyjwt==2.8.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# File Watching
watchdog==3.0.0

# Browser Automation (for Suno)
playwright==1.40.0

# Audio Processing
librosa==0.10.1
pydub==0.25.1
soundfile==0.12.1

# YouTube API
google-auth-oauthlib==1.1.0
google-api-python-client==2.108.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0
aiofiles==23.2.1
```

**Total**: ~15 core dependencies

### Frontend (frontend/requirements.txt)

```txt
# UI Framework
streamlit==1.28.2

# Authentication
streamlit-authenticator==0.2.3

# API Client
requests==2.31.0

# Utilities
python-dotenv==1.0.0
```

**Total**: ~4 core dependencies

---

## Environment Configuration

### .env.example

```bash
# ============================================
# SONGS GENERATION AUTOMATION - CONFIGURATION
# ============================================

# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_URL=http://backend:8000

# Frontend
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501

# Database
DATABASE_URL=sqlite:///data/songs.db

# Security
SECRET_KEY=<generate-with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# File Paths
WATCH_FOLDER=./generated/songs
DOWNLOAD_FOLDER=./downloads
DATA_FOLDER=./data

# Suno.com Credentials
SUNO_EMAIL=your-email@example.com
SUNO_PASSWORD=your-suno-password
SUNO_API_KEY=  # If official API exists

# YouTube API (Google Cloud)
YOUTUBE_CLIENT_ID=your-client-id.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your-client-secret
YOUTUBE_REDIRECT_URI=http://localhost:8501/oauth/callback
YOUTUBE_TOKENS_FILE=data/youtube_tokens.json

# YouTube Upload Settings
YOUTUBE_DEFAULT_PRIVACY=public  # public, unlisted, private
YOUTUBE_DEFAULT_CATEGORY=10  # Music
YOUTUBE_DEFAULT_PLAYLIST_ID=  # Optional

# Worker Settings
WORKER_CHECK_INTERVAL=60  # seconds
WORKER_MAX_RETRIES=3
WORKER_RETRY_DELAY=300  # seconds

# Rate Limiting
SUNO_RATE_LIMIT_DELAY=10  # seconds between uploads
YOUTUBE_RATE_LIMIT_DELAY=5  # seconds between uploads

# Evaluation Settings
MIN_AUDIO_DURATION=30  # seconds
MAX_AUDIO_DURATION=600  # seconds
MIN_QUALITY_SCORE=50  # 0-100

# Admin User (created on first run)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<change-on-first-login>
```

---

## Docker Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: songs-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./generated:/app/generated:ro  # Read-only
      - ./downloads:/app/downloads
      - ./data:/app/data
    environment:
      - APP_ENV=${APP_ENV:-development}
      - DATABASE_URL=sqlite:///data/songs.db
      - SECRET_KEY=${SECRET_KEY}
      - SUNO_EMAIL=${SUNO_EMAIL}
      - SUNO_PASSWORD=${SUNO_PASSWORD}
      - YOUTUBE_CLIENT_ID=${YOUTUBE_CLIENT_ID}
      - YOUTUBE_CLIENT_SECRET=${YOUTUBE_CLIENT_SECRET}
    env_file:
      - .env
    depends_on:
      - playwright-install
    networks:
      - songs-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: songs-frontend
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - ./downloads:/app/downloads:ro  # Read-only
    environment:
      - BACKEND_URL=http://backend:8000
    env_file:
      - .env
    depends_on:
      - backend
    networks:
      - songs-network

  # One-time service to install Playwright browsers
  playwright-install:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: playwright-installer
    command: playwright install chromium
    volumes:
      - playwright-browsers:/root/.cache/ms-playwright
    networks:
      - songs-network

volumes:
  playwright-browsers:

networks:
  songs-network:
    driver: bridge
```

### backend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/generated /app/downloads /app/data

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### frontend/Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## API Endpoints

### Authentication

```
POST   /api/auth/login          # Login with username/password
POST   /api/auth/logout         # Logout (invalidate token)
POST   /api/auth/refresh        # Refresh JWT token
GET    /api/auth/me             # Get current user info
```

### Songs

```
GET    /api/songs               # List all songs (with filters)
GET    /api/songs/{id}          # Get song details
POST   /api/songs               # Create new song (manual)
PUT    /api/songs/{id}          # Update song metadata
DELETE /api/songs/{id}          # Delete song
GET    /api/songs/{id}/status   # Get song status in pipeline
```

### Queue

```
GET    /api/queue/suno          # Get Suno upload queue
GET    /api/queue/youtube       # Get YouTube upload queue
POST   /api/queue/suno/{id}     # Add song to Suno queue
POST   /api/queue/youtube/{id}  # Add song to YouTube queue
DELETE /api/queue/suno/{id}     # Remove from Suno queue
POST   /api/queue/suno/{id}/retry  # Retry failed upload
```

### Evaluation

```
GET    /api/evaluations         # List all evaluations
GET    /api/evaluations/{id}    # Get evaluation details
POST   /api/evaluations         # Create manual evaluation
PUT    /api/evaluations/{id}    # Update evaluation
POST   /api/evaluations/{id}/approve    # Approve song
POST   /api/evaluations/{id}/reject     # Reject song
POST   /api/evaluations/batch-approve   # Approve multiple songs
```

### YouTube

```
GET    /api/youtube/uploads     # List YouTube uploads
GET    /api/youtube/uploads/{id}  # Get upload details
POST   /api/youtube/upload      # Upload song to YouTube
GET    /api/youtube/oauth-url   # Get OAuth authorization URL
POST   /api/youtube/oauth-callback  # Handle OAuth callback
DELETE /api/youtube/uploads/{id}  # Delete video (not from YouTube)
```

### Admin

```
GET    /api/admin/users         # List users (admin only)
POST   /api/admin/users         # Create user (admin only)
PUT    /api/admin/users/{id}    # Update user (admin only)
DELETE /api/admin/users/{id}    # Delete user (admin only)
GET    /api/admin/stats         # Get system statistics
```

### System

```
GET    /health                  # Health check
GET    /api/system/status       # System status (workers, queue sizes)
GET    /api/system/logs         # Get recent logs (admin only)
```

---

## Security Considerations

### 1. Authentication
- **JWT Tokens**: HS256 algorithm with strong secret key
- **Password Hashing**: bcrypt with salt rounds
- **Token Expiry**: 24 hours (configurable)
- **Secure Cookies**: HttpOnly, Secure flags in production

### 2. Authorization
- **Role-Based Access**: admin vs user roles
- **Endpoint Protection**: JWT required for all API calls
- **Admin-Only Routes**: User management, system logs

### 3. API Security
- **CORS**: Configured for frontend domain only
- **Rate Limiting**: Implement per-endpoint limits
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection**: SQLAlchemy ORM prevents SQL injection

### 4. File Security
- **Upload Validation**: Only .md files accepted
- **Path Traversal**: Validate file paths
- **File Size Limits**: Max 1MB for .md files
- **Virus Scanning**: Optional integration with ClamAV

### 5. Secrets Management
- **Environment Variables**: Never commit .env file
- **Secret Rotation**: Support for key rotation
- **OAuth Tokens**: Encrypted storage in database
- **API Keys**: Encrypted at rest

### 6. Production Hardening
- **HTTPS**: Use reverse proxy (nginx) with Let's Encrypt
- **Firewall**: Restrict ports (only 80, 443 exposed)
- **Docker Security**: Non-root user, read-only volumes
- **Updates**: Regular dependency updates

---

## Mobile Access Strategy

### Option 1: Local Network Access (Simplest)
```bash
# Access from phone on same WiFi:
http://192.168.1.XXX:8501

# Find your local IP:
ip addr show  # Linux
ipconfig      # Windows
```

**Pros**: No external exposure, free, fast
**Cons**: Only works on same network

### Option 2: Tailscale (Recommended)
```bash
# Install Tailscale on server and phone
# Access securely from anywhere:
http://100.64.0.XXX:8501

# Free for personal use
```

**Pros**: Secure, works anywhere, free, easy setup
**Cons**: Requires Tailscale app on phone

### Option 3: Cloudflare Tunnel (Advanced)
```bash
# Expose to internet securely:
cloudflared tunnel --url http://localhost:8501

# Access via:
https://your-subdomain.trycloudflare.com
```

**Pros**: Custom domain, HTTPS, no port forwarding
**Cons**: Requires Cloudflare account, slight latency

### Option 4: ngrok (Quick Testing)
```bash
# Temporary public URL:
ngrok http 8501

# Access via:
https://random-id.ngrok.io
```

**Pros**: Instant, no setup, HTTPS
**Cons**: Random URL, requires running ngrok

**Recommendation**: Use Tailscale for secure remote access

---

## Cost Breakdown

### Development Costs
| Phase | Duration | Effort (Hours) | Cost* |
|-------|----------|----------------|-------|
| Phase 1: Infrastructure | 1 week | 20 hours | $0 |
| Phase 2: Backend Core | 1 week | 20 hours | $0 |
| Phase 3: Suno Integration | 1 week | 20 hours | $0 |
| Phase 4: Evaluation | 1 week | 20 hours | $0 |
| Phase 5: YouTube | 1 week | 20 hours | $0 |
| Phase 6: Web UI | 2 weeks | 40 hours | $0 |
| Phase 7: Testing | 1 week | 20 hours | $0 |
| **Total** | **8 weeks** | **160 hours** | **$0** |

*Self-development cost (your time)

### Running Costs (Monthly)
| Service | Cost | Notes |
|---------|------|-------|
| **Hosting** | $0 | Runs locally on your machine |
| **Database** | $0 | SQLite (file-based) |
| **Suno.com** | $10-20 | Your existing subscription |
| **YouTube API** | $0 | Free (10,000 units/day quota) |
| **Storage** | $0 | Local disk space |
| **Compute** | ~$5 | Electricity for running Docker |
| **Domain (optional)** | $0-12 | Only if using custom domain |
| **Total** | **$15-37/month** | **vs $100-300 for cloud hosting** |

### One-Time Costs
- Google Cloud Project: **$0** (free tier)
- Docker Desktop: **$0** (free for personal use)
- Development Tools: **$0** (all open source)

**Total Startup Cost**: **$0**

---

## Success Metrics

### MVP Success Criteria (End of Week 8)
- ✅ Successfully upload 1 song to Suno API
- ✅ Auto-detect new .md files in generated/ folder
- ✅ Download generated audio automatically
- ✅ Evaluate audio quality with auto-score
- ✅ Manual review working in web UI
- ✅ Upload approved song to YouTube
- ✅ Authentication protecting all pages
- ✅ Mobile-friendly UI accessible from phone

### Production Success Criteria (Month 1-3)
- ✅ Process 50+ songs through full pipeline
- ✅ 95%+ successful Suno uploads (with retries)
- ✅ 95%+ successful YouTube uploads
- ✅ <5 minute average Suno upload time
- ✅ <2 minute average YouTube upload time
- ✅ Zero data loss (all songs tracked)
- ✅ <1% false positive rejections
- ✅ 3+ users actively using system

### Performance Metrics
- **Throughput**: 10+ songs/day
- **Latency**: <30 seconds API response time
- **Uptime**: 99%+ availability
- **Storage**: <100GB for 1000 songs
- **CPU**: <20% average usage
- **Memory**: <2GB RAM usage

---

## Risks & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Suno API doesn't exist | HIGH | Medium | Use Playwright browser automation as fallback |
| Suno rate limiting too strict | MEDIUM | High | Implement queue with configurable delays |
| API changes break integration | MEDIUM | Medium | Version API calls, monitor for changes, abstract client |
| Browser automation fails | MEDIUM | Low | Implement robust error handling and retries |
| YouTube quota exceeded | MEDIUM | Low | Monitor usage, implement soft limits |
| Large files fill disk | LOW | Medium | Implement cleanup policies, file size limits |
| Worker thread crashes | MEDIUM | Low | Implement watchdog, auto-restart |
| Database corruption | HIGH | Very Low | Regular backups, WAL mode for SQLite |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Forgot to start Docker | LOW | High | Create startup script, auto-start on boot |
| Lost API credentials | HIGH | Low | Secure backup of .env file |
| Disk space full | MEDIUM | Medium | Monitor disk usage, implement cleanup |
| Network outage during upload | MEDIUM | Low | Retry logic, queue persistence |
| YouTube account suspended | HIGH | Very Low | Follow YouTube ToS, respect rate limits |
| Suno account suspended | HIGH | Very Low | Respect rate limits, use official methods |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Suno changes pricing | MEDIUM | Medium | Monitor costs, set hard limits |
| YouTube policy changes | MEDIUM | Low | Stay updated on ToS changes |
| Time investment too high | MEDIUM | Low | Incremental development, MVP first |
| System too complex to maintain | MEDIUM | Low | Comprehensive documentation, simple architecture |

---

## Future Enhancements (Post-MVP)

### Phase 8+: Nice-to-Have Features

#### 1. Advanced Evaluation
- **AI-powered quality scoring** using pre-trained models
- **Lyric-to-audio matching** (verify lyrics were followed)
- **Genre classification** (auto-detect genre from audio)
- **Mood analysis** (energy, valence, tempo)
- **Plagiarism detection** (check for similar songs)

#### 2. Enhanced YouTube Management
- **Playlist auto-organization** by genre, date, rating
- **Thumbnail generation** from song metadata
- **Schedule publishing** (publish at optimal times)
- **Analytics integration** (track views, engagement)
- **Comment moderation** (auto-reply, filter spam)

#### 3. Collaboration Features
- **Multi-user workflows** (creator, reviewer, publisher roles)
- **Review comments** and discussions
- **Version control** for lyrics and prompts
- **Collaborative playlists**
- **Activity feed** (who did what, when)

#### 4. Advanced Automation
- **Batch song generation** (upload 10+ at once)
- **A/B testing** (generate multiple variations)
- **Style template library** (save successful prompts)
- **Auto-tagging** from lyrics (extract keywords)
- **Genre-specific pipelines** (custom workflows per genre)

#### 5. Analytics & Insights
- **Success rate dashboard** (acceptance rate by genre)
- **Quality trends** (scores over time)
- **YouTube performance** (views, watch time)
- **Cost tracking** (Suno usage, ROI)
- **Persona effectiveness** (which personas work best)

#### 6. Integration Extensions
- **Spotify upload** (via distributor API)
- **SoundCloud upload**
- **Apple Music upload** (via distributor)
- **Social media sharing** (Twitter, Instagram)
- **Discord notifications** (bot integration)
- **Slack notifications** (team updates)

#### 7. Mobile App
- **Native iOS/Android app** (React Native)
- **Push notifications** for completed songs
- **Offline review mode**
- **Voice commands** for approval/rejection
- **Camera for QR code scanning** (share songs)

#### 8. AI Enhancements
- **Claude Code API integration** (automate prompt generation)
- **Auto-improve rejected songs** (analyze and suggest changes)
- **Predictive quality scoring** (before uploading to Suno)
- **Smart scheduling** (optimal upload times)
- **Trend analysis** (suggest popular styles)

---

## Maintenance Plan

### Daily Tasks (Automated)
- ✅ Check worker health
- ✅ Monitor queue sizes
- ✅ Verify disk space
- ✅ Check error logs

### Weekly Tasks (Manual)
- 🔍 Review failed uploads (investigate why)
- 🔍 Check YouTube video performance
- 🔍 Audit user activity (if multi-user)
- 🔍 Backup database file

### Monthly Tasks
- 🔄 Update dependencies (security patches)
- 🔄 Review and archive old songs
- 🔄 Clean up unused audio files
- 🔄 Rotate API tokens (if needed)
- 🔄 Review system performance metrics

### Quarterly Tasks
- 📊 Analyze success rates and trends
- 📊 Plan feature enhancements
- 📊 Audit security configurations
- 📊 Optimize storage (compress old files)

---

## Troubleshooting Guide

### Common Issues

#### 1. File Watcher Not Detecting New Songs
```bash
# Check if folder path is correct
docker exec songs-backend ls -la /app/generated/songs

# Check worker logs
docker logs songs-backend

# Restart backend
docker restart songs-backend
```

#### 2. Suno Upload Failing
```bash
# Check credentials
docker exec songs-backend env | grep SUNO

# Test login manually (in container)
docker exec -it songs-backend python -m app.services.suno_client

# Check rate limiting
# Wait 60 seconds and retry
```

#### 3. YouTube Upload Failing
```bash
# Check OAuth tokens
cat data/youtube_tokens.json

# Re-authenticate
# Delete tokens file and login again via UI

# Check quota
# Visit Google Cloud Console > APIs & Services > Quotas
```

#### 4. Web UI Not Loading
```bash
# Check if frontend container is running
docker ps | grep songs-frontend

# Check frontend logs
docker logs songs-frontend

# Restart frontend
docker restart songs-frontend

# Access directly
curl http://localhost:8501
```

#### 5. Database Locked Error
```bash
# SQLite WAL mode prevents most locks
# If persistent, check for long-running transactions

# Restart backend to release locks
docker restart songs-backend

# If corrupted, restore from backup
cp data/songs.db.backup data/songs.db
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Copy `.env.example` to `.env`
- [ ] Generate strong `SECRET_KEY`
- [ ] Set `ADMIN_PASSWORD` to strong password
- [ ] Configure Suno credentials
- [ ] Set up Google Cloud project
- [ ] Configure YouTube OAuth credentials
- [ ] Create necessary directories
- [ ] Test Docker Compose locally

### Initial Deployment
- [ ] Run `docker-compose up -d`
- [ ] Verify both containers started
- [ ] Access Web UI at http://localhost:8501
- [ ] Login with admin credentials
- [ ] **CHANGE ADMIN PASSWORD IMMEDIATELY**
- [ ] Test file watcher (create dummy song)
- [ ] Test Suno upload (with real song)
- [ ] Test YouTube OAuth flow
- [ ] Test complete end-to-end workflow

### Post-Deployment
- [ ] Set up automatic backups
- [ ] Configure firewall rules
- [ ] Set up monitoring/alerting
- [ ] Document access URLs
- [ ] Train additional users (if any)
- [ ] Create runbook for common issues

### Production Hardening
- [ ] Set `APP_ENV=production` in `.env`
- [ ] Set `DEBUG=false`
- [ ] Configure HTTPS with nginx + Let's Encrypt
- [ ] Enable rate limiting
- [ ] Set up log rotation
- [ ] Configure automated backups
- [ ] Set up uptime monitoring

---

## Support & Resources

### Official Documentation
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **YouTube API**: https://developers.google.com/youtube/v3
- **Playwright**: https://playwright.dev/python/

### Community Resources
- **FastAPI Discord**: https://discord.gg/fastapi
- **Streamlit Forum**: https://discuss.streamlit.io/
- **Stack Overflow**: Tag questions with relevant tech

### Project Documentation
- **Setup Guide**: `docs/SETUP_GUIDE.md` (to be created)
- **API Docs**: http://localhost:8000/docs (auto-generated)
- **Architecture**: `docs/technical/ARCHITECTURE.md` (existing)

### Getting Help
1. Check this plan document first
2. Review logs: `docker logs songs-backend` or `docker logs songs-frontend`
3. Search existing issues in project repository
4. Create new issue with detailed description

---

## Changelog

### Version 1.0.0 (Planned - 2025-11-16)
- Initial implementation plan created
- 8-week development timeline
- Cost-optimized architecture
- Docker-based deployment
- SQLite database
- FastAPI + Streamlit stack
- Suno.com integration (API or Playwright)
- YouTube Data API v3 integration
- JWT authentication
- Mobile-friendly web UI

---

## Appendix

### A. Environment Setup Commands

```bash
# Clone repository (if not already done)
git clone <repo-url>
cd songs-gen

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or vim, code, etc.

# Generate secret key
openssl rand -hex 32

# Create data directories
mkdir -p data downloads

# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### B. Database Management

```bash
# Access SQLite database
docker exec -it songs-backend sqlite3 data/songs.db

# Backup database
docker exec songs-backend sqlite3 data/songs.db ".backup '/app/data/songs.db.backup'"

# Restore database
docker exec songs-backend sqlite3 data/songs.db ".restore '/app/data/songs.db.backup'"

# Export to SQL
docker exec songs-backend sqlite3 data/songs.db .dump > backup.sql

# Import from SQL
docker exec -i songs-backend sqlite3 data/songs.db < backup.sql
```

### C. Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# Check resource usage
docker stats

# Access backend shell
docker exec -it songs-backend bash

# Access frontend shell
docker exec -it songs-frontend bash

# Remove all containers and volumes (CAUTION: DATA LOSS)
docker-compose down -v

# View backend logs
docker logs songs-backend --tail 100 -f

# View frontend logs
docker logs songs-frontend --tail 100 -f
```

### D. Python Development Commands

```bash
# Install dependencies locally (for IDE)
cd backend
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt

# Run tests (backend)
cd backend
pytest

# Format code
black .
isort .

# Type checking
mypy app/

# Linting
ruff check .
```

---

**Document Status**: ✅ Approved for Implementation
**Next Review**: After Phase 1 completion
**Owner**: Development Team
**Last Updated**: 2025-11-16
