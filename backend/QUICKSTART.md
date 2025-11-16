# Backend Quick Start Guide

## Starting the Backend

```bash
cd /home/user/songs-gen/backend

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Starting up Song Automation API...
INFO:     Database initialized
INFO:     SQLite journal mode: wal
INFO:     File watcher started monitoring: ./generated/songs
INFO:     Worker pool started with 2 workers
INFO:     Worker 0 started
INFO:     Worker 1 started
INFO:     Application startup complete
```

## Testing the File Watcher

### 1. Create a Test Song

```bash
mkdir -p /home/user/songs-gen/generated/songs

cat > /home/user/songs-gen/generated/songs/my-test-song.md << 'EOF'
# My Test Song

## Style Prompt
Pop, upbeat, catchy melody, 120 BPM, major key, energetic

## Lyrics
[Verse 1]
Walking down the street today
Feeling good in every way
Sun is shining bright and clear
Nothing but good vibes here

[Chorus]
This is MY TEST SONG!
Singing all day long
This is MY TEST SONG!
Everything feels right, nothing's wrong

[Verse 2]
Testing automation now
File watcher works, wow!
Backend processing the queue
Everything working smooth and true

[Chorus]
This is MY TEST SONG!
Singing all day long
This is MY TEST SONG!
Everything feels right, nothing's wrong
EOF
```

### 2. Watch the Logs

You should see:
```
INFO:     New song file detected: ./generated/songs/my-test-song.md
INFO:     Song created in database: my-test-song (My Test Song)
```

### 3. Verify in Database

```bash
sqlite3 /home/user/songs-gen/data/songs.db

# Check the song was created
SELECT id, title, status, genre FROM songs;

# Check if task was created (if AUTO_UPLOAD_TO_SUNO=true)
SELECT id, task_type, status, song_id FROM task_queue;
```

## API Endpoints

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=changeme"

# Save the token
export TOKEN="<access_token from response>"
```

### System Status

```bash
# Check system health
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/status | jq
```

### Songs

```bash
# List all songs
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/songs | jq

# Get specific song
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/songs/my-test-song | jq
```

### Task Queue

```bash
# List pending tasks
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/queue?status=pending" | jq

# Create manual task
curl -X POST http://localhost:8000/api/v1/queue \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "suno_upload",
    "song_id": "my-test-song",
    "priority": 5
  }' | jq
```

## Configuration

### Environment Variables (.env)

```bash
# Create .env file
cat > /home/user/songs-gen/backend/.env << 'EOF'
# Application
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=sqlite+aiosqlite:////app/data/songs.db

# File Paths
WATCH_FOLDER=./generated/songs
DOWNLOAD_FOLDER=./downloads
DATA_FOLDER=./data

# Workers
WORKER_COUNT=2
WORKER_CHECK_INTERVAL=60
WORKER_MAX_RETRIES=3
AUTO_UPLOAD_TO_SUNO=false

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme
EOF
```

### Enable Auto-Upload to Suno

```bash
# In .env, set:
AUTO_UPLOAD_TO_SUNO=true
```

Now when a new song file is detected, it will automatically:
1. Create Song record
2. Create TaskQueue record with task_type="suno_upload"
3. Worker will pick it up and process (placeholder in Phase 2B)

## Monitoring Workers

### Check Worker Activity

```bash
# Watch the logs in real-time
tail -f /var/log/songs-backend.log

# Or if running with uvicorn --reload, watch console output
```

### Manually Create Tasks

```bash
# Create a task for testing
curl -X POST http://localhost:8000/api/v1/queue \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "evaluate",
    "song_id": "my-test-song",
    "priority": 10,
    "payload": "{\"test\": true}"
  }'

# Watch worker pick it up (check logs)
# Task will be processed within 60 seconds (WORKER_CHECK_INTERVAL)
```

## Troubleshooting

### File Watcher Not Detecting Files

```bash
# Check watch folder exists
ls -la /home/user/songs-gen/generated/songs

# Check permissions
chmod -R 755 /home/user/songs-gen/generated

# Check logs for errors
grep "file_watcher" /var/log/songs-backend.log
```

### Workers Not Processing Tasks

```bash
# Check worker status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/status | jq '.workers'

# Check for pending tasks
sqlite3 /home/user/songs-gen/data/songs.db \
  "SELECT * FROM task_queue WHERE status='pending';"

# Check for failed tasks
sqlite3 /home/user/songs-gen/data/songs.db \
  "SELECT id, task_type, error_message FROM task_queue WHERE status='failed';"
```

### Database Locked Errors

```bash
# Verify WAL mode is enabled
sqlite3 /home/user/songs-gen/data/songs.db "PRAGMA journal_mode;"
# Should output: wal

# Check for stale locks
sqlite3 /home/user/songs-gen/data/songs.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

## Development Workflow

### 1. Create Song with CLI (existing workflow)

```bash
# Use your existing CLI tools
cd /home/user/songs-gen/tools
# ... create song as usual
```

### 2. Song Automatically Detected

The file watcher will:
- Detect the new .md file
- Parse metadata
- Create database record
- Optionally queue for Suno upload

### 3. Workers Process Tasks

Background workers will:
- Pick up tasks from queue
- Execute them (placeholders for now)
- Update status
- Retry on failure

### 4. Monitor Progress

```bash
# Check system status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/status

# Check specific song
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/songs/<song-id>
```

## Next Steps

Phase 2B is complete. Next:

**Phase 3: Suno Integration**
- Implement Playwright automation for Suno.com
- Real `suno_upload` task execution
- Real `suno_download` task execution
- Download audio files to `downloads/` folder

**Phase 4: Evaluation System**
- Implement `evaluate` task execution
- Audio quality checks
- Score calculation

**Phase 5: YouTube Integration**
- Implement `youtube_upload` task execution
- OAuth2 authentication
- Video creation and upload

## Support

For issues or questions:
1. Check logs in console or log files
2. Verify configuration in `.env`
3. Check database with sqlite3
4. Review PHASE_2B_IMPLEMENTATION.md for details
