# Suno Browser Automation Setup Guide

## ⚠️ CRITICAL: Terms of Service Compliance

**Before using this automation, you MUST:**

1. ✅ Read Suno.com Terms of Service thoroughly
2. ✅ Contact Suno support for explicit permission if unclear
3. ✅ Verify browser automation is permitted
4. ✅ Consider using official API if available (check https://suno.com/docs)

**Using this automation without verification may:**
- ❌ Violate Suno's Terms of Service
- ❌ Result in account termination
- ❌ Expose you to legal liability

**YOU ARE RESPONSIBLE for ensuring compliance. Proceed at your own risk.**

---

## Overview

The Suno browser automation is now **fully implemented** using Playwright. However, the selectors need to be customized based on Suno's current UI, which may change over time.

The implementation includes:
- ✅ **Login flow** with multiple fallback selectors
- ✅ **Song upload** with custom mode support
- ✅ **Status checking** with audio URL extraction
- ✅ **Retry logic** with exponential backoff
- ✅ **Error handling** with debug screenshots
- ✅ **Browser lifecycle** management (auto-restart after 100 operations)

---

## Quick Start

### 1. Configure Credentials

Edit `.env` file:

```bash
# Suno Integration (Phase 3)
SUNO_EMAIL=your_email@example.com
SUNO_PASSWORD=your_secure_password
```

### 2. Install Playwright Browsers

```bash
cd backend
playwright install chromium
```

### 3. Test the Automation

```bash
# Start backend
docker-compose up backend

# Or run locally
cd backend
uvicorn app.main:app --reload
```

The automation will run when songs are detected in `generated/songs/` folder.

---

## Customizing Selectors (REQUIRED)

The code includes multiple fallback selectors, but you should verify and update them based on Suno's current UI.

### How to Find Selectors

1. **Open Suno.com in Chrome/Firefox**
2. **Open DevTools** (F12 or Right-click → Inspect)
3. **Navigate to the page** you want to automate (login, create, song page)
4. **Click the Element Picker** (icon in DevTools top-left)
5. **Click the element** you want to select
6. **In DevTools Elements tab**, right-click the highlighted element
7. **Copy → Copy selector** or **Copy → Copy XPath**

### Key Files to Customize

All customizable selectors are marked with `🔧 CUSTOMIZE:` comments.

#### File: `backend/app/services/suno_client.py`

---

### Login Flow Customization

**Location**: `async def login()` method (lines 175-396)

**What to customize**:

```python
# 🔧 CUSTOMIZE: Update this URL if Suno's login page changes
login_url = "https://suno.com"  # Update if different

# 🔧 CUSTOMIZE: Update these selectors based on Suno's actual form
email_selectors = [
    'input[type="email"]',          # Generic email input
    'input[name="email"]',           # Name attribute
    'input[placeholder*="email" i]', # Placeholder contains "email"
    '#email',                        # ID
]

password_selectors = [
    'input[type="password"]',
    'input[name="password"]',
    '#password',
]

submit_selectors = [
    'button[type="submit"]',
    'button:has-text("Sign In")',
    'button:has-text("Log In")',
]

success_indicators = [
    'button:has-text("Create")',     # Button visible when logged in
    '[data-testid="user-profile"]',  # User profile element
    '.user-avatar',                   # Avatar icon
]
```

**Testing**:
1. Run the backend
2. Watch logs for which selector succeeded
3. Remove selectors that don't work
4. Add new ones if needed

---

### Upload Flow Customization

**Location**: `async def upload_song()` method (lines 398-676)

**What to customize**:

```python
# 🔧 CUSTOMIZE: Update this URL to Suno's actual create page
create_url = "https://suno.com/create"  # Or /home, /generate

# 🔧 CUSTOMIZE: Find "Custom Mode" toggle if Suno has it
custom_mode = self.page.locator(
    'button:has-text("Custom"), [data-mode="custom"]'
).first

# 🔧 CUSTOMIZE: Fill style/prompt field
style_selectors = [
    'textarea[placeholder*="style" i]',
    'textarea[name="style"]',
    '#style-input',
]

# 🔧 CUSTOMIZE: Fill lyrics field
lyrics_selectors = [
    'textarea[placeholder*="lyrics" i]',
    'textarea[name="lyrics"]',
    '#lyrics',
]

# 🔧 CUSTOMIZE: Extract job ID from response
# Methods:
# 1. From URL: current_url.split("/")[-1]
# 2. From element: await element.get_attribute("data-song-id")
# 3. From API response
```

**How to test**:
1. Manually create a song on Suno.com
2. Note the URL structure (`/song/{id}` vs `/track/{id}` etc.)
3. Update `job_id` extraction logic accordingly

---

### Status Check Customization

**Location**: `async def check_status()` method (lines 678-908)

**What to customize**:

```python
# 🔧 CUSTOMIZE: Update URL pattern for song pages
song_url = f"https://suno.com/song/{job_id}"  # Or /track/, /library?id=

# 🔧 CUSTOMIZE: Check for status indicators
processing_indicators = [
    '[data-status="processing"]',
    'text="Generating"',
    '.loading-spinner',
]

error_indicators = [
    '[data-status="failed"]',
    'text="Error"',
    '.error-message',
]

# 🔧 CUSTOMIZE: Extract audio download URL
audio_selectors = [
    'audio source',              # HTML5 audio element
    'a[download]',                # Download link
    'button[data-audio-url]',     # Data attribute
    'a[href*=".mp3"]',            # Link to MP3 file
]
```

**How to test**:
1. Generate a test song manually
2. Note its ID from the URL
3. Run status check with that ID
4. Check logs to see which selector worked
5. Update selectors accordingly

---

## Debug Mode

The automation includes automatic debugging features:

### Screenshots

When operations fail, screenshots are automatically saved:

- **Login failed**: `/tmp/suno_login_failed.png`
- **Upload failed**: `/tmp/suno_upload_failed_{attempt}.png`
- **Status unclear**: `/tmp/suno_status_unknown_{job_id}.png`

### Logs

Check backend logs for detailed selector matching:

```bash
docker-compose logs -f backend | grep "Suno"
```

Look for:
- `Filled email using selector: ...` (which selector worked)
- `Login verified using selector: ...` (how login was confirmed)
- `Found audio URL from ...` (how audio was extracted)

### Disable Headless Mode

To see the browser in action (helpful for debugging):

Edit `backend/app/services/suno_client.py` line 125:

```python
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Change True to False
    args=[...]
)
```

---

## Common Issues & Solutions

### Issue: "Could not find email field"

**Cause**: Suno changed their login form structure

**Solution**:
1. Visit https://suno.com and click "Sign In"
2. Inspect the email input field
3. Copy its selector (right-click → Copy selector)
4. Add it to `email_selectors` array in `suno_client.py`

### Issue: "Login verification failed"

**Cause**: Success indicator selector is wrong

**Solution**:
1. Log in manually to Suno.com
2. Find an element that only appears when logged in (e.g., user profile, "Create" button)
3. Inspect it and copy selector
4. Add to `success_indicators` array

### Issue: "Could not extract job ID"

**Cause**: Job ID extraction logic doesn't match Suno's response

**Solution**:
1. Create a song manually
2. Note the URL pattern (e.g., `/song/abc123` or different?)
3. Update job ID extraction in upload_song() method
4. Try different methods (URL, element attribute, API response)

### Issue: Browser crashes or hangs

**Cause**: Memory leak or stale session

**Solution**:
The browser auto-restarts every 100 operations. If needed:
1. Reduce `MAX_OPERATIONS_BEFORE_RESTART` (currently 100)
2. Check Docker container memory limits
3. Review Playwright logs for errors

---

## Advanced Customization

### Network Request Interception

To capture Suno's API calls (useful for finding job IDs or audio URLs):

```python
# Add to initialize() method
self.page.on("response", lambda response:
    logger.debug(f"Response: {response.url} - {response.status}")
)
```

### Custom Wait Strategies

If Suno uses heavy JavaScript or slow loading:

```python
# Wait for specific network state
await self.page.goto(url, wait_until="networkidle")

# Wait for specific element
await self.page.wait_for_selector('.song-ready', timeout=30000)

# Wait for API response
await self.page.wait_for_response(
    lambda r: "suno.com/api" in r.url and r.status == 200
)
```

### Using Suno's Internal API

If Suno exposes an internal API, you might be able to bypass browser automation:

```python
# Make direct API calls
response = await self.page.request.post(
    "https://suno.com/api/v1/generate",
    data={"style": style_prompt, "lyrics": lyrics}
)
data = await response.json()
job_id = data['id']
```

---

## Performance Optimization

### Reduce Wait Times

After verifying selectors work, reduce sleep times:

```python
# Change from:
await asyncio.sleep(3)

# To:
await asyncio.sleep(1)
```

### Parallel Operations

The system supports multiple concurrent workers (configured in Phase 2B). Each worker gets its own browser instance.

### Browser Reuse

Sessions persist for 1 hour before requiring re-login. Adjust in `login()` method:

```python
if age < timedelta(hours=1):  # Change to hours=24 for daily login
    return True
```

---

## Security Best Practices

1. **Never commit credentials** - Use `.env` file (already gitignored)
2. **Rotate passwords regularly** - Change Suno password every 90 days
3. **Monitor for suspicious activity** - Check Suno account for unexpected logins
4. **Use dedicated account** - Don't use your personal Suno account for automation
5. **Limit rate** - Don't spam Suno with requests (respect their servers)

---

## Testing Checklist

Before deploying to production:

- [ ] Login flow works (check logs for successful selectors)
- [ ] Song upload works (manually verify song appears in Suno)
- [ ] Status check works (verify audio URL is extracted)
- [ ] Error handling works (try invalid credentials, network errors)
- [ ] Screenshots save properly (check `/tmp/suno_*.png`)
- [ ] Browser restarts after 100 operations (check logs)
- [ ] Credentials are secure (not in code, in .env only)
- [ ] ToS compliance verified (explicit permission obtained)

---

## Need Help?

1. **Check logs**: `docker-compose logs -f backend | grep Suno`
2. **Review screenshots**: `ls -la /tmp/suno_*.png`
3. **Test selectors manually**: Use browser DevTools
4. **Read Playwright docs**: https://playwright.dev/python/docs/intro
5. **Check Suno's UI changes**: Suno may update their interface

---

## Legal Disclaimer

This automation tool is provided AS-IS. You are solely responsible for:
- Verifying Terms of Service compliance
- Obtaining necessary permissions
- Ensuring legal use of the automation
- Any consequences of using this tool

The authors assume no liability for misuse or ToS violations.

**When in doubt, contact Suno support before enabling automation.**

---

## Next Steps

After customizing selectors:

1. Test with a single song
2. Monitor logs for errors
3. Verify songs generate correctly on Suno
4. Check downloaded audio quality
5. Enable full pipeline automation

See `DEPLOYMENT_GUIDE.md` for production deployment instructions.
