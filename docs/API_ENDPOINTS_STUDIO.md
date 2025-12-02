# YouTube Studio API Endpoints

Complete API reference for the YouTube Studio video project management system.

**Last Updated**: 2025-11-30

---

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Project Management](#project-management)
- [Cover Generation](#cover-generation)
- [Lyric Timing](#lyric-timing)
- [Video Generation](#video-generation)
- [Metadata](#metadata)
- [Publishing](#publishing)
- [Progress Tracking](#progress-tracking)
- [Error Handling](#error-handling)

---

## Base URL

All endpoints are prefixed with:

```
http://localhost:8000/api/v1
```

---

## Authentication

All endpoints require JWT authentication via Bearer token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

Obtain token from `/api/v1/auth/login` endpoint.

---

## Project Management

### Create Video Project

**POST** `/studio/projects`

Create a new video project for a song.

**Request Body:**
```json
{
  "song_id": "uuid-string"
}
```

**Response:** `201 Created`
```json
{
  "id": "project-uuid",
  "song_id": "song-uuid",
  "cover_type": null,
  "cover_path": null,
  "video_style": "lyric_video",
  "lyric_style": "karaoke",
  "background_color": "#000000",
  "text_color": "#ffffff",
  "highlight_color": "#00ff00",
  "custom_title": null,
  "custom_description": null,
  "custom_tags": null,
  "privacy": "private",
  "lyric_timing_json": null,
  "preview_path": null,
  "output_path": null,
  "status": "draft",
  "progress": 0,
  "created_at": "2025-11-30T12:00:00Z",
  "updated_at": "2025-11-30T12:00:00Z"
}
```

---

### List Video Projects

**GET** `/studio/projects`

List all video projects with filtering and pagination.

**Query Parameters:**
- `status_filter` (optional): Filter by status (draft, rendering, ready, uploaded)
- `skip` (default: 0): Pagination offset
- `limit` (default: 50, max: 100): Number of results

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "project-uuid",
      "song_id": "song-uuid",
      "status": "draft",
      "progress": 0,
      ...
    }
  ],
  "meta": {
    "total": 100,
    "skip": 0,
    "limit": 50,
    "has_more": true
  }
}
```

---

### Get Video Project

**GET** `/studio/projects/{project_id}`

Get video project details by ID.

**Response:** `200 OK`
```json
{
  "id": "project-uuid",
  "song_id": "song-uuid",
  "cover_type": "ai",
  "cover_path": "/covers/song-uuid_ai.png",
  ...
}
```

---

### Update Video Project

**PUT** `/studio/projects/{project_id}`

Update video project settings.

**Request Body:** (all fields optional)
```json
{
  "cover_type": "ai",
  "cover_path": "/covers/song-uuid_ai.png",
  "video_style": "static_cover",
  "lyric_style": "line_by_line",
  "background_color": "#1a1a1a",
  "text_color": "#ffffff",
  "highlight_color": "#ff0000",
  "custom_title": "My Song - Official Lyric Video",
  "custom_description": "Custom description for YouTube",
  "custom_tags": "[\"tag1\", \"tag2\"]",
  "privacy": "unlisted"
}
```

**Response:** `200 OK`
```json
{
  "id": "project-uuid",
  "song_id": "song-uuid",
  ...
}
```

---

### Delete Video Project

**DELETE** `/studio/projects/{project_id}`

Delete video project (does not delete the song).

**Response:** `200 OK`
```json
{
  "message": "Video project 'project-uuid' deleted successfully",
  "deleted_id": "project-uuid",
  "song_id": "song-uuid"
}
```

---

## Cover Generation

### List Cover Templates

**GET** `/studio/templates/covers`

List available cover templates organized by genre.

**Response:** `200 OK`
```json
{
  "templates": {
    "pop": ["gradient_bright", "neon_city", "abstract_colorful"],
    "rock": ["dark_grunge", "fire_smoke", "electric"],
    "hip-hop": ["urban_night", "gold_chains", "street_art"],
    "edm": ["laser_grid", "spectrum", "dj_silhouette"],
    "jazz": ["vintage_sepia", "piano_keys", "smoky_club"],
    "country": ["sunset_field", "acoustic_wood", "barn"]
  },
  "note": "Phase 2 feature - templates will be fully implemented with actual image generation"
}
```

---

### Generate Template Cover

**POST** `/studio/projects/{project_id}/cover/template`

Generate cover image from a template.

**Request Body:**
```json
{
  "template_id": "gradient_bright"
}
```

**Response:** `200 OK`
```json
{
  "cover_path": "/covers/song-uuid_template.png",
  "cover_type": "template"
}
```

**Errors:**
- `404`: Project or song not found
- `500`: Cover generation failed

---

### Generate AI Cover

**POST** `/studio/projects/{project_id}/cover/ai`

Generate AI cover image via OpenRouter.

**Request Body:**
```json
{
  "prompt": "Custom prompt for AI generation (optional)"
}
```

If `prompt` is not provided, auto-generates prompt from song metadata.

**Response:** `200 OK`
```json
{
  "cover_path": "/covers/song-uuid_ai.png",
  "cover_type": "ai"
}
```

**Errors:**
- `404`: Project or song not found
- `400`: Invalid prompt or missing OPENROUTER_API_KEY
- `500`: AI generation failed

**Requirements:**
- `OPENROUTER_API_KEY` must be set in environment

---

### Upload Custom Cover

**POST** `/studio/projects/{project_id}/cover/upload`

Upload custom cover image.

**Request:** `multipart/form-data`
- `file`: Image file (JPG, PNG, max 5MB)

**Response:** `200 OK`
```json
{
  "cover_path": "/covers/song-uuid_upload.png",
  "cover_type": "upload"
}
```

**Processing:**
- Image automatically resized to 1280x720
- Maintains aspect ratio with LANCZOS resampling

**Errors:**
- `404`: Project not found
- `400`: Invalid file type
- `413`: File too large (>5MB)
- `500`: Upload processing failed

---

## Lyric Timing

### Sync Lyrics

**POST** `/studio/projects/{project_id}/lyrics/sync`

Generate beat-synced lyric timing.

**Request Body:**
```json
{
  "mode": "beat_synced"
}
```

**Timing Modes:**
- `beat_synced`: Analyze audio and sync to beats (default)
- `uniform`: Evenly distribute lyrics over duration
- `measures`: Sync to musical measures

**Response:** `200 OK`
```json
{
  "timing": {
    "segments": [
      {
        "start": 0.0,
        "end": 2.5,
        "text": "First line of lyrics",
        "type": "verse"
      },
      {
        "start": 2.5,
        "end": 5.0,
        "text": "Second line of lyrics",
        "type": "verse"
      }
    ],
    "duration": 180.0,
    "bpm": 120
  },
  "mode": "beat_synced"
}
```

**Errors:**
- `404`: Project, song, or audio file not found
- `500`: Timing generation failed

**Requirements:**
- Audio file must exist in `downloads/` folder

---

## Video Generation

### Generate Preview

**POST** `/studio/projects/{project_id}/preview`

Generate 30-second preview video.

**Response:** `200 OK`
```json
{
  "message": "Preview generation started",
  "project_id": "project-uuid"
}
```

**Background Task:**
- Generates 30-second preview
- Updates project status to `rendering` → `preview_ready`
- Use `/status` endpoint to track progress

**Errors:**
- `404`: Project not found
- `400`: Project missing cover image

---

### Stream Project Status (SSE)

**GET** `/studio/projects/{project_id}/status`

Stream real-time project status updates via Server-Sent Events.

**Response:** `text/event-stream`

**Event Types:**

**Progress Event:**
```json
{
  "event": "progress",
  "data": {
    "status": "rendering",
    "progress": 45,
    "preview_path": null,
    "output_path": null,
    "error_message": null
  }
}
```

**Error Event:**
```json
{
  "event": "error",
  "data": {
    "error": "Error message"
  }
}
```

**Client Usage:**
```javascript
const eventSource = new EventSource('/api/v1/studio/projects/{project_id}/status');

eventSource.addEventListener('progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Status: ${data.status}, Progress: ${data.progress}%`);

  if (data.status === 'preview_ready' || data.status === 'complete') {
    eventSource.close();
  }
});

eventSource.addEventListener('error', (event) => {
  const data = JSON.parse(event.data);
  console.error('Error:', data.error);
  eventSource.close();
});
```

**Project Statuses:**
- `draft`: Initial state
- `rendering`: Video generation in progress
- `preview_ready`: Preview video complete
- `complete`: Final video complete
- `failed`: Generation failed (see `error_message`)

---

## Metadata

### Suggest Metadata

**GET** `/studio/projects/{project_id}/metadata/suggest`

Auto-generate metadata suggestions for YouTube upload.

**Response:** `200 OK`
```json
{
  "title": "My Song - Official Lyric Video",
  "description": "Listen to \"My Song\" - a pop anthem about love and loss.\n\nLyrics:\n[Full lyrics here]\n\n#PopMusic #NewMusic #LyricVideo",
  "tags": [
    "pop music",
    "new music 2025",
    "lyric video",
    "love song",
    "official audio"
  ],
  "hashtags": [
    "#PopMusic",
    "#NewMusic",
    "#LyricVideo",
    "#2025Music"
  ]
}
```

**Metadata Generation:**
- Title: Based on song title + "- Official Lyric Video"
- Description: Auto-generated from lyrics and genre
- Tags: Genre-specific keywords
- Hashtags: Trending hashtags for genre

**Errors:**
- `404`: Project or song not found
- `500`: Metadata generation failed

---

## Publishing

### Publish Project

**POST** `/studio/projects/{project_id}/publish`

Render final video and prepare for YouTube upload.

**Response:** `200 OK`
```json
{
  "message": "Publishing started",
  "project_id": "project-uuid"
}
```

**Background Task:**
- Renders full-length video
- Updates project status to `rendering` → `complete`
- Queues YouTube upload (if configured)
- Use `/status` endpoint to track progress

**Errors:**
- `404`: Project not found
- `400`: Project missing cover image
- `409`: Project already being rendered

**Requirements:**
- Cover image must be set
- Audio file must exist

**YouTube Integration:**
- After rendering, video will be queued for YouTube upload
- Requires YouTube OAuth configuration
- Uses metadata from project settings or auto-generated suggestions

---

## Error Handling

All endpoints follow consistent error response format:

**400 Bad Request:**
```json
{
  "detail": "Validation error message"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**409 Conflict:**
```json
{
  "detail": "Conflict with current state"
}
```

**413 Payload Too Large:**
```json
{
  "detail": "File too large (max 5MB)"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Operation failed: error details"
}
```

---

## Complete Workflow Example

```bash
# 1. Create project for a song
POST /api/v1/studio/projects
{
  "song_id": "song-123"
}
# Returns: project_id = "proj-456"

# 2. Generate AI cover
POST /api/v1/studio/projects/proj-456/cover/ai
{
  "prompt": "Abstract colorful waves representing pop music"
}

# 3. Generate lyric timing
POST /api/v1/studio/projects/proj-456/lyrics/sync
{
  "mode": "beat_synced"
}

# 4. Update project settings
PUT /api/v1/studio/projects/proj-456
{
  "video_style": "lyric_video",
  "lyric_style": "karaoke",
  "text_color": "#ffffff",
  "highlight_color": "#ff0000"
}

# 5. Generate preview
POST /api/v1/studio/projects/proj-456/preview

# 6. Monitor progress via SSE
GET /api/v1/studio/projects/proj-456/status
# (Connect EventSource and wait for preview_ready)

# 7. Get metadata suggestions
GET /api/v1/studio/projects/proj-456/metadata/suggest

# 8. Update with custom metadata
PUT /api/v1/studio/projects/proj-456
{
  "custom_title": "My Song - Official Lyric Video",
  "custom_description": "Custom description",
  "custom_tags": "[\"tag1\", \"tag2\"]",
  "privacy": "public"
}

# 9. Publish final video
POST /api/v1/studio/projects/proj-456/publish

# 10. Monitor final render progress
GET /api/v1/studio/projects/proj-456/status
# (Wait for complete status)
```

---

## Related Documentation

- **Database Schema**: See `VideoProject` model in `/backend/app/models/video_project.py`
- **Service Layer**: See implementation in `/backend/app/services/`
- **Frontend Integration**: See React components in `/frontend/src/components/studio/`

---

## Implementation Notes

**Background Tasks:**
- Preview and publish operations run as FastAPI background tasks
- Use SSE endpoint to track real-time progress
- Tasks update database with status and progress percentage

**File Storage:**
- Covers: `data/covers/`
- Preview videos: `data/cache/videos/`
- Final videos: `data/videos/`

**Dependencies:**
- `sse-starlette`: Server-Sent Events support
- `Pillow`: Image processing
- `librosa`: Audio analysis for lyric timing
- Service classes handle business logic

**Security:**
- All endpoints require authentication
- File uploads validated for type and size
- User-provided prompts sanitized before AI generation

---

**API Version**: v1
**Last Updated**: 2025-11-30
**Status**: Production Ready
