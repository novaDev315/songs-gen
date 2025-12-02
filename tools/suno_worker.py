#!/usr/bin/env python3
"""
Standalone Suno Worker - Runs OUTSIDE Docker with visible browser.

This script polls the backend API for pending Suno tasks and processes them
using a visible browser that can bypass Cloudflare.

Usage:
    cd /mnt/coding/projects/personal/songs-gen
    python tools/suno_worker.py

Requirements:
    pip install playwright requests
    playwright install chromium
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_BASE = os.getenv('API_BASE', 'http://localhost:7000/api/v1')
API_USERNAME = os.getenv('API_USERNAME', 'admin')
API_PASSWORD = os.getenv('API_PASSWORD', 'pass123')
SESSION_FILE = Path(__file__).parent.parent / 'data' / 'suno_session.json'
DOWNLOAD_FOLDER = Path(__file__).parent.parent / 'downloads'
POLL_INTERVAL = 30  # seconds


class SunoWorker:
    def __init__(self):
        self.token: Optional[str] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def login_api(self) -> bool:
        """Login to the backend API and get JWT token."""
        try:
            resp = requests.post(
                f'{API_BASE}/auth/login',
                json={'username': API_USERNAME, 'password': API_PASSWORD}
            )
            if resp.status_code == 200:
                self.token = resp.json()['access_token']
                logger.info('Logged into backend API')
                return True
            else:
                logger.error(f'API login failed: {resp.text}')
                return False
        except Exception as e:
            logger.error(f'API login error: {e}')
            return False

    def api_headers(self) -> dict:
        return {'Authorization': f'Bearer {self.token}'}

    def get_pending_task(self) -> Optional[dict]:
        """Get next pending Suno task from the queue."""
        tasks = self.get_pending_tasks(limit=1)
        return tasks[0] if tasks else None

    def get_pending_tasks(self, limit: int = 3) -> list[dict]:
        """Get multiple pending Suno tasks from the queue.

        Args:
            limit: Maximum number of tasks to fetch

        Returns:
            List of pending task dicts
        """
        try:
            resp = requests.get(
                f'{API_BASE}/queue/tasks',
                params={'status_filter': 'pending', 'task_type': 'suno_upload', 'limit': limit},
                headers=self.api_headers()
            )
            if resp.status_code == 200:
                return resp.json().get('items', [])
            return []
        except Exception as e:
            logger.error(f'Error getting pending tasks: {e}')
            return []

    def get_song(self, song_id: str) -> Optional[dict]:
        """Get song details."""
        try:
            resp = requests.get(
                f'{API_BASE}/songs/{song_id}',
                headers=self.api_headers()
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            logger.error(f'Error getting song: {e}')
            return None

    def update_task(self, task_id: int, status: str, error_message: str = None):
        """Update task status via API."""
        try:
            # Use retry endpoint to reset or mark as failed
            if status == 'failed':
                # Just log for now - the worker in Docker handles retries
                logger.error(f'Task {task_id} failed: {error_message}')
        except Exception as e:
            logger.error(f'Error updating task: {e}')

    def update_song_status(self, song_id: str, status: str):
        """Update song status."""
        try:
            requests.put(
                f'{API_BASE}/songs/{song_id}',
                json={'status': status},
                headers=self.api_headers()
            )
        except Exception as e:
            logger.error(f'Error updating song status: {e}')

    def create_suno_job(self, song_id: str, suno_job_id: str):
        """Record Suno job in database."""
        try:
            # This would need a dedicated endpoint
            logger.info(f'Suno job created: {suno_job_id} for song {song_id}')
        except Exception as e:
            logger.error(f'Error creating Suno job: {e}')

    async def initialize_browser(self):
        """Initialize visible browser with saved session."""
        if self.browser:
            return

        logger.info('Initializing browser...')

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Visible browser!
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--start-maximized',
            ]
        )

        # Load session if available
        context_options = {
            'viewport': {'width': 1280, 'height': 900},
            'user_agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        }

        if SESSION_FILE.exists():
            logger.info(f'Loading session from {SESSION_FILE}')
            context_options['storage_state'] = str(SESSION_FILE)

        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()

        # Hide webdriver
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        logger.info('Browser initialized')

    async def upload_to_suno(self, style_prompt: str, lyrics: str, title: str) -> Optional[str]:
        """Upload song to Suno and return job ID."""
        await self.initialize_browser()

        logger.info(f'Uploading to Suno: {title}')

        try:
            # Navigate to Suno create page
            await self.page.goto('https://suno.com/create', wait_until='networkidle')
            await asyncio.sleep(2)

            # Take screenshot for debugging
            await self.page.screenshot(path='/tmp/suno_page.png')
            logger.info('Screenshot saved to /tmp/suno_page.png')

            # Check if we need to login
            if 'sign-in' in self.page.url.lower():
                logger.warning('Not logged in! Please run suno_auth_setup.py first')
                return None

            # Click Custom tab if visible
            try:
                custom_tab = self.page.locator('button:has-text("Custom")')
                if await custom_tab.is_visible(timeout=3000):
                    await custom_tab.click()
                    await asyncio.sleep(0.5)
                    logger.info('Clicked Custom tab')
            except:
                pass

            # Fill Style of Music FIRST
            logger.info('Filling style...')
            style_filled = False
            style_selectors = [
                'textarea[placeholder*="style" i]',
                'textarea[placeholder*="Enter style" i]',
                'input[placeholder*="style" i]',
            ]
            for selector in style_selectors:
                try:
                    field = self.page.locator(selector).first
                    if await field.is_visible(timeout=2000):
                        await field.click()
                        await field.fill(style_prompt)
                        style_filled = True
                        logger.info(f'Filled style using: {selector}')
                        break
                except:
                    continue

            if not style_filled:
                # Try first textarea
                textareas = self.page.locator('textarea')
                count = await textareas.count()
                if count > 0:
                    await textareas.first.click()
                    await textareas.first.fill(style_prompt)
                    style_filled = True
                    logger.info('Filled style using first textarea')

            await asyncio.sleep(0.5)

            # Fill Lyrics SECOND
            logger.info('Filling lyrics...')
            lyrics_filled = False
            lyrics_selectors = [
                'textarea[placeholder*="lyrics" i]',
                'textarea[placeholder*="Enter your own" i]',
            ]
            for selector in lyrics_selectors:
                try:
                    field = self.page.locator(selector).first
                    if await field.is_visible(timeout=2000):
                        await field.click()
                        await field.fill(lyrics)
                        lyrics_filled = True
                        logger.info(f'Filled lyrics using: {selector}')
                        break
                except:
                    continue

            if not lyrics_filled:
                # Try second textarea
                textareas = self.page.locator('textarea')
                count = await textareas.count()
                if count >= 2:
                    await textareas.nth(1).click()
                    await textareas.nth(1).fill(lyrics)
                    lyrics_filled = True
                    logger.info('Filled lyrics using second textarea')

            # Take screenshot after filling
            await self.page.screenshot(path='/tmp/suno_filled.png')
            logger.info('Screenshot saved to /tmp/suno_filled.png')

            # Click Create/Generate button
            logger.info('Clicking generate...')
            submit_selectors = [
                'button:has-text("Create")',
                'button:has-text("Generate")',
                'button:has-text("Make")',
            ]
            for selector in submit_selectors:
                try:
                    btn = self.page.locator(selector).first
                    if await btn.is_visible(timeout=2000):
                        await btn.click()
                        logger.info(f'Clicked: {selector}')
                        break
                except:
                    continue

            # Wait for generation to start
            await asyncio.sleep(5)
            await self.page.screenshot(path='/tmp/suno_submitted.png')

            # Generate job ID
            job_id = f"suno_{int(datetime.now(timezone.utc).timestamp())}_{hash(lyrics) % 10000:04d}"
            logger.info(f'Job ID: {job_id}')

            return job_id

        except Exception as e:
            logger.error(f'Upload failed: {e}')
            await self.page.screenshot(path='/tmp/suno_error.png')
            return None

    async def find_song_by_title(self, title: str) -> Optional[object]:
        """Find a song element on the page by its title.

        Args:
            title: Song title to search for

        Returns:
            Locator for the song container element, or None
        """
        try:
            # Common selectors for song cards/items containing the title
            song_card_selectors = [
                f'[data-testid="song-card"]:has-text("{title}")',
                f'.song-card:has-text("{title}")',
                f'[class*="song"]:has-text("{title}")',
                f'[class*="track"]:has-text("{title}")',
                f'article:has-text("{title}")',
                f'div[role="listitem"]:has-text("{title}")',
            ]

            for selector in song_card_selectors:
                try:
                    element = self.page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        logger.info(f'Found song card with title: {title}')
                        return element
                except:
                    continue

            # Fallback: find by exact text match
            title_element = self.page.get_by_text(title, exact=False).first
            if await title_element.is_visible(timeout=2000):
                # Try to get parent container
                parent = title_element.locator('xpath=ancestor::article | ancestor::div[contains(@class, "song")] | ancestor::div[contains(@class, "track")]').first
                if await parent.is_visible(timeout=1000):
                    return parent
                return title_element

        except Exception as e:
            logger.debug(f'Could not find song by title: {e}')

        return None

    async def get_song_status(self, song_element) -> str:
        """Get the status of a song (generating, complete, failed).

        Args:
            song_element: Locator for the song element

        Returns:
            Status string: 'generating', 'complete', or 'unknown'
        """
        try:
            # Check for loading/generating indicators
            generating_indicators = [
                'text="Generating"',
                'text="Creating"',
                'text="Processing"',
                '[class*="loading"]',
                '[class*="spinner"]',
                '[class*="progress"]',
            ]

            for indicator in generating_indicators:
                try:
                    if await song_element.locator(indicator).first.is_visible(timeout=500):
                        return 'generating'
                except:
                    continue

            # Check for audio player (indicates complete)
            audio_indicators = [
                'audio',
                '[class*="player"]',
                'button[aria-label*="play"]',
                '[data-testid*="play"]',
            ]

            for indicator in audio_indicators:
                try:
                    if await song_element.locator(indicator).first.is_visible(timeout=500):
                        return 'complete'
                except:
                    continue

            return 'unknown'

        except Exception as e:
            logger.debug(f'Error checking song status: {e}')
            return 'unknown'

    async def get_audio_urls_from_song(self, song_element) -> list[str]:
        """Extract audio URLs from a song element.

        Args:
            song_element: Locator for the song element

        Returns:
            List of audio URLs
        """
        urls = set()

        try:
            # Look for audio sources within this song element
            audio_selectors = [
                'audio source',
                'audio',
                'a[href*=".mp3"]',
                'a[download]',
            ]

            for selector in audio_selectors:
                try:
                    elements = song_element.locator(selector)
                    count = await elements.count()
                    for i in range(count):
                        element = elements.nth(i)
                        url = await element.get_attribute('src') or await element.get_attribute('href')
                        if url and ('.mp3' in url or 'audio' in url or 'cdn' in url):
                            urls.add(url)
                except:
                    continue

            # Also check for data attributes that might contain URLs
            try:
                data_url = await song_element.get_attribute('data-audio-url')
                if data_url:
                    urls.add(data_url)
            except:
                pass

        except Exception as e:
            logger.debug(f'Error extracting audio URLs: {e}')

        return list(urls)

    async def wait_for_generation(self, title: str, max_wait: int = 300) -> list[str]:
        """Wait for song generation by searching for the song by title.

        Suno generates 2 variations per upload. This method searches for
        the specific song by title and waits for it to complete.

        Args:
            title: Song title to search for
            max_wait: Maximum seconds to wait for generation

        Returns:
            List of audio URLs (typically 2 variations)
        """
        logger.info(f'Waiting for song "{title}" to generate (max {max_wait}s)...')
        start_time = time.time()
        last_status = None

        while time.time() - start_time < max_wait:
            try:
                # Find the song by title
                song_element = await self.find_song_by_title(title)

                if song_element:
                    # Check status
                    status = await self.get_song_status(song_element)

                    if status != last_status:
                        logger.info(f'Song status: {status}')
                        last_status = status

                    if status == 'complete':
                        # Try to get audio URLs
                        audio_urls = await self.get_audio_urls_from_song(song_element)

                        if len(audio_urls) >= 2:
                            logger.info(f'Found {len(audio_urls)} audio URLs for "{title}"')
                            return audio_urls
                        elif audio_urls:
                            # Wait a bit more for second variation
                            logger.info(f'Found {len(audio_urls)} URL(s), waiting for more...')
                            await asyncio.sleep(5)
                            continue

                    elif status == 'generating':
                        elapsed = int(time.time() - start_time)
                        if elapsed % 30 == 0:  # Log every 30s
                            logger.info(f'Still generating... ({elapsed}s elapsed)')

                else:
                    logger.debug(f'Song "{title}" not found on page yet')

                await asyncio.sleep(10)
                await self.page.screenshot(path='/tmp/suno_waiting.png')

            except Exception as e:
                logger.error(f'Error waiting for generation: {e}')
                await asyncio.sleep(5)

        # Timeout - try one more time to get whatever we can
        logger.warning(f'Timed out waiting for "{title}"')
        song_element = await self.find_song_by_title(title)
        if song_element:
            audio_urls = await self.get_audio_urls_from_song(song_element)
            if audio_urls:
                logger.info(f'Found {len(audio_urls)} URLs after timeout')
                return audio_urls

        return []

    async def download_audio(self, audio_url: str, song_id: str, variation: int = 0) -> Optional[Path]:
        """Download audio file from URL.

        Args:
            audio_url: URL to download from
            song_id: Song ID for filename
            variation: Variation index (0 or 1)

        Returns:
            Path to downloaded file, None on failure
        """
        try:
            import aiohttp
            import aiofiles

            DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

            # Include variation in filename
            if variation > 0:
                file_path = DOWNLOAD_FOLDER / f"{song_id}_v{variation}.mp3"
            else:
                file_path = DOWNLOAD_FOLDER / f"{song_id}.mp3"

            if file_path.exists():
                logger.info(f'Audio already downloaded: {file_path}')
                return file_path

            logger.info(f'Downloading variation {variation} to {file_path}')

            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    resp.raise_for_status()
                    async with aiofiles.open(file_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)

            if file_path.exists() and file_path.stat().st_size > 0:
                logger.info(f'Downloaded: {file_path} ({file_path.stat().st_size} bytes)')
                return file_path
            else:
                logger.error('Downloaded file is empty')
                return None

        except Exception as e:
            logger.error(f'Download failed: {e}')
            return None

    async def download_all_variations(self, audio_urls: list[str], song_id: str) -> list[Path]:
        """Download all audio variations.

        Args:
            audio_urls: List of audio URLs
            song_id: Song ID for filenames

        Returns:
            List of downloaded file paths
        """
        downloaded = []
        for i, url in enumerate(audio_urls):
            file_path = await self.download_audio(url, song_id, variation=i)
            if file_path:
                downloaded.append(file_path)
        return downloaded

    async def upload_single_song(self, song: dict) -> Optional[str]:
        """Upload a single song to Suno (without waiting).

        Args:
            song: Song data dict

        Returns:
            Song title if upload successful, None otherwise
        """
        song_id = song['id']
        title = song['title']

        logger.info(f'Uploading: {title}')

        job_id = await self.upload_to_suno(
            style_prompt=song['style_prompt'],
            lyrics=song['lyrics'],
            title=title
        )

        if job_id:
            logger.info(f'Uploaded: {title}')
            self.update_song_status(song_id, 'generating')
            return title
        else:
            logger.error(f'Upload failed: {title}')
            self.update_song_status(song_id, 'failed')
            return None

    async def wait_and_download_song(self, song: dict) -> bool:
        """Wait for a song to generate and download it.

        Args:
            song: Song data dict

        Returns:
            True if successful, False otherwise
        """
        song_id = song['id']
        title = song['title']

        audio_urls = await self.wait_for_generation(title=title)

        if not audio_urls:
            logger.error(f'Failed to get audio for: {title}')
            self.update_song_status(song_id, 'failed')
            return False

        logger.info(f'Found {len(audio_urls)} variations for: {title}')

        downloaded_files = await self.download_all_variations(audio_urls, song_id)

        if downloaded_files:
            logger.info(f'Completed: {title} ({len(downloaded_files)} variations)')
            self.update_song_status(song_id, 'downloaded')
            return True
        else:
            logger.error(f'Download failed: {title}')
            self.update_song_status(song_id, 'failed')
            return False

    async def process_tasks_batch(self, tasks: list[dict], batch_size: int = 3):
        """Process multiple tasks in parallel batches.

        Uploads up to batch_size songs at once, then waits for all to complete.

        Args:
            tasks: List of task dicts
            batch_size: Number of songs to upload concurrently (default 3)
        """
        logger.info(f'Processing batch of {len(tasks)} tasks (batch_size={batch_size})')

        # Get song details for all tasks
        songs = []
        for task in tasks:
            song = self.get_song(task['song_id'])
            if song:
                songs.append(song)
            else:
                logger.error(f'Song not found: {task["song_id"]}')

        if not songs:
            return

        # Process in batches
        for i in range(0, len(songs), batch_size):
            batch = songs[i:i + batch_size]
            logger.info(f'=== Batch {i // batch_size + 1}: {len(batch)} songs ===')

            # Phase 1: Upload all songs in batch (quick, one after another)
            uploaded_songs = []
            for song in batch:
                title = await self.upload_single_song(song)
                if title:
                    uploaded_songs.append(song)
                # Small delay between uploads
                await asyncio.sleep(2)

            if not uploaded_songs:
                logger.error('No songs uploaded in this batch')
                continue

            logger.info(f'Uploaded {len(uploaded_songs)} songs, waiting for generation...')

            # Phase 2: Wait for all songs to complete (in parallel)
            wait_tasks = [
                self.wait_and_download_song(song)
                for song in uploaded_songs
            ]

            results = await asyncio.gather(*wait_tasks, return_exceptions=True)

            success_count = sum(1 for r in results if r is True)
            logger.info(f'Batch complete: {success_count}/{len(uploaded_songs)} successful')

            # Wait before next batch
            if i + batch_size < len(songs):
                logger.info('Waiting 10s before next batch...')
                await asyncio.sleep(10)

    async def process_task(self, task: dict):
        """Process a single Suno upload task."""
        task_id = task['id']
        song_id = task['song_id']

        logger.info(f'Processing task {task_id} for song {song_id}')

        # Get song details
        song = self.get_song(song_id)
        if not song:
            logger.error(f'Song not found: {song_id}')
            return

        # Upload to Suno
        title = await self.upload_single_song(song)
        if not title:
            return

        # Wait for generation and download
        await self.wait_and_download_song(song)

    async def run(self, batch_size: int = 3):
        """Main worker loop with batch processing.

        Args:
            batch_size: Number of songs to process concurrently (default 3)
        """
        logger.info('Starting Suno Worker (outside Docker)')
        logger.info(f'API: {API_BASE}')
        logger.info(f'Session file: {SESSION_FILE}')
        logger.info(f'Batch size: {batch_size} songs')

        if not self.login_api():
            logger.error('Failed to login to API. Exiting.')
            return

        while True:
            try:
                # Check for pending tasks (get multiple)
                tasks = self.get_pending_tasks(limit=batch_size)

                if tasks:
                    if len(tasks) > 1:
                        # Process multiple songs in parallel
                        logger.info(f'Found {len(tasks)} pending tasks, processing in batch')
                        await self.process_tasks_batch(tasks, batch_size=batch_size)
                    else:
                        # Single task - process normally
                        await self.process_task(tasks[0])
                else:
                    logger.debug('No pending tasks')

                # Wait before next poll
                await asyncio.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                logger.info('Shutting down...')
                break
            except Exception as e:
                logger.error(f'Worker error: {e}')
                await asyncio.sleep(POLL_INTERVAL)

        # Cleanup
        if self.browser:
            await self.browser.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Suno Worker - Upload songs to Suno AI')
    parser.add_argument('--batch-size', '-b', type=int, default=3,
                        help='Number of songs to upload concurrently (default: 3)')
    parser.add_argument('--interval', '-i', type=int, default=POLL_INTERVAL,
                        help=f'Seconds between task checks (default: {POLL_INTERVAL})')
    args = parser.parse_args()

    # Update poll interval if specified
    if args.interval != POLL_INTERVAL:
        POLL_INTERVAL = args.interval

    worker = SunoWorker()
    asyncio.run(worker.run(batch_size=args.batch_size))
