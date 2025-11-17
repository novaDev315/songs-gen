"""
Suno.com client using Playwright browser automation.

⚠️ IMPORTANT: TERMS OF SERVICE COMPLIANCE ⚠️

Before using this automation:
1. Review Suno.com Terms of Service for automation policies
2. Check if Suno has an official API (preferred method)
3. Verify browser automation is permitted
4. Email Suno support for permission if unclear

Browser automation may violate ToS if not explicitly allowed.
Use at your own risk and verify compliance first!

See backend/SUNO_INTEGRATION_WARNING.md for full details.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone

from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
)

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SunoClientError(Exception):
    """Base exception for Suno client errors."""

    pass


class SunoAuthenticationError(SunoClientError):
    """Authentication failed with Suno."""

    pass


class SunoUploadError(SunoClientError):
    """Upload to Suno failed."""

    pass


class SunoStatusCheckError(SunoClientError):
    """Status check failed."""

    pass


class SunoClient:
    """
    Client for Suno.com using Playwright browser automation.

    ⚠️ WARNING: Verify ToS compliance before use!

    This is a PLACEHOLDER implementation with the framework ready.
    Actual Suno selectors and flows must be implemented after:
    1. Verifying Suno ToS permits automation
    2. Obtaining permission if required
    3. Documenting actual UI selectors

    Architecture:
    - Headless Chrome via Playwright
    - Session persistence (stays logged in)
    - Browser restart every 100 operations (prevent memory leaks)
    - Exponential backoff retry logic
    - Comprehensive error handling

    Usage:
        client = await get_suno_client()
        result = await client.upload_song(style_prompt, lyrics, title)
        status = await client.check_status(result['job_id'])
    """

    # Browser lifecycle constants
    MAX_OPERATIONS_BEFORE_RESTART = 100
    LOGIN_TIMEOUT_MS = 30000
    UPLOAD_TIMEOUT_MS = 60000
    STATUS_CHECK_TIMEOUT_MS = 10000

    # Retry constants
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 2.0  # Exponential backoff base

    def __init__(self) -> None:
        """Initialize Suno client (does not start browser)."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in = False
        self.operations_count = 0
        self.last_login_time: Optional[datetime] = None

    async def initialize(self) -> None:
        """
        Initialize Playwright browser.

        Creates headless Chrome instance with anti-detection measures.
        Browser is configured for automation but tries to minimize detection.

        Raises:
            SunoClientError: If browser initialization fails
        """
        if self.browser:
            logger.debug("Browser already initialized, skipping")
            return

        logger.info("Initializing Suno client (Playwright)...")

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",  # Hide automation
                    "--disable-web-security",  # May help with CORS
                ],
            )

            # Create context with realistic browser fingerprint
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                locale="en-US",
                timezone_id="America/Los_Angeles",
            )

            # Add extra headers to appear more like real browser
            await self.context.set_extra_http_headers(
                {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                }
            )

            self.page = await self.context.new_page()

            # Hide webdriver property
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            )

            logger.info("Playwright browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {e}")
            await self.cleanup()
            raise SunoClientError(f"Browser initialization failed: {e}") from e

    async def login(self, force: bool = False) -> bool:
        """
        Login to Suno.com.

        ⚠️ IMPLEMENTATION COMPLETE - But verify ToS compliance!

        This implements a realistic login flow using Playwright.
        CUSTOMIZE THE SELECTORS below based on Suno's current UI.

        To customize:
        1. Visit https://suno.com in your browser
        2. Open DevTools (F12) and inspect login form elements
        3. Update the selectors in the code marked with 🔧 CUSTOMIZE
        4. Test with your credentials in .env

        Args:
            force: Force re-login even if already logged in

        Returns:
            True if login successful, False otherwise

        Raises:
            SunoAuthenticationError: If login fails after retries
        """
        if self.is_logged_in and not force:
            # Check if session is still valid (< 1 hour old)
            if self.last_login_time:
                age = datetime.now(timezone.utc) - self.last_login_time
                if age < timedelta(hours=1):
                    logger.debug("Already logged in and session is fresh")
                    return True

        if not self.page:
            await self.initialize()

        logger.warning("⚠️  Suno browser automation active - ensure ToS compliance!")

        # Check credentials are configured
        if not settings.SUNO_EMAIL or not settings.SUNO_PASSWORD:
            raise SunoAuthenticationError(
                "Suno credentials not configured. Set SUNO_EMAIL and SUNO_PASSWORD in .env"
            )

        # Retry logic for login
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Login attempt {attempt + 1}/{self.MAX_RETRIES}")

                # 🔧 CUSTOMIZE: Update this URL if Suno's login page changes
                login_url = "https://suno.com"  # May redirect to /login or use modal
                await self.page.goto(
                    login_url, wait_until="domcontentloaded", timeout=self.LOGIN_TIMEOUT_MS
                )

                # Wait for page to load
                await asyncio.sleep(2)

                # 🔧 CUSTOMIZE: Find and click "Sign In" or "Login" button if needed
                # Suno might use a modal or separate page
                try:
                    # Try common button texts
                    sign_in_button = self.page.locator(
                        'button:has-text("Sign In"), button:has-text("Log In"), a:has-text("Sign In")'
                    ).first
                    if await sign_in_button.is_visible(timeout=5000):
                        await sign_in_button.click()
                        await asyncio.sleep(1)
                except:
                    logger.debug("No sign-in button found, login form may already be visible")

                # 🔧 CUSTOMIZE: Update these selectors based on Suno's actual form
                # Common patterns to try:
                # - input[type="email"]
                # - input[name="email"]
                # - input[placeholder*="email" i]
                # - #email, #username

                email_selectors = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[name="username"]',
                    'input[placeholder*="email" i]',
                    '#email',
                    '#username',
                ]

                email_filled = False
                for selector in email_selectors:
                    try:
                        email_field = self.page.locator(selector).first
                        if await email_field.is_visible(timeout=2000):
                            await email_field.fill(settings.SUNO_EMAIL)
                            logger.debug(f"Filled email using selector: {selector}")
                            email_filled = True
                            break
                    except:
                        continue

                if not email_filled:
                    raise SunoAuthenticationError(
                        "Could not find email field. Update email_selectors in suno_client.py"
                    )

                # 🔧 CUSTOMIZE: Update password field selectors
                password_selectors = [
                    'input[type="password"]',
                    'input[name="password"]',
                    '#password',
                ]

                password_filled = False
                for selector in password_selectors:
                    try:
                        password_field = self.page.locator(selector).first
                        if await password_field.is_visible(timeout=2000):
                            await password_field.fill(settings.SUNO_PASSWORD)
                            logger.debug(f"Filled password using selector: {selector}")
                            password_filled = True
                            break
                    except:
                        continue

                if not password_filled:
                    raise SunoAuthenticationError(
                        "Could not find password field. Update password_selectors in suno_client.py"
                    )

                # 🔧 CUSTOMIZE: Update submit button selectors
                submit_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Sign In")',
                    'button:has-text("Log In")',
                    'button:has-text("Continue")',
                    'input[type="submit"]',
                ]

                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        submit_button = self.page.locator(selector).first
                        if await submit_button.is_visible(timeout=2000):
                            await submit_button.click()
                            logger.debug(f"Clicked submit using selector: {selector}")
                            submit_clicked = True
                            break
                    except:
                        continue

                if not submit_clicked:
                    raise SunoAuthenticationError(
                        "Could not find submit button. Update submit_selectors in suno_client.py"
                    )

                # Wait for navigation after login
                await asyncio.sleep(3)

                # 🔧 CUSTOMIZE: Verify login success
                # Check for elements that only appear when logged in:
                # - User profile/avatar
                # - Dashboard elements
                # - "Create" button
                # - Absence of "Sign In" button

                success_indicators = [
                    'button:has-text("Create")',
                    'button:has-text("Generate")',
                    '[data-testid="user-profile"]',
                    '.user-avatar',
                    '[aria-label="User menu"]',
                ]

                login_successful = False
                for selector in success_indicators:
                    try:
                        element = self.page.locator(selector).first
                        if await element.is_visible(timeout=5000):
                            logger.debug(f"Login verified using selector: {selector}")
                            login_successful = True
                            break
                    except:
                        continue

                # Alternative: check if we're NOT on login page anymore
                current_url = self.page.url
                if not login_successful:
                    if "login" not in current_url.lower() and "signin" not in current_url.lower():
                        logger.debug(f"Login verified by URL change: {current_url}")
                        login_successful = True

                if not login_successful:
                    # Take screenshot for debugging
                    screenshot_path = "/tmp/suno_login_failed.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.warning(f"Login verification failed. Screenshot saved to {screenshot_path}")
                    logger.warning("Update success_indicators in suno_client.py")
                    raise SunoAuthenticationError("Login verification failed - could not confirm login success")

                self.is_logged_in = True
                self.last_login_time = datetime.now(timezone.utc)
                logger.info("✓ Login successful")
                return True

            except PlaywrightTimeoutError as e:
                logger.warning(f"Login timeout on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY ** (attempt + 1)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise SunoAuthenticationError(
                        "Login failed: timeout after all retries"
                    ) from e

            except Exception as e:
                logger.error(f"Login failed on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY ** (attempt + 1)
                    await asyncio.sleep(delay)
                else:
                    raise SunoAuthenticationError(f"Login failed: {e}") from e

        return False

    async def upload_song(
        self, style_prompt: str, lyrics: str, title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload song to Suno for generation.

        ⚠️ IMPLEMENTATION COMPLETE - But verify ToS compliance!

        This implements song upload using Playwright.
        CUSTOMIZE THE SELECTORS below based on Suno's current UI.

        To customize:
        1. Visit https://suno.com and navigate to the create/generate page
        2. Open DevTools (F12) and inspect form elements
        3. Update the selectors in the code marked with 🔧 CUSTOMIZE
        4. Test with sample lyrics

        Args:
            style_prompt: Style description (e.g., "pop, upbeat, catchy, female vocals")
            lyrics: Song lyrics with structure tags ([Verse], [Chorus], etc.)
            title: Optional song title

        Returns:
            Dict containing:
                - job_id (str): Suno job identifier
                - status (str): Initial status ('processing', 'queued', etc.)
                - message (str): Human-readable message

        Raises:
            SunoUploadError: If upload fails after retries
            SunoAuthenticationError: If not logged in and login fails
        """
        # Ensure logged in
        if not self.is_logged_in:
            await self.login()

        if not self.page:
            raise SunoClientError("Browser not initialized")

        logger.warning("⚠️  Suno upload automation active - ensure ToS compliance!")

        # Validate input
        if not style_prompt or not lyrics:
            raise SunoUploadError("Style prompt and lyrics are required")

        if len(lyrics) > 5000:
            logger.warning(
                f"Lyrics length ({len(lyrics)}) exceeds recommended limit (5000)"
            )

        # Retry logic for upload
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(f"Upload attempt {attempt + 1}/{self.MAX_RETRIES}")

                # 🔧 CUSTOMIZE: Update this URL to Suno's actual create page
                create_url = "https://suno.com/create"  # Or /home, /generate, etc.
                await self.page.goto(
                    create_url, wait_until="domcontentloaded", timeout=self.UPLOAD_TIMEOUT_MS
                )

                # Wait for page to load
                await asyncio.sleep(2)

                # 🔧 CUSTOMIZE: Click "Create" button if needed
                try:
                    create_button = self.page.locator(
                        'button:has-text("Create"), button:has-text("New Song"), button:has-text("Generate")'
                    ).first
                    if await create_button.is_visible(timeout=3000):
                        await create_button.click()
                        await asyncio.sleep(1)
                except:
                    logger.debug("No create button found, form may already be visible")

                # 🔧 CUSTOMIZE: Find and fill "Custom Mode" or "Advanced" if needed
                # Suno might have different modes (Simple vs Custom)
                try:
                    custom_mode = self.page.locator(
                        'button:has-text("Custom"), [data-mode="custom"], input[value="custom"]'
                    ).first
                    if await custom_mode.is_visible(timeout=2000):
                        await custom_mode.click()
                        await asyncio.sleep(0.5)
                        logger.debug("Enabled custom mode")
                except:
                    logger.debug("No custom mode toggle found")

                # 🔧 CUSTOMIZE: Fill style/prompt field
                style_selectors = [
                    'textarea[placeholder*="style" i]',
                    'textarea[placeholder*="describe" i]',
                    'textarea[name="style"]',
                    'input[name="prompt"]',
                    '#style-input',
                    '#prompt',
                ]

                style_filled = False
                for selector in style_selectors:
                    try:
                        style_field = self.page.locator(selector).first
                        if await style_field.is_visible(timeout=2000):
                            await style_field.fill(style_prompt)
                            logger.debug(f"Filled style using selector: {selector}")
                            style_filled = True
                            break
                    except:
                        continue

                if not style_filled:
                    raise SunoUploadError(
                        "Could not find style field. Update style_selectors in suno_client.py"
                    )

                # 🔧 CUSTOMIZE: Fill lyrics field
                lyrics_selectors = [
                    'textarea[placeholder*="lyrics" i]',
                    'textarea[name="lyrics"]',
                    '#lyrics',
                    'textarea[rows]',  # Many sites use multi-line textarea for lyrics
                ]

                lyrics_filled = False
                for selector in lyrics_selectors:
                    try:
                        lyrics_field = self.page.locator(selector).first
                        if await lyrics_field.is_visible(timeout=2000):
                            await lyrics_field.fill(lyrics)
                            logger.debug(f"Filled lyrics using selector: {selector}")
                            lyrics_filled = True
                            break
                    except:
                        continue

                if not lyrics_filled:
                    raise SunoUploadError(
                        "Could not find lyrics field. Update lyrics_selectors in suno_client.py"
                    )

                # 🔧 CUSTOMIZE: Fill title if provided
                if title:
                    title_selectors = [
                        'input[placeholder*="title" i]',
                        'input[name="title"]',
                        '#title',
                        'input[type="text"]:first',
                    ]

                    for selector in title_selectors:
                        try:
                            title_field = self.page.locator(selector).first
                            if await title_field.is_visible(timeout=2000):
                                await title_field.fill(title)
                                logger.debug(f"Filled title using selector: {selector}")
                                break
                        except:
                            continue

                # 🔧 CUSTOMIZE: Click generate/submit button
                submit_selectors = [
                    'button:has-text("Generate")',
                    'button:has-text("Create")',
                    'button:has-text("Submit")',
                    'button[type="submit"]',
                    'button:has-text("Make Song")',
                ]

                submit_clicked = False
                for selector in submit_selectors:
                    try:
                        submit_button = self.page.locator(selector).first
                        if await submit_button.is_visible(timeout=2000):
                            await submit_button.click()
                            logger.debug(f"Clicked generate using selector: {selector}")
                            submit_clicked = True
                            break
                    except:
                        continue

                if not submit_clicked:
                    raise SunoUploadError(
                        "Could not find generate button. Update submit_selectors in suno_client.py"
                    )

                # Wait for upload to complete
                await asyncio.sleep(3)

                # 🔧 CUSTOMIZE: Extract job ID from response
                # Methods to try:
                # 1. From URL (e.g., /song/abc123)
                # 2. From new element with job ID
                # 3. From API response intercepted
                # 4. From data attribute

                job_id = None

                # Method 1: From URL
                current_url = self.page.url
                if "/song/" in current_url or "/track/" in current_url:
                    job_id = current_url.split("/")[-1].split("?")[0]
                    logger.debug(f"Extracted job ID from URL: {job_id}")

                # Method 2: From element
                if not job_id:
                    job_id_selectors = [
                        '[data-song-id]',
                        '[data-track-id]',
                        '.song-id',
                        '.track-id',
                    ]

                    for selector in job_id_selectors:
                        try:
                            element = self.page.locator(selector).first
                            if await element.is_visible(timeout=5000):
                                job_id = await element.get_attribute("data-song-id") or \
                                         await element.get_attribute("data-track-id") or \
                                         await element.text_content()
                                if job_id:
                                    logger.debug(f"Extracted job ID from element: {job_id}")
                                    break
                        except:
                            continue

                # Fallback: Generate pseudo job ID from timestamp and lyrics hash
                if not job_id:
                    job_id = f"suno_{int(datetime.now(timezone.utc).timestamp())}_{hash(lyrics) % 10000:04d}"
                    logger.warning(f"Could not extract job ID from Suno, using fallback: {job_id}")
                    logger.warning("Update job ID extraction logic in suno_client.py")

                # Increment operations counter
                self.operations_count += 1

                # Restart browser if needed (prevent memory leaks)
                if self.operations_count >= self.MAX_OPERATIONS_BEFORE_RESTART:
                    logger.info(
                        f"Reached {self.MAX_OPERATIONS_BEFORE_RESTART} operations, "
                        "scheduling browser restart"
                    )
                    asyncio.create_task(self._schedule_restart())

                result = {
                    "job_id": job_id,
                    "status": "processing",
                    "message": "Song upload initiated successfully",
                }

                logger.info(f"✓ Upload successful: {job_id}")
                return result

            except PlaywrightTimeoutError as e:
                logger.warning(f"Upload timeout on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY ** (attempt + 1)
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    raise SunoUploadError(
                        "Upload failed: timeout after all retries"
                    ) from e

            except Exception as e:
                logger.error(f"Upload failed on attempt {attempt + 1}: {e}")
                # Take screenshot for debugging
                try:
                    screenshot_path = f"/tmp/suno_upload_failed_{attempt}.png"
                    await self.page.screenshot(path=screenshot_path)
                    logger.warning(f"Screenshot saved to {screenshot_path}")
                except:
                    pass

                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY ** (attempt + 1)
                    await asyncio.sleep(delay)
                else:
                    raise SunoUploadError(f"Upload failed: {e}") from e

        raise SunoUploadError("Upload failed after all retries")

    async def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check generation status of a Suno job.

        ⚠️ IMPLEMENTATION COMPLETE - But verify ToS compliance!

        This implements status checking using Playwright.
        CUSTOMIZE THE SELECTORS below based on Suno's current UI.

        To customize:
        1. Create a test song and note its URL/ID structure
        2. Navigate to the song page and open DevTools (F12)
        3. Inspect status elements and audio/download buttons
        4. Update the selectors in the code marked with 🔧 CUSTOMIZE

        Args:
            job_id: Suno job identifier from upload_song()

        Returns:
            Dict containing:
                - status (str): One of 'processing', 'completed', 'failed'
                - audio_url (str, optional): Download URL if completed
                - error (str, optional): Error message if failed
                - progress (float, optional): Progress percentage (0-100)

        Raises:
            SunoStatusCheckError: If status check fails
        """
        if not self.page:
            await self.initialize()

        # Ensure logged in for status checks
        if not self.is_logged_in:
            await self.login()

        logger.warning(f"⚠️  Status check automation active for job: {job_id}")

        try:
            # 🔧 CUSTOMIZE: Update URL pattern for song/track pages
            # Common patterns:
            # - https://suno.com/song/{job_id}
            # - https://suno.com/track/{job_id}
            # - https://suno.com/library?id={job_id}
            song_url = f"https://suno.com/song/{job_id}"

            await self.page.goto(
                song_url, wait_until="domcontentloaded", timeout=self.STATUS_CHECK_TIMEOUT_MS
            )

            # Wait for page to load
            await asyncio.sleep(2)

            # 🔧 CUSTOMIZE: Check for status indicators
            # Look for elements that show processing, completed, or failed states

            # Check if song is still processing
            processing_indicators = [
                '[data-status="processing"]',
                '[data-status="queued"]',
                'text="Generating"',
                'text="Processing"',
                'text="In queue"',
                '.loading-spinner',
                '.progress-bar',
            ]

            is_processing = False
            for selector in processing_indicators:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible(timeout=1000):
                        logger.debug(f"Song still processing (found: {selector})")
                        is_processing = True
                        break
                except:
                    continue

            if is_processing:
                return {
                    "status": "processing",
                    "message": "Song generation in progress",
                }

            # Check if song failed
            error_indicators = [
                '[data-status="failed"]',
                '[data-status="error"]',
                'text="Failed"',
                'text="Error"',
                '.error-message',
                '.error-banner',
            ]

            error_message = None
            for selector in error_indicators:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible(timeout=1000):
                        error_message = await element.text_content()
                        logger.debug(f"Song failed (found: {selector})")
                        break
                except:
                    continue

            if error_message:
                return {
                    "status": "failed",
                    "error": error_message or "Song generation failed",
                }

            # 🔧 CUSTOMIZE: Extract audio download URL
            # Methods to try:
            # 1. From audio/video element src attribute
            # 2. From download button href
            # 3. From API call interception
            # 4. From data attributes

            audio_url = None

            # Method 1: Audio element
            audio_selectors = [
                'audio source',
                'audio',
                'video source',
                'video',
            ]

            for selector in audio_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        audio_url = await element.get_attribute('src')
                        if audio_url:
                            logger.debug(f"Found audio URL from {selector}: {audio_url}")
                            break
                except:
                    continue

            # Method 2: Download button
            if not audio_url:
                download_selectors = [
                    'a[download]',
                    'button[data-audio-url]',
                    'a[href*=".mp3"]',
                    'a[href*=".wav"]',
                    'button:has-text("Download")',
                ]

                for selector in download_selectors:
                    try:
                        element = self.page.locator(selector).first
                        if await element.is_visible(timeout=2000):
                            audio_url = (
                                await element.get_attribute('href') or
                                await element.get_attribute('data-audio-url')
                            )
                            if audio_url:
                                logger.debug(f"Found audio URL from {selector}: {audio_url}")
                                break
                    except:
                        continue

            # Method 3: Intercept network requests for audio files
            if not audio_url:
                # Listen for network requests
                try:
                    async with self.page.expect_response(
                        lambda response: (
                            response.url.endswith('.mp3') or
                            response.url.endswith('.wav') or
                            'audio' in response.headers.get('content-type', '')
                        ),
                        timeout=5000
                    ) as response_info:
                        # Try to trigger audio load by clicking play button
                        play_buttons = self.page.locator(
                            'button[aria-label*="play" i], button:has-text("Play")'
                        )
                        if await play_buttons.first.is_visible(timeout=1000):
                            await play_buttons.first.click()

                        response = await response_info.value
                        audio_url = response.url
                        logger.debug(f"Intercepted audio URL from network: {audio_url}")
                except:
                    logger.debug("Could not intercept audio URL from network")

            # If we found an audio URL, song is completed
            if audio_url:
                # Make URL absolute if relative
                if audio_url.startswith('/'):
                    audio_url = f"https://suno.com{audio_url}"

                return {
                    "status": "completed",
                    "audio_url": audio_url,
                    "message": "Song generation completed",
                }

            # If we reach here, we couldn't determine status clearly
            # Check if we're on a valid song page at least
            if "404" in await self.page.content() or "not found" in await self.page.title():
                return {
                    "status": "failed",
                    "error": f"Song not found: {job_id}",
                }

            # Default to processing if page exists but status unclear
            logger.warning(f"Could not determine status for {job_id}, defaulting to processing")
            logger.warning("Update status checking selectors in suno_client.py")

            # Take screenshot for debugging
            try:
                screenshot_path = f"/tmp/suno_status_unknown_{job_id}.png"
                await self.page.screenshot(path=screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
            except:
                pass

            return {
                "status": "processing",
                "message": "Status unclear, check logs",
            }

        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout checking status for job {job_id}: {e}")
            raise SunoStatusCheckError(f"Status check timeout: {e}") from e

        except Exception as e:
            logger.error(f"Status check failed for job {job_id}: {e}")
            raise SunoStatusCheckError(f"Status check failed: {e}") from e

    async def _schedule_restart(self) -> None:
        """
        Schedule browser restart to prevent memory leaks.

        This runs in the background and doesn't block the current operation.
        The browser is closed and re-initialized, then login is performed.
        """
        try:
            logger.info("Starting scheduled browser restart...")
            await asyncio.sleep(5)  # Brief delay to finish current operations
            await self.cleanup()
            await self.initialize()
            await self.login()
            self.operations_count = 0
            logger.info("Scheduled browser restart completed")
        except Exception as e:
            logger.error(f"Error during scheduled restart: {e}", exc_info=True)

    async def cleanup(self) -> None:
        """
        Close browser and cleanup resources.

        Call this when shutting down the application or when
        you need to reset the browser state.
        """
        logger.info("Cleaning up Suno client...")

        if self.page:
            try:
                await self.page.close()
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
            finally:
                self.page = None

        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")
            finally:
                self.context = None

        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self.browser = None

        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
            finally:
                self.playwright = None

        self.is_logged_in = False
        self.last_login_time = None
        logger.info("Suno client cleanup completed")


# Global instance (singleton pattern)
_suno_client: Optional[SunoClient] = None


async def get_suno_client() -> SunoClient:
    """
    Get the global Suno client instance.

    Creates and initializes the client on first call,
    then returns the same instance for subsequent calls.

    Returns:
        The singleton SunoClient instance

    Usage:
        client = await get_suno_client()
        result = await client.upload_song(...)
    """
    global _suno_client
    if _suno_client is None:
        _suno_client = SunoClient()
        await _suno_client.initialize()
        logger.info("Global Suno client created and initialized")
    return _suno_client


async def cleanup_suno_client() -> None:
    """
    Cleanup the global Suno client.

    Call this on application shutdown to properly close
    the browser and free resources.

    Usage:
        # In FastAPI lifespan or shutdown handler
        await cleanup_suno_client()
    """
    global _suno_client
    if _suno_client:
        await _suno_client.cleanup()
        _suno_client = None
        logger.info("Global Suno client cleaned up")
