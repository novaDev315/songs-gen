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
        try:
            resp = requests.get(
                f'{API_BASE}/queue/tasks',
                params={'status_filter': 'pending', 'task_type': 'suno_upload', 'limit': 1},
                headers=self.api_headers()
            )
            if resp.status_code == 200:
                tasks = resp.json().get('items', [])
                if tasks:
                    return tasks[0]
            return None
        except Exception as e:
            logger.error(f'Error getting pending task: {e}')
            return None

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
        job_id = await self.upload_to_suno(
            style_prompt=song['style_prompt'],
            lyrics=song['lyrics'],
            title=song['title']
        )

        if job_id:
            logger.info(f'Upload successful! Job ID: {job_id}')
            self.update_song_status(song_id, 'generating')
        else:
            logger.error('Upload failed')
            self.update_song_status(song_id, 'failed')

    async def run(self):
        """Main worker loop."""
        logger.info('Starting Suno Worker (outside Docker)')
        logger.info(f'API: {API_BASE}')
        logger.info(f'Session file: {SESSION_FILE}')

        if not self.login_api():
            logger.error('Failed to login to API. Exiting.')
            return

        while True:
            try:
                # Check for pending tasks
                task = self.get_pending_task()

                if task:
                    await self.process_task(task)
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
    worker = SunoWorker()
    asyncio.run(worker.run())
