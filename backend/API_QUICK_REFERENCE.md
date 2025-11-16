# API Quick Reference - Phase 2A

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All endpoints require JWT authentication via Bearer token:
```
Authorization: Bearer <access_token>
```

---

## Songs API

### List Songs
```http
GET /songs?status=pending&genre=pop&skip=0&limit=50
```

### Get Song
```http
GET /songs/{song_id}
```

### Create Song
```http
POST /songs
Content-Type: application/json

{
  "title": "My Song",
  "genre": "pop",
  "style_prompt": "upbeat pop, female vocals",
  "lyrics": "[Verse 1]\nLyrics here...",
  "file_path": "/path/to/song.md"
}
```

### Update Song
```http
PUT /songs/{song_id}
Content-Type: application/json

{
  "status": "pending"
}
```

### Delete Song
```http
DELETE /songs/{song_id}
```

### Get Pipeline Status
```http
GET /songs/{song_id}/status
```

### Upload to Suno
```http
POST /songs/{song_id}/upload-to-suno?priority=50
```

### Download from Suno
```http
POST /songs/{song_id}/download?priority=50
```

---

## Queue API

### List Tasks
```http
GET /queue/tasks?status=pending&task_type=suno_upload&skip=0&limit=50
```

### Get Queue Stats
```http
GET /queue/stats
```

### Enqueue Task
```http
POST /queue/tasks
Content-Type: application/json

{
  "task_type": "suno_upload",
  "song_id": "abc-123",
  "priority": 50
}
```

### Cancel Task
```http
DELETE /queue/tasks/{task_id}
```

### Retry Task
```http
POST /queue/tasks/{task_id}/retry
```

### Clear Completed
```http
POST /queue/clear-completed
```

### Clear Failed
```http
POST /queue/clear-failed
```

---

## Evaluation API

### List Evaluations
```http
GET /evaluations?approved=true&min_rating=7&skip=0&limit=50
```

### Get Evaluation
```http
GET /evaluations/{evaluation_id}
```

### Create Evaluation
```http
POST /evaluations
Content-Type: application/json

{
  "song_id": "abc-123",
  "audio_quality_score": 85.5,
  "duration_seconds": 180.2,
  "file_size_mb": 4.5
}
```

### Update Evaluation
```http
PUT /evaluations/{evaluation_id}
Content-Type: application/json

{
  "manual_rating": 8,
  "approved": true,
  "notes": "Great quality!"
}
```

### Approve Song
```http
POST /evaluations/{evaluation_id}/approve
```

### Reject Song
```http
POST /evaluations/{evaluation_id}/reject?notes=Poor+audio+quality
```

### Batch Approve
```http
POST /evaluations/batch-approve
Content-Type: application/json

{
  "song_ids": ["abc-123", "def-456"],
  "notes": "All approved for upload"
}
```

### Get Pending
```http
GET /evaluations/pending?limit=50
```

---

## YouTube API

### List Uploads
```http
GET /youtube/uploads?upload_status=published&skip=0&limit=50
```

### Get Upload
```http
GET /youtube/uploads/{upload_id}
```

### Upload to YouTube
```http
POST /youtube/upload
Content-Type: application/json

{
  "song_id": "abc-123",
  "title": "My Amazing Song",
  "description": "Created with AI",
  "tags": "music,ai,pop",
  "privacy": "private"
}
```

### Get OAuth URL
```http
GET /youtube/oauth-url
```

### OAuth Callback
```http
POST /youtube/oauth-callback
Content-Type: application/json

{
  "code": "oauth_code_from_google",
  "state": "csrf_state_token"
}
```

### Delete Upload Record
```http
DELETE /youtube/uploads/{upload_id}
```

---

## Response Formats

### Success Response (Single Item)
```json
{
  "id": "abc-123",
  "title": "My Song",
  "status": "pending",
  "created_at": "2024-01-01T12:00:00",
  ...
}
```

### Success Response (List)
```json
{
  "items": [
    { "id": "abc-123", ... },
    { "id": "def-456", ... }
  ],
  "meta": {
    "total": 100,
    "skip": 0,
    "limit": 50,
    "has_more": true
  }
}
```

### Error Response
```json
{
  "detail": "Song with ID 'abc-123' not found"
}
```

---

## Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Common Query Parameters

- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return (max 100-200)
- `status` - Filter by status
- `genre` - Filter by genre
- `task_type` - Filter by task type
- `approved` - Filter by approval status
- `min_rating` - Minimum rating filter

---

## Song Status Flow

```
pending → uploading → generating → downloaded → evaluated → uploaded
                                                    ↓
                                                 failed
```

## Task Types

- `suno_upload` - Upload song to Suno
- `suno_download` - Download generated audio
- `youtube_upload` - Upload to YouTube
- `evaluate` - Run quality evaluation

## Upload Privacy Options

- `private` - Only you can view
- `unlisted` - Anyone with link can view
- `public` - Everyone can view

