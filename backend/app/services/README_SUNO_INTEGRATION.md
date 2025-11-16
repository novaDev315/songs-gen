# Suno Integration - Technical Documentation

## Overview

This document describes the Suno.com integration for automated song generation. The integration uses Playwright-based browser automation to upload songs and monitor generation status.

⚠️ **CRITICAL**: See `/backend/SUNO_INTEGRATION_WARNING.md` for ToS compliance requirements!

---

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Song Automation Pipeline                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  File Watcher   │
                    │  (Detects new   │
                    │   .md files)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Song Record   │
                    │   (Database)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Task Queue    │
                    │  (suno_upload)  │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      Background Worker       │
              │  execute_suno_upload()       │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │       Suno Client            │
              │  (Playwright Automation)     │
              │  - login()                   │
              │  - upload_song()             │
              │  - check_status()            │
              └──────────────┬───────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Suno.com     │
                    │  (Web Browser)  │
                    └────────┬────────┘
                             │
                             ▼ (Job ID returned)
                    ┌─────────────────┐
                    │   SunoJob DB    │
                    │   (Tracking)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Task Queue    │
                    │ (suno_download) │
                    └────────┬────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │      Background Worker       │
              │  execute_suno_download()     │
              └──────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │       Suno Client            │
              │  check_status()              │
              └──────────────┬───────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
           ▼                          ▼
    ┌──────────┐              ┌──────────────┐
    │Processing│              │  Completed   │
    │(Retry)   │              │  (Download)  │
    └──────────┘              └──────┬───────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Download Manager│
                            │ (Get audio file)│
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Evaluation     │
                            │  (Next phase)   │
                            └─────────────────┘
```

---

## File Structure

```
backend/
├── app/
│   ├── main.py                        # Added cleanup handler
│   ├── services/
│   │   ├── suno_client.py             # NEW: Playwright client
│   │   ├── worker.py                  # UPDATED: Integration
│   │   └── README_SUNO_INTEGRATION.md # This file
│   └── ...
├── SUNO_INTEGRATION_WARNING.md        # NEW: ToS compliance guide
└── ...
```

---

## Suno Client (`suno_client.py`)

### Class: `SunoClient`

Browser automation client for Suno.com using Playwright.

**Features:**
- Headless Chrome browser
- Session persistence (stays logged in)
- Automatic browser restart every 100 operations (prevents memory leaks)
- Exponential backoff retry logic (max 3 retries)
- Anti-detection measures (custom user-agent, hide webdriver)
- Comprehensive error handling

**Lifecycle:**

```python
# Initialize browser
client = SunoClient()
await client.initialize()  # Starts Playwright Chrome

# Login (session persists)
await client.login()  # Only needed once per browser session

# Upload song
result = await client.upload_song(
    style_prompt="pop, upbeat, catchy",
    lyrics="[Verse 1]\nLyrics here...",
    title="My Song"
)
# Returns: {'job_id': 'suno_xxx', 'status': 'processing'}

# Check status (call repeatedly until completed)
status = await client.check_status(result['job_id'])
# Returns: {'status': 'completed', 'audio_url': 'https://...'}

# Cleanup (on shutdown)
await client.cleanup()  # Closes browser
```

**Singleton Pattern:**

```python
# Use helper function for singleton instance
from app.services.suno_client import get_suno_client

client = await get_suno_client()  # Same instance every time
```

**Browser Lifecycle Management:**

```python
# Browser auto-restarts after 100 operations
client.operations_count  # Tracked internally
# At 100: browser closes, reinitializes, re-logins automatically
```

### Methods

#### `initialize() -> None`

Starts Playwright browser with anti-detection measures.

**Configuration:**
- Headless mode
- 1920x1080 viewport
- Chrome user-agent
- Hidden webdriver property
- No sandbox (for Docker)

#### `login(force: bool = False) -> bool`

Logs into Suno.com.

**Arguments:**
- `force`: Re-login even if already logged in

**Returns:**
- `True` if successful

**Behavior:**
- Checks session age (< 1 hour = skip login)
- Retries 3 times with exponential backoff
- Stores login time for session validation

**⚠️ PLACEHOLDER**: Actual login flow commented out until ToS verified!

#### `upload_song(style_prompt: str, lyrics: str, title: Optional[str]) -> Dict`

Uploads song to Suno for generation.

**Arguments:**
- `style_prompt`: Style description (e.g., "pop, female vocals, upbeat")
- `lyrics`: Song lyrics with structure tags ([Verse], [Chorus], etc.)
- `title`: Optional song title

**Returns:**
```python
{
    'job_id': 'suno_1234567890_5678',
    'status': 'processing',
    'message': 'Song uploaded successfully'
}
```

**Validation:**
- Ensures logged in before upload
- Validates non-empty style_prompt and lyrics
- Warns if lyrics > 5000 characters

**⚠️ PLACEHOLDER**: Actual upload flow commented out until ToS verified!

#### `check_status(job_id: str) -> Dict`

Checks generation status of Suno job.

**Arguments:**
- `job_id`: Suno job identifier from `upload_song()`

**Returns (Processing):**
```python
{
    'status': 'processing',
    'progress': 45.5  # Optional percentage
}
```

**Returns (Completed):**
```python
{
    'status': 'completed',
    'audio_url': 'https://cdn.suno.com/audio/xxx.mp3'
}
```

**Returns (Failed):**
```python
{
    'status': 'failed',
    'error': 'Generation timeout or error message'
}
```

**⚠️ PLACEHOLDER**: Actual status check commented out until ToS verified!

### Error Handling

**Custom Exceptions:**

```python
class SunoClientError(Exception):
    """Base exception for all Suno errors"""

class SunoAuthenticationError(SunoClientError):
    """Login failed"""

class SunoUploadError(SunoClientError):
    """Upload failed"""

class SunoStatusCheckError(SunoClientError):
    """Status check failed"""
```

**Retry Logic:**

All operations retry up to 3 times with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 2^1 = 2 seconds
- Attempt 3: Wait 2^2 = 4 seconds
- Fail: Raise exception

---

## Worker Integration (`worker.py`)

### `execute_suno_upload(task, db)`

Executes Suno upload task from queue.

**Flow:**

1. Get song from database by `task.song_id`
2. Update song status to `'uploading'`
3. Get Suno client (singleton)
4. Call `client.upload_song()` with song data
5. Create or update `SunoJob` record with job ID
6. Update song status to `'generating'`
7. Create `suno_download` task (higher priority)

**Error Handling:**

- `SunoClientError`: Mark song as failed, raise to trigger retry
- Other errors: Mark song as failed, log with traceback

**Database Updates:**

```python
# Song status progression
'pending' -> 'uploading' -> 'generating' -> (download phase)

# SunoJob record created
{
    'song_id': task.song_id,
    'suno_job_id': 'suno_xxx',
    'status': 'processing'
}

# New task queued
TaskQueue(task_type='suno_download', song_id=task.song_id)
```

### `execute_suno_download(task, db)`

Executes Suno download task from queue.

**Flow:**

1. Get most recent `SunoJob` for song
2. Call `client.check_status(job_id)`
3. Branch based on status:
   - **Processing**: Raise exception to retry later
   - **Completed**: Download audio, queue evaluation
   - **Failed**: Mark failed, raise exception

**Status: Processing**

```python
# Still generating, retry later
raise Exception("Song still processing, will retry")
# Worker's retry logic will re-queue this task
```

**Status: Completed**

```python
# Update SunoJob
suno_job.status = 'completed'
suno_job.audio_url = status['audio_url']
suno_job.completed_at = datetime.utcnow()

# Download audio
download_manager.download_from_suno_job(suno_job.id)

# Update song
song.status = 'downloaded'

# Queue evaluation
TaskQueue(task_type='evaluate', song_id=song.id)
```

**Status: Failed**

```python
# Update records
suno_job.status = 'failed'
suno_job.error_message = status['error']
song.status = 'failed'

# Raise exception (task marked failed)
raise Exception("Suno generation failed")
```

---

## Application Lifecycle (`main.py`)

### Startup

No Suno-specific startup actions needed. Browser initializes on first use (lazy loading).

### Shutdown

```python
# In lifespan shutdown
await cleanup_suno_client()
```

Closes browser and frees Playwright resources.

**Importance:**
- Prevents zombie browser processes
- Releases memory
- Allows graceful shutdown

---

## Configuration (`config.py`)

### Environment Variables

```bash
# Suno credentials (required for actual implementation)
SUNO_EMAIL=your-email@example.com
SUNO_PASSWORD=your-password

# Worker settings
WORKER_COUNT=2                  # Number of concurrent workers
WORKER_CHECK_INTERVAL=60        # Seconds between queue checks
WORKER_MAX_RETRIES=3            # Max retries per task

# Auto-upload
AUTO_UPLOAD_TO_SUNO=false       # Auto-queue new songs
```

**Security:**
- Passwords stored in `.env` (gitignored)
- Never commit credentials!

---

## Database Schema

### `suno_jobs` Table

Tracks Suno generation jobs.

```sql
CREATE TABLE suno_jobs (
    id INTEGER PRIMARY KEY,
    song_id INTEGER NOT NULL REFERENCES songs(id),
    suno_job_id VARCHAR(100),           -- Suno's job identifier
    status VARCHAR(20),                 -- 'processing', 'completed', 'failed'
    audio_url VARCHAR(500),             -- Download URL (when completed)
    error_message TEXT,                 -- Error if failed
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

**Status Values:**
- `processing`: Suno is generating audio
- `completed`: Audio ready, URL available
- `failed`: Generation failed, error recorded

---

## Status Flow

### Song Status Progression

```
pending           # Initial state (file detected)
    ↓
uploading         # Worker executing suno_upload
    ↓
generating        # Uploaded to Suno, job ID received
    ↓
downloaded        # Audio downloaded from Suno
    ↓
evaluated         # Quality check complete
    ↓
uploaded          # Uploaded to YouTube (Phase 5)
```

### Failure Paths

```
Any state → failed   # Error occurred, check error_message
```

---

## Retry Logic

### Task Queue Retries

**Automatic Retry:**
```python
# In worker.py execute_task()
try:
    await execute_suno_upload(task, db)
except Exception as e:
    task.retry_count += 1
    if task.retry_count < task.max_retries:
        task.status = 'pending'  # Retry
    else:
        task.status = 'failed'   # Give up
```

**Retry Scenarios:**

1. **Suno upload timeout**: Retry 3 times
2. **Status check - still processing**: Retry indefinitely (normal behavior)
3. **Network error**: Retry 3 times
4. **Suno generation failed**: Don't retry (mark failed)

---

## Monitoring and Debugging

### Logging

**Log Levels:**

```python
# Info: Normal operations
logger.info("Uploading song 123 to Suno")
logger.info("Suno job abc completed")

# Warning: Retryable errors
logger.warning("Upload timeout, retrying...")

# Error: Failures
logger.error("Suno upload failed after 3 retries")

# Critical: System issues
logger.critical("⚠️ Multiple account errors - possible ban!")
```

### Health Checks

**Check Suno Integration Status:**

```bash
# API endpoint to check Suno client
GET /api/v1/system/status

# Response includes:
{
    "suno_client": {
        "initialized": true,
        "logged_in": true,
        "operations_count": 45,
        "last_operation": "2025-11-16T12:34:56Z"
    }
}
```

### Debugging Tips

**Issue: Songs stuck in 'uploading'**

```bash
# Check worker logs
docker logs songs-backend | grep "suno_upload"

# Check if browser is running
docker exec songs-backend ps aux | grep chromium

# Restart workers
docker restart songs-backend
```

**Issue: "Song still processing" forever**

```bash
# Check SunoJob status
sqlite3 data/songs.db "SELECT * FROM suno_jobs WHERE status='processing';"

# Manually check Suno.com for job ID
# If completed on Suno but not detected, status check may be broken
```

**Issue: Browser memory leak**

```bash
# Browser auto-restarts at 100 operations
# Check if restart is happening
docker logs songs-backend | grep "browser restart"

# If not restarting, check operations counter
# May need to lower MAX_OPERATIONS_BEFORE_RESTART
```

---

## Testing

### Unit Tests

**Test Suno Client (Placeholder):**

```python
# tests/services/test_suno_client.py

import pytest
from app.services.suno_client import SunoClient

@pytest.mark.asyncio
async def test_suno_upload_placeholder():
    """Test upload returns mock job ID."""
    client = SunoClient()
    await client.initialize()

    result = await client.upload_song(
        style_prompt="pop",
        lyrics="[Verse 1]\nTest",
        title="Test Song"
    )

    assert 'job_id' in result
    assert result['status'] == 'processing'

    await client.cleanup()
```

### Integration Tests

**Test Full Upload Flow:**

```python
@pytest.mark.asyncio
async def test_suno_upload_task_execution(db_session):
    """Test worker executes suno_upload task."""

    # Create song
    song = Song(title="Test", lyrics="...", style_prompt="...")
    db_session.add(song)
    await db_session.commit()

    # Create task
    task = TaskQueue(task_type='suno_upload', song_id=song.id)
    db_session.add(task)
    await db_session.commit()

    # Execute task
    worker = BackgroundWorker(worker_id=0)
    await worker.execute_task(task, db_session)

    # Verify SunoJob created
    suno_job = await db_session.execute(
        select(SunoJob).where(SunoJob.song_id == song.id)
    )
    assert suno_job is not None
    assert suno_job.status == 'processing'
```

---

## Performance Considerations

### Browser Overhead

**Resource Usage:**
- Memory: ~200-500 MB per browser instance
- CPU: Moderate during page loads
- Disk: Minimal (temporary files)

**Optimization:**
- Single browser instance (singleton)
- Headless mode (no GPU rendering)
- Auto-restart to free memory

### Concurrency

**Current Design:**
- 1 Suno client instance
- Multiple workers (2 default)
- Workers share the same browser

**Limitation:**
- Browser operations are sequential
- Parallel uploads may cause race conditions

**Future Improvement:**
```python
# Use browser pool for parallel uploads
class SunoClientPool:
    def __init__(self, pool_size=2):
        self.clients = [SunoClient() for _ in range(pool_size)]
```

### Rate Limiting

**Recommended Limits:**
```python
# Respect Suno's servers
MAX_UPLOADS_PER_HOUR = 10
MAX_UPLOADS_PER_DAY = 50

# Add delays between operations
DELAY_BETWEEN_UPLOADS = 5  # seconds
```

---

## Security Considerations

### Credentials Storage

**Do:**
- ✅ Store in `.env` file
- ✅ Use environment variables
- ✅ Add `.env` to `.gitignore`

**Don't:**
- ❌ Hardcode in source files
- ❌ Commit to git
- ❌ Log passwords

### Browser Security

**Anti-Detection:**
- Realistic user-agent
- Hide webdriver property
- Human-like delays (future)

**Risk:**
- Browser automation may be detected
- Suno may implement CAPTCHA
- Account suspension risk (see WARNING doc)

---

## Troubleshooting

### Common Issues

**1. Playwright not installed**

```bash
# Error: playwright._impl._api_types.Error: Executable doesn't exist
# Fix:
playwright install chromium
```

**2. Browser fails to start in Docker**

```bash
# Error: Could not find browser
# Fix: Ensure Dockerfile installs Playwright
RUN playwright install --with-deps chromium
```

**3. Login fails (when implemented)**

```bash
# Check credentials
echo $SUNO_EMAIL
echo $SUNO_PASSWORD

# Check Suno.com is accessible
curl -I https://suno.com

# Check selectors are correct (may have changed)
# Update selectors in suno_client.py
```

**4. Status check never completes**

```bash
# Suno generation may be slow
# Check actual job on Suno.com
# Increase timeout if needed
```

---

## Future Enhancements

### 1. Official API Integration

When/if Suno releases an API:

```python
# Replace Playwright with API client
class SunoAPIClient:
    async def upload_song(self, style, lyrics):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.suno.com/v1/songs",
                json={"style": style, "lyrics": lyrics},
                headers={"Authorization": f"Bearer {api_key}"}
            )
            return response.json()
```

**Benefits:**
- More reliable
- Faster
- No browser overhead
- Official support

### 2. Browser Pool

Multiple browser instances for parallel uploads:

```python
class SunoClientPool:
    def __init__(self, pool_size=3):
        self.pool = [SunoClient() for _ in range(pool_size)]

    async def get_client(self):
        # Return least-busy client
        return min(self.pool, key=lambda c: c.operations_count)
```

### 3. Real-Time Status Updates

WebSocket for live status updates:

```python
# In worker, emit events
await websocket_manager.broadcast({
    'type': 'suno_status',
    'song_id': song.id,
    'status': 'uploading'
})
```

### 4. Retry Strategy Improvements

Adaptive retry delays:

```python
# Exponential backoff with jitter
delay = (2 ** attempt) + random.uniform(0, 1)
```

### 5. Metrics and Analytics

Track Suno performance:

```python
suno_metrics = {
    'avg_generation_time': timedelta,
    'success_rate': float,
    'uploads_today': int,
    'failures_by_reason': dict
}
```

---

## API Integration Checklist

If Suno releases an official API, follow this migration checklist:

- [ ] Obtain API key from Suno
- [ ] Read API documentation
- [ ] Create new `SunoAPIClient` class
- [ ] Implement `create_song()` method
- [ ] Implement `get_job_status()` method
- [ ] Add authentication (Bearer token)
- [ ] Handle rate limits (429 responses)
- [ ] Update worker to use API client
- [ ] Deprecate Playwright client
- [ ] Update tests
- [ ] Update documentation

---

## Support

**For implementation issues:**
- Check logs: `docker logs songs-backend`
- Review ToS compliance: `backend/SUNO_INTEGRATION_WARNING.md`
- Debug with Python: `python -m pdb app/services/suno_client.py`

**For ToS questions:**
- Contact Suno support: support@suno.com
- Review community: r/SunoAI on Reddit

**For technical questions:**
- See main project documentation
- Open GitHub issue (for code bugs, not ToS advice)

---

*Last Updated: 2025-11-16*
*Phase 3 Implementation - Suno Integration*
