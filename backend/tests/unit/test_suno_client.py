"""Unit tests for Suno client service.

Tests for Suno.com browser automation using Playwright.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch, Mock, PropertyMock

import pytest
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from app.services.suno_client import (
    SunoClient,
    SunoClientError,
    SunoAuthenticationError,
    SunoUploadError,
    SunoStatusCheckError,
    get_suno_client,
    cleanup_suno_client,
)


@pytest.mark.unit
class TestSunoClientExceptions:
    """Test Suno client exception classes."""

    def test_suno_client_error_inheritance(self):
        """Test SunoClientError inherits from Exception."""
        error = SunoClientError("Test error")
        assert isinstance(error, Exception)
        assert str(error) == "Test error"

    def test_suno_authentication_error_inheritance(self):
        """Test SunoAuthenticationError inherits from SunoClientError."""
        error = SunoAuthenticationError("Auth failed")
        assert isinstance(error, SunoClientError)
        assert str(error) == "Auth failed"

    def test_suno_upload_error_inheritance(self):
        """Test SunoUploadError inherits from SunoClientError."""
        error = SunoUploadError("Upload failed")
        assert isinstance(error, SunoClientError)
        assert str(error) == "Upload failed"

    def test_suno_status_check_error_inheritance(self):
        """Test SunoStatusCheckError inherits from SunoClientError."""
        error = SunoStatusCheckError("Status check failed")
        assert isinstance(error, SunoClientError)
        assert str(error) == "Status check failed"


@pytest.mark.unit
class TestSunoClientInit:
    """Test SunoClient initialization."""

    def test_init_sets_defaults(self):
        """Test that initialization sets default values."""
        client = SunoClient()

        assert client.playwright is None
        assert client.browser is None
        assert client.context is None
        assert client.page is None
        assert client.is_logged_in is False
        assert client.operations_count == 0
        assert client.last_login_time is None

    def test_class_constants(self):
        """Test class constants are defined."""
        assert SunoClient.MAX_OPERATIONS_BEFORE_RESTART == 100
        assert SunoClient.LOGIN_TIMEOUT_MS == 30000
        assert SunoClient.UPLOAD_TIMEOUT_MS == 60000
        assert SunoClient.STATUS_CHECK_TIMEOUT_MS == 10000
        assert SunoClient.MAX_RETRIES == 3
        assert SunoClient.RETRY_BASE_DELAY == 2.0


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientInitialize:
    """Test SunoClient.initialize method."""

    async def test_initialize_skips_if_already_initialized(self):
        """Test initialize skips if browser already exists."""
        client = SunoClient()
        client.browser = MagicMock()  # Already initialized

        with patch('app.services.suno_client.async_playwright') as mock_playwright:
            await client.initialize()

            # Should not call async_playwright since browser already exists
            mock_playwright.assert_not_called()

    async def test_initialize_creates_browser(self):
        """Test initialize creates browser and page."""
        client = SunoClient()

        mock_page = AsyncMock()
        mock_page.add_init_script = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.set_extra_http_headers = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_chromium = AsyncMock()
        mock_chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_instance = AsyncMock()
        mock_pw_instance.chromium = mock_chromium

        mock_playwright = AsyncMock()
        mock_playwright.start = AsyncMock(return_value=mock_pw_instance)

        with patch('app.services.suno_client.async_playwright', return_value=mock_playwright):
            await client.initialize()

            assert client.browser is mock_browser
            assert client.context is mock_context
            assert client.page is mock_page
            mock_chromium.launch.assert_called_once()

    async def test_initialize_handles_error(self):
        """Test initialize handles errors and cleans up."""
        client = SunoClient()

        mock_playwright = AsyncMock()
        mock_playwright.start.side_effect = Exception("Browser launch failed")

        with patch('app.services.suno_client.async_playwright', return_value=mock_playwright):
            with patch.object(client, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
                with pytest.raises(SunoClientError, match="Browser initialization failed"):
                    await client.initialize()

                mock_cleanup.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientLogin:
    """Test SunoClient.login method."""

    async def test_login_skips_if_already_logged_in(self):
        """Test login skips if already logged in with fresh session."""
        client = SunoClient()
        client.is_logged_in = True
        client.last_login_time = datetime.now(timezone.utc) - timedelta(minutes=30)

        result = await client.login()

        assert result is True

    async def test_login_force_relogin(self):
        """Test login forces relogin when force=True."""
        client = SunoClient()
        client.is_logged_in = True
        client.last_login_time = datetime.now(timezone.utc)
        client.page = AsyncMock()

        # Mock the login process
        with patch.object(client, 'initialize', new_callable=AsyncMock):
            with patch('app.services.suno_client.settings') as mock_settings:
                mock_settings.SUNO_EMAIL = "test@example.com"
                mock_settings.SUNO_PASSWORD = "testpassword"

                # Mock page interactions
                mock_locator = AsyncMock()
                mock_locator.is_visible = AsyncMock(return_value=True)
                mock_locator.fill = AsyncMock()
                mock_locator.click = AsyncMock()
                mock_locator.first = mock_locator
                client.page.locator = Mock(return_value=mock_locator)
                client.page.goto = AsyncMock()
                client.page.url = "https://suno.com/home"
                client.page.screenshot = AsyncMock()

                result = await client.login(force=True)

                assert result is True
                assert client.is_logged_in is True

    async def test_login_no_credentials(self):
        """Test login raises error when credentials not configured."""
        client = SunoClient()
        client.page = AsyncMock()

        with patch('app.services.suno_client.settings') as mock_settings:
            mock_settings.SUNO_EMAIL = ""
            mock_settings.SUNO_PASSWORD = ""

            with pytest.raises(SunoAuthenticationError, match="credentials not configured"):
                await client.login()

    async def test_login_handles_timeout(self):
        """Test login handles timeout errors."""
        client = SunoClient()
        client.page = AsyncMock()
        client.page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))

        with patch('app.services.suno_client.settings') as mock_settings:
            mock_settings.SUNO_EMAIL = "test@example.com"
            mock_settings.SUNO_PASSWORD = "testpassword"

            with patch('asyncio.sleep', new_callable=AsyncMock):
                with pytest.raises(SunoAuthenticationError, match="timeout"):
                    await client.login()

    async def test_login_initializes_if_no_page(self):
        """Test login initializes browser if page doesn't exist."""
        client = SunoClient()
        client.page = None

        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        mock_page.locator = Mock(return_value=mock_locator)
        mock_page.goto = AsyncMock()
        mock_page.url = "https://suno.com/home"
        mock_page.screenshot = AsyncMock()

        async def set_page():
            client.page = mock_page

        with patch.object(client, 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = set_page

            with patch('app.services.suno_client.settings') as mock_settings:
                mock_settings.SUNO_EMAIL = "test@example.com"
                mock_settings.SUNO_PASSWORD = "testpassword"

                result = await client.login()

                mock_init.assert_called_once()
                assert result is True


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientUploadSong:
    """Test SunoClient.upload_song method."""

    async def test_upload_song_success(self):
        """Test successful song upload."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()
        client.operations_count = 0

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        mock_locator.get_attribute = AsyncMock(return_value=None)
        mock_locator.text_content = AsyncMock(return_value=None)
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.url = "https://suno.com/song/generated123"

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('asyncio.create_task'):
                result = await client.upload_song(
                    style_prompt="Pop, upbeat, catchy",
                    lyrics="[Verse 1]\nTest lyrics",
                    title="Test Song",
                )

                assert "job_id" in result
                assert result["status"] == "processing"
                assert client.operations_count == 1

    async def test_upload_song_logs_in_if_needed(self):
        """Test upload_song logs in if not logged in."""
        client = SunoClient()
        client.is_logged_in = False
        client.page = AsyncMock()

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.url = "https://suno.com/song/generated123"

        with patch.object(client, 'login', new_callable=AsyncMock) as mock_login:
            mock_login.return_value = True

            with patch('asyncio.sleep', new_callable=AsyncMock):
                with patch('asyncio.create_task'):
                    result = await client.upload_song(
                        style_prompt="Pop, upbeat",
                        lyrics="[Verse]\nTest",
                    )

                    mock_login.assert_called_once()

    async def test_upload_song_no_page(self):
        """Test upload_song raises error when no page."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = None

        with pytest.raises(SunoClientError, match="Browser not initialized"):
            await client.upload_song("style", "lyrics")

    async def test_upload_song_missing_inputs(self):
        """Test upload_song raises error for missing inputs."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()

        with pytest.raises(SunoUploadError, match="required"):
            await client.upload_song("", "lyrics")

        with pytest.raises(SunoUploadError, match="required"):
            await client.upload_song("style", "")

    async def test_upload_song_handles_timeout(self):
        """Test upload_song handles timeout errors."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()
        client.page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
        client.page.screenshot = AsyncMock()

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with pytest.raises(SunoUploadError, match="timeout"):
                await client.upload_song("Pop, upbeat", "[Verse]\nTest")

    async def test_upload_song_triggers_browser_restart(self):
        """Test upload_song triggers browser restart after max operations."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()
        client.operations_count = 99  # One before max

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.url = "https://suno.com/song/123"

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('asyncio.create_task') as mock_create_task:
                await client.upload_song("Pop", "[Verse]\nTest")

                # Should have scheduled restart
                mock_create_task.assert_called_once()
                assert client.operations_count == 100


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientCheckStatus:
    """Test SunoClient.check_status method."""

    async def test_check_status_processing(self):
        """Test check_status when song is still processing."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.first = mock_locator
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.content = AsyncMock(return_value="<html>...</html>")

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await client.check_status("job-123")

            assert result["status"] == "processing"

    async def test_check_status_completed(self):
        """Test check_status when song is completed."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()

        # Processing indicators not visible
        mock_locator_processing = AsyncMock()
        mock_locator_processing.is_visible = AsyncMock(return_value=False)
        mock_locator_processing.first = mock_locator_processing

        # Error indicators not visible
        mock_locator_error = AsyncMock()
        mock_locator_error.is_visible = AsyncMock(return_value=False)
        mock_locator_error.first = mock_locator_error

        # Audio element visible with URL
        mock_locator_audio = AsyncMock()
        mock_locator_audio.is_visible = AsyncMock(return_value=True)
        mock_locator_audio.get_attribute = AsyncMock(return_value="https://cdn.suno.com/audio.mp3")
        mock_locator_audio.first = mock_locator_audio

        def locator_side_effect(selector):
            if "processing" in selector.lower() or "loading" in selector.lower() or "queue" in selector.lower():
                return mock_locator_processing
            elif "failed" in selector.lower() or "error" in selector.lower():
                return mock_locator_error
            else:
                return mock_locator_audio

        client.page.locator = Mock(side_effect=locator_side_effect)
        client.page.goto = AsyncMock()
        client.page.content = AsyncMock(return_value="<html>...</html>")
        client.page.title = AsyncMock(return_value="Song Title")

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await client.check_status("job-123")

            assert result["status"] == "completed"
            assert "audio_url" in result

    async def test_check_status_failed(self):
        """Test check_status when song generation failed."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()

        # Processing indicators not visible
        mock_locator_processing = AsyncMock()
        mock_locator_processing.is_visible = AsyncMock(return_value=False)
        mock_locator_processing.first = mock_locator_processing

        # Error indicator visible
        mock_locator_error = AsyncMock()
        mock_locator_error.is_visible = AsyncMock(return_value=True)
        mock_locator_error.text_content = AsyncMock(return_value="Generation failed due to content policy")
        mock_locator_error.first = mock_locator_error

        def locator_side_effect(selector):
            if "processing" in selector.lower() or "loading" in selector.lower():
                return mock_locator_processing
            else:
                return mock_locator_error

        client.page.locator = Mock(side_effect=locator_side_effect)
        client.page.goto = AsyncMock()
        client.page.content = AsyncMock(return_value="<html>...</html>")

        with patch('asyncio.sleep', new_callable=AsyncMock):
            result = await client.check_status("job-123")

            assert result["status"] == "failed"
            assert "error" in result

    async def test_check_status_initializes_if_needed(self):
        """Test check_status initializes browser if needed."""
        client = SunoClient()
        client.page = None

        mock_page = AsyncMock()
        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(return_value=True)
        mock_locator.first = mock_locator
        mock_page.locator = Mock(return_value=mock_locator)
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>...</html>")

        async def set_page():
            client.page = mock_page

        with patch.object(client, 'initialize', new_callable=AsyncMock) as mock_init:
            mock_init.side_effect = set_page

            with patch.object(client, 'login', new_callable=AsyncMock):
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    await client.check_status("job-123")

                    mock_init.assert_called_once()

    async def test_check_status_timeout_error(self):
        """Test check_status handles timeout errors."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()
        client.page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))

        with pytest.raises(SunoStatusCheckError, match="timeout"):
            await client.check_status("job-123")


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientCleanup:
    """Test SunoClient.cleanup method."""

    async def test_cleanup_closes_all_resources(self):
        """Test cleanup closes page, context, browser, and playwright."""
        client = SunoClient()
        client.page = AsyncMock()
        client.context = AsyncMock()
        client.browser = AsyncMock()
        client.playwright = AsyncMock()
        client.is_logged_in = True
        client.last_login_time = datetime.now(timezone.utc)

        await client.cleanup()

        client.page.close.assert_called_once()
        client.context.close.assert_called_once()
        client.browser.close.assert_called_once()
        client.playwright.stop.assert_called_once()
        assert client.page is None
        assert client.context is None
        assert client.browser is None
        assert client.playwright is None
        assert client.is_logged_in is False
        assert client.last_login_time is None

    async def test_cleanup_handles_errors(self):
        """Test cleanup handles errors during resource closing."""
        client = SunoClient()
        client.page = AsyncMock()
        client.page.close = AsyncMock(side_effect=Exception("Page close error"))
        client.context = AsyncMock()
        client.browser = AsyncMock()
        client.playwright = AsyncMock()

        # Should not raise, just log errors
        await client.cleanup()

        assert client.page is None
        assert client.context is None
        assert client.browser is None
        assert client.playwright is None

    async def test_cleanup_with_no_resources(self):
        """Test cleanup with no resources to clean."""
        client = SunoClient()

        # Should not raise
        await client.cleanup()

        assert client.page is None
        assert client.is_logged_in is False


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientScheduleRestart:
    """Test SunoClient._schedule_restart method."""

    async def test_schedule_restart_reinitializes(self):
        """Test _schedule_restart reinitializes browser."""
        client = SunoClient()
        client.operations_count = 100

        with patch.object(client, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            with patch.object(client, 'initialize', new_callable=AsyncMock) as mock_init:
                with patch.object(client, 'login', new_callable=AsyncMock) as mock_login:
                    with patch('asyncio.sleep', new_callable=AsyncMock):
                        await client._schedule_restart()

                        mock_cleanup.assert_called_once()
                        mock_init.assert_called_once()
                        mock_login.assert_called_once()
                        assert client.operations_count == 0

    async def test_schedule_restart_handles_error(self):
        """Test _schedule_restart handles errors."""
        client = SunoClient()

        with patch.object(client, 'cleanup', new_callable=AsyncMock) as mock_cleanup:
            mock_cleanup.side_effect = Exception("Cleanup failed")

            with patch('asyncio.sleep', new_callable=AsyncMock):
                # Should not raise
                await client._schedule_restart()


@pytest.mark.unit
@pytest.mark.asyncio
class TestGlobalSunoClient:
    """Test global Suno client functions."""

    async def test_get_suno_client_creates_singleton(self):
        """Test get_suno_client creates and returns singleton."""
        import app.services.suno_client as sc
        sc._suno_client = None

        with patch.object(SunoClient, 'initialize', new_callable=AsyncMock):
            client1 = await get_suno_client()
            client2 = await get_suno_client()

            assert client1 is client2
            assert isinstance(client1, SunoClient)

        # Clean up
        sc._suno_client = None

    async def test_cleanup_suno_client(self):
        """Test cleanup_suno_client cleans up global client."""
        import app.services.suno_client as sc

        mock_client = AsyncMock(spec=SunoClient)
        sc._suno_client = mock_client

        await cleanup_suno_client()

        mock_client.cleanup.assert_called_once()
        assert sc._suno_client is None

    async def test_cleanup_suno_client_no_client(self):
        """Test cleanup_suno_client with no client."""
        import app.services.suno_client as sc
        sc._suno_client = None

        # Should not raise
        await cleanup_suno_client()

        assert sc._suno_client is None


@pytest.mark.unit
@pytest.mark.asyncio
class TestSunoClientRetryLogic:
    """Test Suno client retry logic."""

    async def test_login_retries_on_failure(self):
        """Test login retries on failure."""
        client = SunoClient()
        client.page = AsyncMock()

        call_count = 0

        async def fail_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return True

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(side_effect=fail_then_succeed)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.url = "https://suno.com/home"

        with patch('app.services.suno_client.settings') as mock_settings:
            mock_settings.SUNO_EMAIL = "test@example.com"
            mock_settings.SUNO_PASSWORD = "testpassword"

            with patch('asyncio.sleep', new_callable=AsyncMock):
                result = await client.login()

                assert result is True
                assert call_count >= 1

    async def test_upload_retries_on_failure(self):
        """Test upload retries on failure."""
        client = SunoClient()
        client.is_logged_in = True
        client.page = AsyncMock()

        call_count = 0

        async def fail_twice_then_succeed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return True

        mock_locator = AsyncMock()
        mock_locator.is_visible = AsyncMock(side_effect=fail_twice_then_succeed)
        mock_locator.fill = AsyncMock()
        mock_locator.click = AsyncMock()
        mock_locator.first = mock_locator
        client.page.locator = Mock(return_value=mock_locator)
        client.page.goto = AsyncMock()
        client.page.url = "https://suno.com/song/123"
        client.page.screenshot = AsyncMock()

        with patch('asyncio.sleep', new_callable=AsyncMock):
            with patch('asyncio.create_task'):
                result = await client.upload_song("Pop", "[Verse]\nTest")

                assert "job_id" in result
