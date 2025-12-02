# Integration Guide

This guide explains how to set up external integrations for the Song Automation Pipeline.

## Table of Contents

- [Suno Integration](#suno-integration)
- [YouTube Integration](#youtube-integration)
- [Discord Notifications](#discord-notifications)
- [Slack Notifications](#slack-notifications)

---

## Suno Integration

Suno integration allows automatic upload of songs for AI music generation.

### Setup Steps

1. **Create a Suno Account**
   - Go to [suno.ai](https://suno.ai)
   - Sign up or log in

2. **Add Credentials to `.env`**
   ```env
   SUNO_EMAIL=your-email@example.com
   SUNO_PASSWORD=your-suno-password
   ```

3. **Enable Auto-Upload (Optional)**
   ```env
   AUTO_UPLOAD_TO_SUNO=true
   ```

### Notes
- The system uses browser automation (Playwright) to interact with Suno
- Ensure you have a valid Suno subscription for API access
- Rate limits may apply based on your Suno plan

---

## YouTube Integration

YouTube integration enables automatic video uploads of generated songs.

### Setup Steps

#### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** → **New Project**
3. Enter project name (e.g., "Song Automation Pipeline")
4. Click **Create**

#### 2. Enable YouTube Data API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click on it and press **Enable**

#### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: **External**
   - App name: "Song Automation Pipeline"
   - User support email: Your email
   - Developer contact: Your email
   - Click **Save and Continue** through all steps
4. Back in Credentials, click **Create Credentials** → **OAuth client ID**
5. Application type: **Web application**
6. Name: "Song Pipeline Web Client"
7. Add Authorized redirect URI:
   ```
   http://localhost:8501/oauth/callback
   ```
8. Click **Create**
9. Copy the **Client ID** and **Client Secret**

#### 4. Add Credentials to `.env`

```env
YOUTUBE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=your-client-secret-here
YOUTUBE_REDIRECT_URI=http://localhost:8501/oauth/callback
YOUTUBE_DEFAULT_PRIVACY=public
```

#### 5. First-Time Authorization

1. Start the application: `docker-compose up`
2. Go to the web UI: `http://localhost:8501`
3. Navigate to **YouTube** settings
4. Click **Authorize YouTube**
5. Log in with your Google account
6. Grant permissions to upload videos
7. You'll be redirected back to the app

### Privacy Options

| Value | Description |
|-------|-------------|
| `public` | Anyone can see the video |
| `unlisted` | Only people with the link can see |
| `private` | Only you can see the video |

---

## Discord Notifications

Get notified in Discord when songs complete, fail, or upload to YouTube.

### Setup Steps

#### 1. Create a Discord Webhook

1. Open Discord and go to your server
2. Right-click on the channel where you want notifications
3. Click **Edit Channel** → **Integrations** → **Webhooks**
4. Click **New Webhook**
5. Name it (e.g., "Song Pipeline")
6. Click **Copy Webhook URL**

#### 2. Add to `.env`

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijk
NOTIFICATIONS_ENABLED=true
NOTIFY_ON_SONG_COMPLETE=true
NOTIFY_ON_SONG_FAILED=true
NOTIFY_ON_YOUTUBE_UPLOAD=true
```

### Notification Types

| Setting | Notification |
|---------|-------------|
| `NOTIFY_ON_SONG_COMPLETE` | When a song finishes generating |
| `NOTIFY_ON_SONG_FAILED` | When song generation fails |
| `NOTIFY_ON_YOUTUBE_UPLOAD` | When a video uploads to YouTube |
| `NOTIFY_ON_EVALUATION` | When song evaluation completes |

---

## Slack Notifications

Get notified in Slack when songs complete, fail, or upload to YouTube.

### Setup Steps

#### 1. Create a Slack App

1. Go to [Slack API](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name it (e.g., "Song Pipeline")
4. Select your workspace
5. Click **Create App**

#### 2. Enable Incoming Webhooks

1. In your app settings, go to **Incoming Webhooks**
2. Toggle **Activate Incoming Webhooks** to **On**
3. Click **Add New Webhook to Workspace**
4. Select the channel for notifications
5. Click **Allow**
6. Copy the **Webhook URL**

#### 3. Add to `.env`

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXX
NOTIFICATIONS_ENABLED=true
NOTIFY_ON_SONG_COMPLETE=true
NOTIFY_ON_SONG_FAILED=true
NOTIFY_ON_YOUTUBE_UPLOAD=true
```

---

## Environment Variables Reference

### Required

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing key (generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `ADMIN_PASSWORD` | Admin login password |

### Suno

| Variable | Default | Description |
|----------|---------|-------------|
| `SUNO_EMAIL` | (empty) | Suno account email |
| `SUNO_PASSWORD` | (empty) | Suno account password |
| `AUTO_UPLOAD_TO_SUNO` | `false` | Auto-queue new songs |

### YouTube

| Variable | Default | Description |
|----------|---------|-------------|
| `YOUTUBE_CLIENT_ID` | (empty) | OAuth 2.0 Client ID |
| `YOUTUBE_CLIENT_SECRET` | (empty) | OAuth 2.0 Client Secret |
| `YOUTUBE_REDIRECT_URI` | `http://localhost:8501/oauth/callback` | OAuth redirect URI |
| `YOUTUBE_DEFAULT_PRIVACY` | `public` | Default video privacy |

### Notifications

| Variable | Default | Description |
|----------|---------|-------------|
| `DISCORD_WEBHOOK_URL` | (empty) | Discord webhook URL |
| `SLACK_WEBHOOK_URL` | (empty) | Slack webhook URL |
| `NOTIFICATIONS_ENABLED` | `true` | Master switch for notifications |
| `NOTIFY_ON_SONG_COMPLETE` | `true` | Notify on song completion |
| `NOTIFY_ON_SONG_FAILED` | `true` | Notify on song failure |
| `NOTIFY_ON_YOUTUBE_UPLOAD` | `true` | Notify on YouTube upload |
| `NOTIFY_ON_EVALUATION` | `false` | Notify on evaluation |

### Workers

| Variable | Default | Description |
|----------|---------|-------------|
| `WORKER_COUNT` | `2` | Number of background workers |
| `WORKER_CHECK_INTERVAL` | `60` | Seconds between task checks |
| `WORKER_MAX_RETRIES` | `3` | Max retries for failed tasks |

### Evaluation

| Variable | Default | Description |
|----------|---------|-------------|
| `MIN_QUALITY_SCORE` | `70.0` | Auto-approve threshold (0-100) |

---

## Troubleshooting

### YouTube: "Access Denied" Error
- Ensure your OAuth consent screen is configured
- Check that YouTube Data API v3 is enabled
- Verify the redirect URI matches exactly

### Suno: "Login Failed" Error
- Double-check email and password
- Ensure your Suno account is active
- Try logging in manually to verify credentials

### Notifications Not Working
- Verify `NOTIFICATIONS_ENABLED=true`
- Check webhook URLs are correct
- Test webhooks manually with curl:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"content":"Test message"}' \
    YOUR_DISCORD_WEBHOOK_URL
  ```

### General Issues
- Check logs: `docker-compose logs -f backend`
- Verify `.env` file is in the project root
- Restart containers after `.env` changes: `docker-compose down && docker-compose up`
