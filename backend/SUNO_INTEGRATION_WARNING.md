# ⚠️ SUNO INTEGRATION - TERMS OF SERVICE COMPLIANCE ⚠️

## CRITICAL: READ BEFORE USING SUNO AUTOMATION

This automation system includes **Playwright-based browser automation** for Suno.com. You **MUST** verify compliance with Suno's Terms of Service before using this feature.

**Failure to verify ToS compliance may result in:**
- Account suspension or ban
- Legal liability for ToS violations
- Wasted development time
- Loss of access to Suno services

---

## Pre-Implementation Checklist

Complete **ALL** these steps before using Suno integration:

### 1. Review Suno.com Terms of Service

**Action Items:**
- [ ] Read Suno.com ToS in full at: https://suno.com/terms (verify URL)
- [ ] Search ToS for keywords: "automation", "scraping", "bot", "API"
- [ ] Check for "Acceptable Use Policy" section
- [ ] Review robots.txt: https://suno.com/robots.txt
- [ ] Document ToS findings (create `SUNO_TOS_REVIEW.md` with notes)

**What to Look For:**
```
✅ ALLOWED if ToS states:
   - "You may use automation tools..."
   - "API access is available..."
   - "Browser automation is permitted for personal use..."

❌ PROHIBITED if ToS states:
   - "Automated access is strictly prohibited..."
   - "You may not use bots or scraping tools..."
   - "Only manual interaction is permitted..."
```

### 2. Check for Official API

**Action Items:**
- [ ] Visit Suno documentation: https://docs.suno.com (verify URL)
- [ ] Search for "API" or "Developer" sections
- [ ] Check GitHub for official Suno API libraries
- [ ] Search Reddit/Discord for Suno API announcements
- [ ] Google: "Suno.com official API" OR "Suno developer documentation"

**API Discovery:**
```bash
# Check if Suno has API endpoints
curl -I https://api.suno.com
curl -I https://suno.com/api

# Search for API documentation
# If API exists, USE IT INSTEAD of browser automation!
```

**If API Exists:**
- ✅ Use official API (much better than browser automation)
- ✅ Follow API rate limits
- ✅ Use authentication tokens
- ✅ Replace Playwright with API client in `suno_client.py`

### 3. Contact Suno Support

**REQUIRED BEFORE PRODUCTION USE**

**Email Template:**
```
To: support@suno.com (verify actual email)
Subject: API Availability and Automation Policy Inquiry

Hello Suno Support,

I'm developing a personal automation tool to streamline my song generation
workflow with Suno. I have a few questions:

1. Does Suno offer an official API for programmatic song generation?
   If yes, where can I find the documentation?

2. If no API exists, does your Terms of Service permit browser automation
   for personal use (not commercial, not scraping)?

3. Are there any rate limits I should be aware of?

4. What is the recommended approach for bulk song generation?

I want to ensure I'm using your service in compliance with your policies.

Thank you for your time!

Best regards,
[Your Name]
```

**Action Items:**
- [ ] Send email to Suno support
- [ ] Wait for official response (allow 3-5 business days)
- [ ] Document response in `SUNO_SUPPORT_RESPONSE.md`
- [ ] DO NOT implement actual selectors until you receive permission

### 4. Research Community Practices

**Action Items:**
- [ ] Search Reddit r/SunoAI for automation discussions
- [ ] Check Suno Discord server (if it exists) for API/automation channels
- [ ] Search GitHub for existing Suno automation projects
- [ ] Review how other developers interact with Suno programmatically

**Community Research:**
```
If you find existing automation projects:
- ✅ Check if they have Suno's permission
- ✅ Check if they've been taken down for ToS violations
- ⚠️  Existence doesn't mean it's allowed - verify yourself!
```

---

## Risk Assessment

### If You Proceed WITHOUT Verification:

| Risk | Likelihood | Impact | Severity |
|------|-----------|---------|----------|
| Account suspension | High | Lost access to Suno | 🔴 Critical |
| ToS violation | High | Legal liability | 🔴 Critical |
| Development time wasted | High | Code becomes unusable | 🟡 High |
| IP ban | Medium | Cannot create new account | 🟡 High |
| Data loss | Medium | Lose all generated songs | 🟡 High |

### Compliance Scenarios:

**✅ SAFE TO PROCEED:**
```
Scenario 1: Official API exists
- Replace Playwright with API client
- Follow API documentation
- Use provided authentication

Scenario 2: Suno explicitly permits automation
- ToS states automation is allowed
- OR Suno support grants written permission
- Implement with rate limiting and respect

Scenario 3: Manual operation mode
- User manually uploads via Suno.com
- Automation only handles pre/post processing
- System generates upload queue for copy/paste
```

**❌ DO NOT PROCEED:**
```
Scenario 1: ToS prohibits automation
- Clear statement against bots/automation
- No API available
- No support response or permission denied

Scenario 2: Unclear ToS + No support response
- ToS is ambiguous about automation
- Support hasn't responded
- Risk is too high - wait for clarification

Scenario 3: Other projects have been banned
- Community reports account suspensions
- GitHub projects removed for ToS violations
- Indicates Suno actively enforces anti-automation
```

---

## Current Implementation Status

### What's Implemented (Framework Only):

The Suno client (`backend/app/services/suno_client.py`) contains:

✅ **Complete Framework:**
- Playwright browser initialization
- Session management with auto-login
- Error handling with exponential backoff retry
- Browser memory management (restart every 100 operations)
- Type hints and comprehensive documentation

⚠️ **Placeholder Implementations:**
- `login()` - Framework ready, selectors commented out
- `upload_song()` - Framework ready, selectors commented out
- `check_status()` - Framework ready, selectors commented out

### What's NOT Implemented (Intentionally):

❌ **Actual Suno Interactions:**
- Login page URL and form selectors
- Song creation page URL and form selectors
- Status check endpoints or page selectors
- Job ID extraction logic
- Audio download URL extraction

**These are NOT implemented until you verify ToS compliance!**

### Current Behavior:

```python
# When you call the Suno client now:
client = await get_suno_client()

# Login - Returns success but doesn't actually login
await client.login()  # Placeholder returns True

# Upload - Returns mock job ID
result = await client.upload_song(style, lyrics, title)
# Returns: {'job_id': 'suno_mock_123', 'status': 'processing'}

# Check status - Returns mock completed
status = await client.check_status(job_id)
# Returns: {'status': 'completed', 'audio_url': 'https://mock.url'}
```

**This allows testing the pipeline WITHOUT violating ToS!**

---

## Alternative Approaches (ToS-Compliant)

If automation is prohibited or unclear, consider these alternatives:

### Option 1: Manual Upload Queue

**Architecture:**
```
1. User creates songs with Claude Code CLI
2. System detects new songs in generated/ folder
3. Backend generates "upload queue" with formatted data
4. Web UI shows queue with copy/paste buttons
5. User manually opens Suno.com in browser
6. User copies style prompt and lyrics from queue
7. User pastes into Suno form and generates
8. User inputs Suno job ID back into system
9. System polls Suno (if API exists) or downloads manually
```

**Benefits:**
- ✅ Fully compliant with any ToS
- ✅ User maintains full control
- ✅ No risk of account suspension
- ✅ Simple to implement

**Drawbacks:**
- ❌ Manual work required for each song
- ❌ Less convenient than full automation

**Implementation:**
```python
# Keep file watcher and queue system
# Replace Suno client with manual workflow UI
# User becomes the "automation" layer
```

### Option 2: Use Official API (If Available)

**If Suno releases an API:**
```python
# Replace suno_client.py with API client

import httpx
from typing import Dict, Any

class SunoAPIClient:
    """Official Suno API client."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.suno.com/v1"

    async def create_song(self, style: str, lyrics: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/songs",
                json={"style": style, "lyrics": lyrics},
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            return response.json()
```

**Benefits:**
- ✅ Official and supported
- ✅ Reliable and maintained
- ✅ Rate limits clearly defined
- ✅ No browser overhead

### Option 3: Use Alternative Services

**Research competitors with official APIs:**

1. **Udio.com** - Check if they have an API
2. **MusicLM** (Google) - Research availability
3. **MusicGen** (Meta) - Open source, can self-host
4. **Other AI Music Platforms** - Search for "AI music generation API"

**Evaluation Criteria:**
```
✅ Has official API
✅ Reasonable pricing
✅ Good quality output
✅ Commercial use allowed (if applicable)
✅ Rate limits suitable for your use case
```

---

## Implementation Guide (After ToS Verification)

**ONLY proceed with these steps if you have verified ToS compliance!**

### Step 1: Document Suno UI

Before implementing, document the actual Suno.com interface:

```bash
# Create documentation file
touch backend/SUNO_UI_SELECTORS.md
```

**Document:**
1. Login page URL
2. Login form field selectors (email, password)
3. Song creation page URL
4. Song form field selectors (style, lyrics, title)
5. Generate button selector
6. Job ID location (URL, DOM element, API response)
7. Job status page URL or API endpoint
8. Status indicators (processing, completed, failed)
9. Audio download URL location

### Step 2: Implement Login Flow

```python
# In backend/app/services/suno_client.py

async def login(self, force: bool = False) -> bool:
    """Login to Suno.com - IMPLEMENT AFTER ToS VERIFICATION"""

    # Navigate to login page
    await self.page.goto('https://suno.com/login')  # REPLACE WITH ACTUAL URL

    # Fill form (REPLACE WITH ACTUAL SELECTORS)
    await self.page.fill('input[name="email"]', settings.SUNO_EMAIL)
    await self.page.fill('input[name="password"]', settings.SUNO_PASSWORD)

    # Submit
    await self.page.click('button[type="submit"]')

    # Wait for success (REPLACE WITH ACTUAL SELECTOR)
    await self.page.wait_for_selector('.user-profile', timeout=30000)

    self.is_logged_in = True
    return True
```

### Step 3: Implement Upload Flow

```python
async def upload_song(
    self, style_prompt: str, lyrics: str, title: Optional[str] = None
) -> Dict[str, Any]:
    """Upload song - IMPLEMENT AFTER ToS VERIFICATION"""

    # Navigate to create page
    await self.page.goto('https://suno.com/create')  # REPLACE WITH ACTUAL URL

    # Fill form (REPLACE WITH ACTUAL SELECTORS)
    await self.page.fill('textarea[name="style"]', style_prompt)
    await self.page.fill('textarea[name="lyrics"]', lyrics)

    if title:
        await self.page.fill('input[name="title"]', title)

    # Generate
    await self.page.click('button:has-text("Generate")')  # REPLACE

    # Extract job ID (REPLACE WITH ACTUAL LOGIC)
    await self.page.wait_for_selector('.job-id')
    job_id = await self.page.text_content('.job-id')

    return {'job_id': job_id, 'status': 'processing'}
```

### Step 4: Test Incrementally

```bash
# Test login only
python -c "
import asyncio
from app.services.suno_client import get_suno_client

async def test():
    client = await get_suno_client()
    success = await client.login()
    print(f'Login: {success}')

asyncio.run(test())
"

# Test upload
# ... etc
```

### Step 5: Add Rate Limiting

```python
# Respect Suno's servers - add delays
await asyncio.sleep(2)  # Between operations

# Track usage
daily_uploads = 0
MAX_DAILY_UPLOADS = 100  # Adjust based on Suno's limits
```

---

## Monitoring and Safety

### If You Implement Automation:

**Add monitoring:**
```python
# Log all Suno interactions
logger.info(f"Suno operation: {operation_type}")

# Track success/failure rates
suno_stats = {
    'uploads_succeeded': 0,
    'uploads_failed': 0,
    'account_errors': 0  # May indicate ban
}

# Alert on suspicious patterns
if suno_stats['account_errors'] > 5:
    logger.critical("⚠️  Multiple account errors - possible ban!")
    # Pause automation
    # Notify user
```

**Safety Features:**
```python
# Respect rate limits
MAX_UPLOADS_PER_HOUR = 10
MAX_UPLOADS_PER_DAY = 50

# Add random delays (appear more human)
delay = random.uniform(5, 15)
await asyncio.sleep(delay)

# User-Agent rotation
# Session persistence (don't login repeatedly)
# Graceful error handling
```

---

## Legal Disclaimer

**This code is provided for EDUCATIONAL PURPOSES ONLY.**

The maintainers of this project:
- ❌ Do NOT endorse ToS violations
- ❌ Are NOT responsible for your use of this code
- ❌ Are NOT liable for account suspensions or legal issues
- ❌ Do NOT guarantee this code complies with any service's ToS

**By using this automation, you acknowledge:**
1. You have read and understood Suno.com's Terms of Service
2. You have verified automation is permitted
3. You accept all risks and liability
4. You will cease use immediately if requested by Suno
5. You understand your account may be suspended

**USE AT YOUR OWN RISK!**

---

## Support and Questions

**Before asking for help:**
1. Have you verified ToS compliance? (Required first step)
2. Have you contacted Suno support? (Required for clarity)
3. Have you checked for an official API? (Preferred method)

**Where to Get Help:**
- Suno Support: support@suno.com (verify actual email)
- Suno Community: r/SunoAI on Reddit
- This Project: GitHub issues (for technical issues only, not ToS advice)

**We cannot provide legal advice on ToS interpretation!**

---

## Checklist Summary

Before using Suno automation, you MUST complete:

- [ ] Read Suno.com ToS completely
- [ ] Search for official Suno API
- [ ] Contact Suno support for permission
- [ ] Receive written confirmation automation is allowed
- [ ] Document Suno UI selectors
- [ ] Implement actual login/upload flows
- [ ] Test incrementally with single account
- [ ] Add rate limiting and safety features
- [ ] Monitor for errors/bans
- [ ] Have contingency plan if account is suspended

**Only check this box when ALL above are complete:**
- [ ] I have verified Suno ToS compliance and received permission

---

## Final Warning

🚨 **DO NOT IMPLEMENT ACTUAL SUNO SELECTORS UNTIL ToS IS VERIFIED!** 🚨

The current placeholder implementation is intentionally incomplete.
This protects you from accidentally violating ToS.

**When in doubt, DON'T proceed with automation.**
**Use manual upload queue (Option 1) as a safe fallback.**

---

*Last Updated: 2025-11-16*
*Review this document before each Suno automation change*
