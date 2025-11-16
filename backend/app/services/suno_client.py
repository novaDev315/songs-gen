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
from datetime import datetime, timedelta

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

        ⚠️ PLACEHOLDER: Requires actual Suno.com login flow implementation

        This method contains the framework for login but not the actual
        implementation. Before implementing:
        1. Verify Suno ToS permits automation
        2. Document actual login page URL
        3. Document actual form selectors
        4. Document any 2FA/captcha handling needed

        Args:
            force: Force re-login even if already logged in

        Returns:
            True if login successful, False otherwise

        Raises:
            SunoAuthenticationError: If login fails after retries

        TODO:
        1. Navigate to Suno.com login page
        2. Enter credentials (from environment variables)
        3. Handle 2FA if required
        4. Verify successful login (check for dashboard/profile element)
        5. Store session cookies for reuse
        """
        if self.is_logged_in and not force:
            # Check if session is still valid (e.g., < 1 hour old)
            if self.last_login_time:
                age = datetime.utcnow() - self.last_login_time
                if age < timedelta(hours=1):
                    logger.debug("Already logged in and session is fresh")
                    return True

        if not self.page:
            await self.initialize()

        logger.warning("⚠️  Suno login NOT IMPLEMENTED - requires ToS verification!")
        logger.warning(
            "⚠️  Before implementing: verify Suno.com permits browser automation"
        )
        logger.warning("⚠️  See backend/SUNO_INTEGRATION_WARNING.md for details")

        # Check credentials are configured
        if not settings.SUNO_EMAIL or not settings.SUNO_PASSWORD:
            raise SunoAuthenticationError(
                "Suno credentials not configured. Set SUNO_EMAIL and SUNO_PASSWORD."
            )

        # Placeholder implementation with retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"[PLACEHOLDER] Login attempt {attempt + 1}/{self.MAX_RETRIES}"
                )

                # TODO: Implement actual login flow
                # Example (REPLACE WITH ACTUAL SUNO SELECTORS):
                #
                # # Navigate to login page
                # await self.page.goto(
                #     'https://suno.com/login',
                #     wait_until='networkidle',
                #     timeout=self.LOGIN_TIMEOUT_MS
                # )
                #
                # # Fill email field
                # await self.page.fill(
                #     'input[name="email"]',
                #     settings.SUNO_EMAIL
                # )
                #
                # # Fill password field
                # await self.page.fill(
                #     'input[name="password"]',
                #     settings.SUNO_PASSWORD
                # )
                #
                # # Click login button
                # await self.page.click('button[type="submit"]')
                #
                # # Wait for navigation to dashboard
                # await self.page.wait_for_url(
                #     '**/dashboard',
                #     timeout=self.LOGIN_TIMEOUT_MS
                # )
                #
                # # Verify login success (check for user profile element)
                # user_element = await self.page.query_selector('.user-profile')
                # if not user_element:
                #     raise SunoAuthenticationError("Login succeeded but user profile not found")

                # Simulate success for placeholder
                await asyncio.sleep(1)  # Simulate network delay

                self.is_logged_in = True
                self.last_login_time = datetime.utcnow()
                logger.info("[PLACEHOLDER] Login successful")
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

        ⚠️ PLACEHOLDER: Requires actual Suno.com upload flow implementation

        This method contains the framework but not actual implementation.
        Before implementing:
        1. Verify Suno ToS permits automation
        2. Document song creation page URL
        3. Document form field selectors
        4. Document how to extract job ID from response

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

        TODO:
        1. Ensure logged in (call login if needed)
        2. Navigate to song creation page
        3. Fill style prompt field
        4. Fill lyrics field
        5. Set title if provided
        6. Click generate/submit button
        7. Wait for job ID to appear (or extract from API response)
        8. Return job details
        """
        # Ensure logged in
        if not self.is_logged_in:
            await self.login()

        if not self.page:
            raise SunoClientError("Browser not initialized")

        logger.warning("⚠️  Suno upload NOT IMPLEMENTED - requires ToS verification!")
        logger.info(
            f"[PLACEHOLDER] Would upload song: title='{title}', "
            f"style='{style_prompt[:50]}...', lyrics_length={len(lyrics)}"
        )

        # Validate input
        if not style_prompt or not lyrics:
            raise SunoUploadError("Style prompt and lyrics are required")

        if len(lyrics) > 5000:
            logger.warning(
                f"Lyrics length ({len(lyrics)}) exceeds recommended limit (5000)"
            )

        # Placeholder implementation with retry logic
        for attempt in range(self.MAX_RETRIES):
            try:
                logger.info(
                    f"[PLACEHOLDER] Upload attempt {attempt + 1}/{self.MAX_RETRIES}"
                )

                # TODO: Implement actual upload flow
                # Example (REPLACE WITH ACTUAL SUNO SELECTORS):
                #
                # # Navigate to create page
                # await self.page.goto(
                #     'https://suno.com/create',
                #     wait_until='networkidle',
                #     timeout=self.UPLOAD_TIMEOUT_MS
                # )
                #
                # # Wait for form to load
                # await self.page.wait_for_selector('textarea[name="style"]')
                #
                # # Fill style prompt
                # await self.page.fill('textarea[name="style"]', style_prompt)
                #
                # # Fill lyrics
                # await self.page.fill('textarea[name="lyrics"]', lyrics)
                #
                # # Fill title if provided
                # if title:
                #     await self.page.fill('input[name="title"]', title)
                #
                # # Click generate button
                # await self.page.click('button:has-text("Generate")')
                #
                # # Wait for job ID to appear
                # await self.page.wait_for_selector('.job-id', timeout=10000)
                # job_id_element = await self.page.query_selector('.job-id')
                # job_id = await job_id_element.text_content()
                #
                # # Or extract from URL/API response
                # # job_id = self.page.url.split('/')[-1]

                # Simulate upload
                await asyncio.sleep(2)  # Simulate network delay

                # Generate mock job ID
                job_id = f"suno_{int(datetime.utcnow().timestamp())}_{hash(lyrics) % 10000:04d}"

                # Increment operations counter
                self.operations_count += 1

                # Restart browser if needed (prevent memory leaks)
                if self.operations_count >= self.MAX_OPERATIONS_BEFORE_RESTART:
                    logger.info(
                        f"Reached {self.MAX_OPERATIONS_BEFORE_RESTART} operations, "
                        "scheduling browser restart"
                    )
                    # Note: Actual restart happens in background to not block this request
                    asyncio.create_task(self._schedule_restart())

                result = {
                    "job_id": job_id,
                    "status": "processing",
                    "message": "PLACEHOLDER: Song upload initiated (mock)",
                }

                logger.info(f"[PLACEHOLDER] Upload successful: {job_id}")
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
                if attempt < self.MAX_RETRIES - 1:
                    delay = self.RETRY_BASE_DELAY ** (attempt + 1)
                    await asyncio.sleep(delay)
                else:
                    raise SunoUploadError(f"Upload failed: {e}") from e

        raise SunoUploadError("Upload failed after all retries")

    async def check_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check generation status of a Suno job.

        ⚠️ PLACEHOLDER: Requires actual Suno.com status checking

        This method contains the framework but not actual implementation.
        Before implementing:
        1. Document how to check job status (API endpoint or page URL)
        2. Document status values returned by Suno
        3. Document how to extract audio download URL

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

        TODO:
        1. Navigate to job status page or call API endpoint
        2. Extract current status
        3. If completed, extract audio download URL
        4. If failed, extract error message
        5. Return status dict
        """
        if not self.page:
            await self.initialize()

        # Ensure logged in for status checks
        if not self.is_logged_in:
            await self.login()

        logger.warning(
            f"⚠️  Status check NOT IMPLEMENTED for job: {job_id} - requires ToS verification!"
        )

        # Placeholder implementation
        try:
            # TODO: Implement actual status check
            # Example (REPLACE WITH ACTUAL SUNO LOGIC):
            #
            # # Option 1: Navigate to job page
            # await self.page.goto(
            #     f'https://suno.com/jobs/{job_id}',
            #     timeout=self.STATUS_CHECK_TIMEOUT_MS
            # )
            #
            # # Wait for status element
            # await self.page.wait_for_selector('.job-status')
            # status_element = await self.page.query_selector('.job-status')
            # status_text = await status_element.text_content()
            #
            # # Parse status
            # if 'completed' in status_text.lower():
            #     # Extract audio URL
            #     audio_element = await self.page.query_selector('audio source')
            #     audio_url = await audio_element.get_attribute('src')
            #     return {'status': 'completed', 'audio_url': audio_url}
            #
            # elif 'processing' in status_text.lower() or 'queued' in status_text.lower():
            #     return {'status': 'processing'}
            #
            # elif 'failed' in status_text.lower() or 'error' in status_text.lower():
            #     error_element = await self.page.query_selector('.error-message')
            #     error_msg = await error_element.text_content() if error_element else 'Unknown error'
            #     return {'status': 'failed', 'error': error_msg}
            #
            # # Option 2: Call API endpoint (if available)
            # response = await self.page.request.get(f'https://api.suno.com/v1/jobs/{job_id}')
            # data = await response.json()
            # return {
            #     'status': data['status'],
            #     'audio_url': data.get('audio_url'),
            #     'error': data.get('error')
            # }

            # Simulate status check (mock completed job)
            await asyncio.sleep(0.5)

            # For demo: always return completed with mock URL
            result = {
                "status": "completed",
                "audio_url": f"https://cdn.suno.com/mock/{job_id}.mp3",
                "message": "PLACEHOLDER: Job completed (mock)",
            }

            logger.info(f"[PLACEHOLDER] Status check result: {result['status']}")
            return result

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
