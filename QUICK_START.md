# Phase 1: Quick Start Guide

## Overview

Phase 1 Core Infrastructure is complete. This guide helps you get started quickly.

## Prerequisites

- Docker and Docker Compose installed
- Ports 8000 (backend) and 8501 (frontend) available

## Start the System (3 commands)

```bash
# 1. Navigate to project
cd /home/user/songs-gen

# 2. Start containers
docker compose up -d

# 3. Check status
docker compose ps
```

Expected output:
```
NAME              IMAGE                STATUS         PORTS
songs-backend     songs-gen-backend    Up (healthy)   0.0.0.0:8000->8000/tcp
songs-frontend    songs-gen-frontend   Up (healthy)   0.0.0.0:8501->8501/tcp
```

## Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health

## Test Authentication

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme123!"}'

# You'll get:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
#   "token_type": "bearer"
# }

# Copy the access_token and test protected endpoint
export TOKEN="YOUR_ACCESS_TOKEN_HERE"

curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# You'll get:
# {
#   "id": 1,
#   "username": "admin",
#   "role": "admin",
#   "created_at": "2025-01-16T..."
# }
```

## View Logs

```bash
# Backend logs (shows startup, DB init, backup scheduler)
docker logs songs-backend

# Frontend logs
docker logs songs-frontend

# Follow logs in real-time
docker logs songs-backend -f
```

## Verify Database

```bash
# Check tables exist
docker exec songs-backend sqlite3 /app/data/songs.db ".tables"

# Expected:
# evaluations    suno_jobs      task_queue     youtube_uploads
# songs          users

# Check WAL mode enabled
docker exec songs-backend sqlite3 /app/data/songs.db "PRAGMA journal_mode;"

# Expected: wal

# View admin user
docker exec songs-backend sqlite3 /app/data/songs.db \
  "SELECT id, username, role, created_at FROM users;"

# Expected:
# 1|admin|admin|2025-01-16...
```

## Common Commands

```bash
# Stop containers
docker compose down

# Start containers
docker compose up -d

# Restart containers
docker compose restart

# View container status
docker compose ps

# Rebuild after code changes
docker compose build
docker compose up -d

# Run tests
docker exec songs-backend pytest -v

# Access backend shell
docker exec -it songs-backend bash

# Access database shell
docker exec -it songs-backend sqlite3 /app/data/songs.db
```

## Important Security Notes

### CHANGE ADMIN PASSWORD IMMEDIATELY

1. Login to frontend: http://localhost:8501
2. Or update .env file:
   ```bash
   # Edit .env
   ADMIN_PASSWORD=YourNewSecurePassword123!

   # Restart backend
   docker restart songs-backend
   ```

### SECRET_KEY

The .env file contains a randomly generated SECRET_KEY. This is used for JWT signing.

**NEVER commit .env to git!** It's already in .gitignore.

## File Locations

### Configuration
- `/home/user/songs-gen/.env` - Environment variables (GITIGNORED)
- `/home/user/songs-gen/.env.example` - Template for .env
- `/home/user/songs-gen/docker-compose.yml` - Container orchestration

### Backend
- `/home/user/songs-gen/backend/app/main.py` - FastAPI app entry point
- `/home/user/songs-gen/backend/app/config.py` - Settings
- `/home/user/songs-gen/backend/app/database.py` - Database connection
- `/home/user/songs-gen/backend/app/models/` - Database models
- `/home/user/songs-gen/backend/app/api/auth.py` - Authentication endpoints
- `/home/user/songs-gen/backend/scripts/backup.sh` - Automated backup script

### Frontend
- `/home/user/songs-gen/frontend/streamlit_app.py` - Streamlit UI

### Data
- `/home/user/songs-gen/data/songs.db` - SQLite database (created on startup)
- `/home/user/songs-gen/data/backups/` - Daily backups (3 AM)
- `/home/user/songs-gen/downloads/` - Downloaded audio files
- `/home/user/songs-gen/generated/songs/` - Claude-generated song files

## API Endpoints (Phase 1)

### Authentication
- `POST /api/v1/auth/login` - Login (returns access + refresh tokens)
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout (invalidates refresh token)
- `GET /api/v1/auth/me` - Get current user (requires auth)

### System
- `GET /health` - Health check

### Coming in Phase 2
- Song management endpoints
- Task queue endpoints
- File watcher service

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8000
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

### Backend won't start
```bash
# Check logs
docker logs songs-backend

# Common issues:
# 1. Missing SECRET_KEY in .env
# 2. Database file permissions
# 3. Port conflict
```

### Frontend can't connect
```bash
# Verify backend is healthy
curl http://localhost:8000/health

# Check network
docker network inspect songs-network

# Restart frontend
docker restart songs-frontend
```

### Database locked
```bash
# SQLite write lock - restart backend
docker restart songs-backend
```

## Database Schema

### users
- id, username (unique), password_hash, role
- refresh_token_hash, refresh_token_expires_at
- created_at, last_login

### songs
- id (primary key), title, genre, style_prompt, lyrics
- file_path, status, metadata_json
- created_at, updated_at

### suno_jobs
- id, song_id (FK), suno_job_id, status
- audio_url, downloaded_path
- error_message, retry_count
- created_at, completed_at

### evaluations
- id, song_id (FK)
- audio_quality_score, duration_seconds, file_size_mb, sample_rate, bitrate
- manual_rating, approved, notes
- evaluated_by (FK to users), evaluated_at

### youtube_uploads
- id, song_id (FK), video_id, video_url
- upload_status, title, description, tags, privacy
- error_message
- uploaded_by (FK to users), uploaded_at

### task_queue (CRITICAL - persistent queue)
- id, task_type, song_id (FK), payload (JSON)
- status, priority, retry_count, max_retries
- error_message
- created_at, started_at, completed_at
- Composite index: (status, priority, created_at)

## Backup System

### Automatic Backups
- Run daily at 3 AM
- Retain last 30 days
- Compressed with gzip
- Integrity verified

### Manual Backup
```bash
# Create backup now
docker exec songs-backend /app/scripts/backup.sh

# List backups
docker exec songs-backend ls -lh /app/data/backups/
```

### Restore from Backup
```bash
# Stop backend
docker stop songs-backend

# Restore
docker exec songs-backend gunzip -c /app/data/backups/songs_YYYYMMDD_HHMMSS.db.gz > /app/data/songs.db

# Start backend
docker start songs-backend
```

## Next Steps

1. **Change admin password** (security!)
2. **Test authentication** with curl commands above
3. **Access frontend** at http://localhost:8501
4. **Review PHASE_1_COMPLETE.md** for detailed documentation
5. **Ready for Phase 2**: File watcher and background workers

## Phase 2 Preview

Coming next:
- File watcher service (monitors generated/songs/ for new files)
- Background worker system (processes task_queue)
- Song management API (CRUD operations)
- Queue management API (view/manage tasks)

## Support

For detailed documentation, see:
- `PHASE_1_COMPLETE.md` - Full Phase 1 documentation
- `docs/AUTOMATION_PIPELINE_PLAN.md` - Complete project plan
- `CLAUDE.md` - Development guidelines

## Health Check Quick Reference

```bash
# All-in-one health check
echo "=== Backend Health ===" && \
curl -s http://localhost:8000/health | jq && \
echo -e "\n=== Database Tables ===" && \
docker exec songs-backend sqlite3 /app/data/songs.db ".tables" && \
echo -e "\n=== WAL Mode ===" && \
docker exec songs-backend sqlite3 /app/data/songs.db "PRAGMA journal_mode;" && \
echo -e "\n=== Container Status ===" && \
docker compose ps
```

Expected output:
```
=== Backend Health ===
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}

=== Database Tables ===
evaluations    suno_jobs      task_queue     youtube_uploads
songs          users

=== WAL Mode ===
wal

=== Container Status ===
NAME              IMAGE                STATUS         PORTS
songs-backend     songs-gen-backend    Up (healthy)   0.0.0.0:8000->8000/tcp
songs-frontend    songs-gen-frontend   Up (healthy)   0.0.0.0:8501->8501/tcp
```

## Congratulations!

Phase 1 is complete and working. You have a production-ready foundation with:
- ✅ Docker containerization
- ✅ SQLite with WAL mode
- ✅ JWT authentication with refresh tokens
- ✅ Persistent task queue
- ✅ Automated backups
- ✅ Mobile-friendly UI
- ✅ Comprehensive tests

Ready to build Phase 2!
