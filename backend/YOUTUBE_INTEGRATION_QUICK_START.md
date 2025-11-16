# YouTube Integration - Quick Start Guide

## 30-Second Setup

### 1. Get Google Credentials
```bash
# Visit: https://console.cloud.google.com/
# Create project → Enable YouTube Data API v3
# Create OAuth credentials → Copy CLIENT_ID and CLIENT_SECRET
```

### 2. Configure Environment
```bash
# Edit .env
YOUTUBE_CLIENT_ID=123456789-abc.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-abcdefghijklmnop
YOUTUBE_DEFAULT_PRIVACY=public
```

### 3. Restart Backend
```bash
docker-compose restart backend
```

### 4. Authenticate (One-Time)
```bash
# Via web UI:
# 1. Login to http://localhost:8501
# 2. Go to Settings → YouTube
# 3. Click "Authenticate"
# 4. Grant permissions
# Done! Tokens saved to /app/data/youtube_tokens.json
```

---

## Testing the Integration

### Test Video Generation (Manual)
```python
from pathlib import Path
from app.services.video_generator import get_video_generator

generator = get_video_generator()
generator.generate_video(
    audio_file=Path("/app/downloads/test.mp3"),
    output_file=Path("/app/downloads/test.mp4")
)
# Check /app/downloads/test.mp4
```

### Test YouTube Upload (Manual)
```python
import asyncio
from pathlib import Path
from app.services.youtube_uploader import get_youtube_uploader

async def test_upload():
    uploader = get_youtube_uploader()

    # Must authenticate first!
    if not uploader.load_credentials():
        print("Please complete OAuth flow first")
        return

    result = await uploader.upload_video(
        video_file=Path("/app/downloads/test.mp4"),
        title="Test Upload",
        description="Test video from automation pipeline",
        tags=["test", "ai music"],
        privacy_status="unlisted"  # Safe for testing
    )

    print(f"Uploaded: {result['video_url']}")

asyncio.run(test_upload())
```

---

## Common Commands

### Check OAuth Status
```bash
docker exec songs-backend ls -la /app/data/youtube_tokens.json
# If exists → authenticated
# If missing → need to authenticate
```

### View Tokens (Debugging)
```bash
docker exec songs-backend cat /app/data/youtube_tokens.json | jq
```

### Reset Authentication
```bash
docker exec songs-backend rm /app/data/youtube_tokens.json
# Then re-authenticate via web UI
```

### Check Logs
```bash
docker logs songs-backend | grep -i youtube
# Shows OAuth flow, uploads, errors
```

---

## API Quick Reference

### OAuth URL
```bash
curl -X GET http://localhost:8000/api/youtube/oauth-url \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### OAuth Callback
```bash
curl -X POST http://localhost:8000/api/youtube/oauth-callback \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "4/0AanRRrv..."}'
```

### List Uploads
```bash
curl -X GET "http://localhost:8000/api/youtube/uploads?limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Queue Upload
```bash
curl -X POST http://localhost:8000/api/youtube/upload \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "song_id": "song_abc123",
    "title": "My Song",
    "description": "AI-generated music",
    "tags": "ai,music",
    "privacy": "public"
  }'
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| "YouTube OAuth credentials not configured" | Set `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` in `.env` |
| "No valid YouTube credentials available" | Complete OAuth flow via web UI |
| "OAuth authentication failed" | Authorization code expired, restart flow |
| "quotaExceeded" | YouTube quota limit reached (6 videos/day default) |
| "Video file not found" | Ensure song is downloaded first |
| "FFmpeg failed" | Already installed, check audio file format |

---

## Privacy Settings

| Setting | Visibility | Use Case |
|---------|-----------|----------|
| `public` | Anyone can find and watch | Production releases |
| `unlisted` | Only with link | Testing, selective sharing |
| `private` | Only you | Internal review |

**Recommendation:** Start with `unlisted` for testing

---

## Quota Management

**Default quota:** 10,000 units/day

**Costs:**
- Video upload: ~1,600 units
- Can upload: ~6 videos/day

**Increase quota:**
1. Google Cloud Console
2. APIs & Services → YouTube Data API v3
3. Quotas → Request increase
4. Typical approval: 1-2 business days

---

## Files Reference

| File | Purpose |
|------|---------|
| `/app/services/youtube_uploader.py` | OAuth & upload logic |
| `/app/services/video_generator.py` | FFmpeg video generation |
| `/app/api/youtube.py` | REST API endpoints |
| `/app/data/youtube_tokens.json` | Stored OAuth tokens |
| `/app/downloads/*.mp4` | Generated videos (auto-cleanup) |

---

## Complete Flow Example

```python
# 1. Song created (manual or CLI)
# File: generated/songs/my-song.md

# 2. File watcher detects → creates DB record
# Status: pending

# 3. Worker uploads to Suno
# Status: uploading → generating

# 4. Worker downloads audio
# Status: downloaded

# 5. Worker evaluates quality
# Status: evaluated (if approved)

# 6. Worker generates video
from app.services.video_generator import get_video_generator
video_generator.generate_video(
    audio_file=Path("downloads/my-song.mp3"),
    output_file=Path("downloads/my-song.mp4")
)

# 7. Worker uploads to YouTube
from app.services.youtube_uploader import get_youtube_uploader
result = await youtube_uploader.upload_video(
    video_file=Path("downloads/my-song.mp4"),
    title="My Song",
    description="...",
    tags=["ai", "music"],
    privacy_status="public"
)

# 8. Database updated
# Status: uploaded
# YouTubeUpload record created with video_url

# 9. Video file cleanup
# downloads/my-song.mp4 deleted
```

---

## Next Steps

1. ✅ Set up Google Cloud credentials
2. ✅ Configure .env
3. ✅ Complete OAuth flow
4. ✅ Test video generation
5. ✅ Test YouTube upload
6. ✅ Run end-to-end pipeline test
7. ✅ Set quota limits
8. ✅ Configure privacy settings
9. ✅ Monitor first uploads

**Estimated setup time:** 15 minutes (+ Google Cloud approval time)

---

**For detailed documentation, see:** `PHASE_5_YOUTUBE_INTEGRATION_COMPLETE.md`
