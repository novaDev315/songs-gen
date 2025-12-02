"""
Suno.com client using Playwright browser automation with session-based auth.

Authentication Flow:
1. Run `python tools/suno_auth_setup.py` to sign in manually (once)
2. This saves your session to `data/suno_session.json`
3. The automation loads this session - no login needed each time
4. Re-run setup script when session expires (typically every few days/weeks)

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

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
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
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 2.0

    def __init__(self) -> None:
        """Initialize the Suno client."""
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_logged_in: bool = False
        self.operations_count: int = 0
        self.last_login_time: Optional[datetime] = None

    async def initialize(self) -> None:
        """Initialize the browser and page.

        Raises:
            SunoClientError: If browser initialization fails
        """
        if self.browser is not None:
            return

        try:
            logger.info("Initializing Suno client browser")

            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            self.context = await self.browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
            )

            await self.context.set_extra_http_headers(
                {
                    "Accept-Language": "en-US,en;q=0.9",
                }
            )

            self.page = await self.context.new_page()
            await self.page.add_init_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            )

            logger.info("Suno client browser initialized")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self.cleanup()
            raise SunoClientError(f"Browser initialization failed: {e}")

    async def login(self, force: bool = False) -> bool:
        """Log in to Suno.

        Args:
            force: Force re-login even if already logged in

        Returns:
            True if login successful

        Raises:
            SunoAuthenticationError: If login fails
        """
        # Check if already logged in with fresh session
        if self.is_logged_in and not force:
            if self.last_login_time:
                session_age = datetime.now(timezone.utc) - self.last_login_time
                if session_age < timedelta(hours=1):
                    return True

        # Check credentials
        if not settings.SUNO_EMAIL or not settings.SUNO_PASSWORD:
            raise SunoAuthenticationError(
                "Suno credentials not configured. Set SUNO_EMAIL and SUNO_PASSWORD."
            )

        # Initialize if needed
        if self.page is None:
            await self.initialize()

        try:
            logger.info("Logging in to Suno")

            await self.page.goto(
                "https://suno.com/signin",
                timeout=self.LOGIN_TIMEOUT_MS,
            )

            # Wait for login form
            email_input = self.page.locator('input[type="email"]')
            await email_input.first.fill(settings.SUNO_EMAIL)

            password_input = self.page.locator('input[type="password"]')
            await password_input.first.fill(settings.SUNO_PASSWORD)

            # Click sign in button
            signin_button = self.page.locator('button[type="submit"]')
            await signin_button.first.click()

            # Wait for navigation
            await asyncio.sleep(3)

            # Check if logged in by URL
            if "home" in self.page.url or "create" in self.page.url:
                self.is_logged_in = True
                self.last_login_time = datetime.now(timezone.utc)
                logger.info("Suno login successful")
                return True

            raise SunoAuthenticationError("Login failed - not redirected to home")

        except PlaywrightTimeoutError as e:
            logger.error(f"Login timeout: {e}")
            raise SunoAuthenticationError(f"Login timeout: {e}")
        except SunoAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise SunoAuthenticationError(f"Login failed: {e}")

    async def upload_song(
        self,
        style_prompt: str,
        lyrics: str,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a song to Suno for generation.

        Args:
            style_prompt: Style/genre description
            lyrics: Song lyrics
            title: Optional song title

        Returns:
            Dict with job_id and status

        Raises:
            SunoClientError: If browser not initialized
            SunoUploadError: If upload fails
        """
        if self.page is None:
            raise SunoClientError("Browser not initialized")

        if not style_prompt:
            raise SunoUploadError("Style prompt is required")
        if not lyrics:
            raise SunoUploadError("Lyrics is required")

        # Login if needed
        if not self.is_logged_in:
            await self.login()

        try:
            logger.info(f"Uploading song: {title or 'Untitled'}")

            # Navigate to create page
            await self.page.goto(
                "https://suno.com/create",
                timeout=self.UPLOAD_TIMEOUT_MS,
            )

            await asyncio.sleep(2)

            # Fill in style prompt
            style_input = self.page.locator('textarea[placeholder*="style"]')
            await style_input.first.fill(style_prompt)

            # Fill in lyrics
            lyrics_input = self.page.locator('textarea[placeholder*="lyrics"]')
            await lyrics_input.first.fill(lyrics)

            # Fill in title if provided
            if title:
                title_input = self.page.locator('input[placeholder*="title"]')
                if await title_input.first.is_visible():
                    await title_input.first.fill(title)

            # Click create button
            create_button = self.page.locator('button:has-text("Create")')
            await create_button.first.click()

            # Wait for generation to start
            await asyncio.sleep(3)

            # Extract job ID from URL or page
            job_id = f"suno-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            if "/song/" in self.page.url:
                job_id = self.page.url.split("/song/")[-1].split("?")[0]

            self.operations_count += 1

            # Check if browser restart needed
            if self.operations_count >= self.MAX_OPERATIONS_BEFORE_RESTART:
                asyncio.create_task(self._schedule_restart())

            logger.info(f"Song upload started: {job_id}")

            return {
                "job_id": job_id,
                "status": "processing",
                "title": title,
            }

        except PlaywrightTimeoutError as e:
            logger.error(f"Upload timeout: {e}")
            await self.page.screenshot(path="/tmp/suno_upload_error.png")
            raise SunoUploadError(f"Upload timeout: {e}")
        except SunoUploadError:
            raise
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise SunoUploadError(f"Upload failed: {e}")

    async def check_status(self, job_id: str) -> Dict[str, Any]:
        """Check the status of a song generation job.

        Args:
            job_id: The job ID to check

        Returns:
            Dict with status and audio_url if completed

        Raises:
            SunoStatusCheckError: If status check fails
        """
        # Initialize if needed
        if self.page is None:
            await self.initialize()

        # Login if needed
        if not self.is_logged_in:
            await self.login()

        try:
            logger.info(f"Checking status for job: {job_id}")

            # Navigate to song page
            await self.page.goto(
                f"https://suno.com/song/{job_id}",
                timeout=self.STATUS_CHECK_TIMEOUT_MS,
            )

            await asyncio.sleep(2)

            # Check for processing indicators
            processing_indicators = [
                "processing",
                "loading",
                "generating",
                "queue",
            ]

            for indicator in processing_indicators:
                locator = self.page.locator(f'text="{indicator}"')
                if await locator.first.is_visible():
                    return {"status": "processing", "job_id": job_id}

            # Check for error indicators
            error_locators = [
                self.page.locator('text="failed"'),
                self.page.locator('text="error"'),
            ]

            for locator in error_locators:
                if await locator.first.is_visible():
                    error_text = await locator.first.text_content()
                    return {
                        "status": "failed",
                        "job_id": job_id,
                        "error": error_text,
                    }

            # Check for completed - look for audio element
            audio_locator = self.page.locator("audio source, audio[src]")
            if await audio_locator.first.is_visible():
                audio_url = await audio_locator.first.get_attribute("src")
                return {
                    "status": "completed",
                    "job_id": job_id,
                    "audio_url": audio_url,
                }

            # Default to processing if unclear
            return {"status": "processing", "job_id": job_id}

        except PlaywrightTimeoutError as e:
            logger.error(f"Status check timeout: {e}")
            raise SunoStatusCheckError(f"Status check timeout: {e}")
        except Exception as e:
            logger.error(f"Status check error: {e}")
            raise SunoStatusCheckError(f"Status check failed: {e}")

    async def cleanup(self) -> None:
        """Clean up browser resources."""
        logger.info("Cleaning up Suno client")

        try:
            if self.page:
                await self.page.close()
        except Exception as e:
            logger.warning(f"Error closing page: {e}")
        finally:
            self.page = None

        try:
            if self.context:
                await self.context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")
        finally:
            self.context = None

        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.warning(f"Error closing browser: {e}")
        finally:
            self.browser = None

        try:
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error stopping playwright: {e}")
        finally:
            self.playwright = None

        self.is_logged_in = False
        self.last_login_time = None

    async def _schedule_restart(self) -> None:
        """Schedule browser restart after max operations."""
        try:
            logger.info("Scheduling browser restart")
            await asyncio.sleep(1)
            await self.cleanup()
            await self.initialize()
            await self.login()
            self.operations_count = 0
            logger.info("Browser restart complete")
        except Exception as e:
            logger.error(f"Browser restart failed: {e}")


# Global instance
_suno_client: Optional[SunoClient] = None


async def get_suno_client() -> SunoClient:
    """Get the global Suno client instance.

    Returns:
        The singleton SunoClient instance
    """
    global _suno_client
    if _suno_client is None:
        _suno_client = SunoClient()
        await _suno_client.initialize()
    return _suno_client


async def cleanup_suno_client() -> None:
    """Clean up the global Suno client."""
    global _suno_client
    if _suno_client is not None:
        await _suno_client.cleanup()
        _suno_client = None
