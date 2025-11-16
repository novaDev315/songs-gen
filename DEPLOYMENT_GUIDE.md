# Deployment Guide - Song Automation Pipeline

Complete guide for deploying and running the Song Automation Pipeline system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Security Configuration](#security-configuration)
4. [Starting the System](#starting-the-system)
5. [Accessing the Web UI](#accessing-the-web-ui)
6. [YouTube Integration Setup](#youtube-integration-setup)
7. [Troubleshooting](#troubleshooting)
8. [Upgrading](#upgrading)
9. [Security Best Practices](#security-best-practices)

---

## Prerequisites

### Required Software

- **Docker** (20.10+) and **Docker Compose** (2.0+)
  ```bash
  # Verify installation
  docker --version
  docker-compose --version
  ```

- **Git** (for cloning repository)
  ```bash
  git --version
  ```

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB+ free space
- **OS**: Linux, macOS, or Windows with WSL2

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/novaDev315/songs-gen.git
cd songs-gen
```

### 2. Create Environment File

```bash
cp .env.example .env
```

### 3. Configure Required Variables

Edit `.env` and set **CRITICAL** values:

```bash
# Generate secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to SECRET_KEY in .env

# Generate secure admin password
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy output to ADMIN_PASSWORD in .env
```

**Minimum Required Configuration:**

```env
SECRET_KEY=<your_generated_secret_key>
ADMIN_PASSWORD=<your_generated_secure_password>
```

---

## Security Configuration

### Critical Security Steps

⚠️ **BEFORE DEPLOYING TO PRODUCTION:**

1. **Change Default Passwords**
   - Never use default `ADMIN_PASSWORD`
   - Use generated secrets (32+ characters)

2. **Set Production Mode**
   ```env
   APP_ENV=production
   DEBUG=false
   ```

3. **Review Security Audit Report**
   ```bash
   cat SECURITY_AUDIT_REPORT.md
   ```

4. **Upgrade Vulnerable Dependencies**
   ```bash
   cd backend
   pip install --upgrade aiohttp requests python-multipart fastapi
   ```

### Recommended Security Settings

```env
# JWT Settings (already secure defaults)
JWT_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# Set strong password policy
ADMIN_PASSWORD=<64-character-random-string>
```

---

## Starting the System

### Build and Start Containers

```bash
# Build images (first time only)
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Services Started

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501
- **Database**: SQLite at `data/songs.db`

### Verify Services

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","environment":"development"}
```

---

## Accessing the Web UI

### Local Access

Open browser to: **http://localhost:8501**

### Login Credentials

```
Username: admin
Password: <your_ADMIN_PASSWORD_from_.env>
```

### Mobile/Remote Access Options

**Option 1: Same Network (Wi-Fi)**
```
http://<your-computer-ip>:8501
# Find IP: ifconfig (Mac/Linux) or ipconfig (Windows)
```

**Option 2: Tailscale (Recommended for Remote)**
1. Install Tailscale on server and devices
2. Access via: `http://<tailscale-ip>:8501`

**Option 3: Cloudflare Tunnel (Public HTTPS)**
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Create tunnel
cloudflared tunnel --url http://localhost:8501
```

**Option 4: ngrok (Quick Testing)**
```bash
ngrok http 8501
# Use generated HTTPS URL
```

---

## YouTube Integration Setup

### 1. Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Create new project: "Song Automation"
3. Enable **YouTube Data API v3**

### 2. Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: "Song Automation Pipeline"
5. Authorized redirect URIs:
   ```
   http://localhost:8501/oauth/callback
   ```
6. Save **Client ID** and **Client Secret**

### 3. Configure Environment

```env
YOUTUBE_CLIENT_ID=<your_client_id>
YOUTUBE_CLIENT_SECRET=<your_client_secret>
YOUTUBE_REDIRECT_URI=http://localhost:8501/oauth/callback
YOUTUBE_DEFAULT_PRIVACY=unlisted  # or public/private
```

### 4. Restart Services

```bash
docker-compose restart
```

### 5. Authorize Access

1. Open Web UI > Settings page
2. Click "Connect YouTube"
3. Follow OAuth flow
4. Grant permissions
5. Tokens saved to `data/youtube_tokens.json`

---

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database locked
docker-compose restart backend

# 2. Missing .env variables
cat .env | grep SECRET_KEY

# 3. Port already in use
lsof -i :8000  # Find process using port
```

### Frontend Can't Connect

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check network connectivity
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

### File Watcher Not Detecting Files

```bash
# Check volume mounts
docker exec songs-backend ls -la /app/generated/songs

# Verify permissions
chmod -R 755 generated/

# Restart with fresh volumes
docker-compose down -v
docker-compose up -d
```

### Database Locked Error

```bash
# SQLite WAL mode should prevent this, but if it occurs:
docker-compose restart backend

# If persistent, check for orphaned processes:
docker exec songs-backend lsof /app/data/songs.db
```

### YouTube Upload Fails

```bash
# Check OAuth tokens
ls -la data/youtube_tokens.json

# Re-authorize if expired
# Go to Settings > Disconnect > Connect YouTube

# Check quota limits
# YouTube API has daily quota - check console.cloud.google.com
```

---

## Upgrading

### Update Code

```bash
git pull origin main
```

### Rebuild Containers

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations

```bash
# Backup first
docker exec songs-backend cp /app/data/songs.db /app/data/songs.db.backup

# Check for schema changes
docker-compose logs backend | grep "Alembic"
```

---

## Security Best Practices

### 1. Regular Updates

```bash
# Check for security updates monthly
cd backend
pip list --outdated

# Update requirements.txt and rebuild
docker-compose build
```

### 2. Monitor Logs

```bash
# Check for suspicious activity
docker-compose logs backend | grep "401"
docker-compose logs backend | grep "Failed"
```

### 3. Rotate Secrets

```bash
# Rotate SECRET_KEY every 90 days
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Update .env and restart
```

### 4. Backup Database

```bash
# Automated backups run daily (see backend/app/services/backup.py)
# Manual backup:
docker exec songs-backend tar -czf /app/data/backup-manual.tar.gz /app/data/songs.db
docker cp songs-backend:/app/data/backup-manual.tar.gz ./backup-manual.tar.gz
```

### 5. Limit Network Exposure

```bash
# Only expose to localhost
# In docker-compose.yml:
ports:
  - "127.0.0.1:8000:8000"
  - "127.0.0.1:8501:8501"
```

### 6. Enable HTTPS

For production deployment with HTTPS:

```bash
# Use Nginx reverse proxy with Let's Encrypt
# Or Cloudflare Tunnel (recommended)

cloudflared tunnel --url http://localhost:8501
```

---

## Production Deployment Checklist

- [ ] Set `APP_ENV=production`
- [ ] Set `DEBUG=false`
- [ ] Change `SECRET_KEY` to secure random value
- [ ] Change `ADMIN_PASSWORD` to secure random value
- [ ] Upgrade all dependencies to latest secure versions
- [ ] Review `SECURITY_AUDIT_REPORT.md`
- [ ] Enable HTTPS (Cloudflare Tunnel or Nginx+Certbot)
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Restrict CORS origins to production domains
- [ ] Enable firewall rules
- [ ] Set up log rotation

---

## Getting Help

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# Backend API
curl http://localhost:8000/health

# Database
docker exec songs-backend sqlite3 /app/data/songs.db "SELECT count(*) FROM songs;"

# File watcher status
curl http://localhost:8000/api/v1/system/status
```

### Reset Everything

```bash
# ⚠️ WARNING: This deletes all data!
docker-compose down -v
rm -rf data/*
docker-compose up -d
```

---

## Next Steps

After deployment:

1. **Create Songs**: Add `.md` files to `generated/songs/`
2. **Monitor Queue**: Web UI > Queue page
3. **Review Songs**: Web UI > Review page
4. **Configure YouTube**: Settings > Connect YouTube
5. **Watch Automation**: Dashboard shows real-time stats

For song creation workflow, see: `docs/AUTOMATION_PIPELINE_PLAN.md`

---

## Support

- **Security Issues**: Review `SECURITY_AUDIT_REPORT.md`
- **Test Suite**: See `backend/tests/README.md`
- **Architecture**: See `docs/AUTOMATION_PIPELINE_PLAN.md`
- **GitHub Issues**: https://github.com/novaDev315/songs-gen/issues
