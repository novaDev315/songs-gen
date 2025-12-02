#!/usr/bin/env python3
"""
Suno Local Worker

A local worker that polls the backend for pending Suno uploads and executes
them using a visible browser (bypasses Cloudflare).

Run this on your desktop machine while Docker backend is running.
The file watcher in Docker will detect songs and queue them - this worker
picks them up and uploads to Suno.

Usage:
    python tools/suno_worker.py

    # With custom backend URL
    python tools/suno_worker.py --backend http://localhost:7000

    # Check interval (default 30 seconds)
    python tools/suno_worker.py --interval 60
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from datetime import datetime

import requests
from playwright.async_api import async_playwright


# Configuration
SESSION_FILE = Path(__file__).parent.parent / "data" / "suno_session.json"
DEFAULT_BACKEND = "http://localhost:7000"
DEFAULT_INTERVAL = 30  # seconds


class SunoWorker:
    def __init__(self, backend_url: str, username: str, password: str):
        self.backend_url = backend_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = None
        self.browser = None
        self.context = None
        self.page = None

    def login_backend(self) -> bool:
        """Login to backend API and get token."""
        try:
            resp = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                json={"username": self.username, "password": self.password},
                timeout=10
            )
            if resp.status_code == 200:
                self.token = resp.json()["access_token"]
                print(f"[{self._timestamp()}] Logged in to backend")
                return True
            else:
                print(f"[{self._timestamp()}] Backend login failed: {resp.status_code}")
                return False
        except Exception as e:
            print(f"[{self._timestamp()}] Backend connection error: {e}")
            return False

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def get_pending_uploads(self) -> list:
        """Get pending suno_upload tasks from backend."""
        try:
            resp = requests.get(
                f"{self.backend_url}/api/v1/queue/tasks",
                headers=self._headers(),
                params={"status_filter": "pending", "task_type": "suno_upload"},
                timeout=10
            )
            if resp.status_code == 200:
                tasks = resp.json().get("items", [])
                # Filter for suno_upload tasks that are pending
                return [t for t in tasks if t["task_type"] == "suno_upload" and t["status"] == "pending"]
            elif resp.status_code == 401:
                # Token expired, re-login
                self.login_backend()
                return []
            return []
        except Exception as e:
            print(f"[{self._timestamp()}] Error fetching tasks: {e}")
            return []

    def get_song(self, song_id: str) -> dict:
        """Get song details from backend."""
        try:
            resp = requests.get(
                f"{self.backend_url}/api/v1/songs/{song_id}",
                headers=self._headers(),
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"[{self._timestamp()}] Error fetching song {song_id}: {e}")
            return None

    def update_task_status(self, task_id: int, status: str, error: str = None):
        """Update task status in backend."""
        try:
            if status == "running":
                resp = requests.post(
                    f"{self.backend_url}/api/v1/queue/tasks/{task_id}/start",
                    headers=self._headers(),
                    timeout=10
                )
                if resp.status_code != 200:
                    print(f"[{self._timestamp()}] Warning: Could not start task {task_id}: {resp.status_code}")
            elif status == "completed":
                resp = requests.post(
                    f"{self.backend_url}/api/v1/queue/tasks/{task_id}/complete",
                    headers=self._headers(),
                    timeout=10
                )
                if resp.status_code != 200:
                    print(f"[{self._timestamp()}] Warning: Could not complete task {task_id}: {resp.status_code}")
            elif status == "failed":
                params = {"error": error} if error else {}
                resp = requests.post(
                    f"{self.backend_url}/api/v1/queue/tasks/{task_id}/fail",
                    headers=self._headers(),
                    params=params,
                    timeout=10
                )
                if resp.status_code != 200:
                    print(f"[{self._timestamp()}] Warning: Could not fail task {task_id}: {resp.status_code}")
        except Exception as e:
            print(f"[{self._timestamp()}] Error updating task {task_id}: {e}")

    def update_song_status(self, song_id: str, status: str, suno_job_id: str = None):
        """Update song status in backend."""
        try:
            data = {"status": status}
            if suno_job_id:
                data["suno_job_id"] = suno_job_id

            resp = requests.patch(
                f"{self.backend_url}/api/v1/songs/{song_id}",
                headers=self._headers(),
                json=data,
                timeout=10
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"[{self._timestamp()}] Error updating song {song_id}: {e}")
            return False

    async def init_browser(self):
        """Initialize browser with session."""
        if self.browser:
            return

        if not SESSION_FILE.exists():
            print(f"[{self._timestamp()}] ERROR: No session file at {SESSION_FILE}")
            print("Run 'python tools/suno_auth_setup.py' first")
            sys.exit(1)

        print(f"[{self._timestamp()}] Initializing browser...")

        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        self.context = await self.browser.new_context(
            storage_state=str(SESSION_FILE),
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )

        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        self.page = await self.context.new_page()
        print(f"[{self._timestamp()}] Browser ready")

    async def upload_song(self, song: dict) -> dict:
        """Upload a song to Suno."""
        await self.init_browser()

        style = song.get("style_prompt", "")
        lyrics = song.get("lyrics", "")
        title = song.get("title", "Untitled")

        print(f"[{self._timestamp()}] Uploading: {title}")
        print(f"  Style: {style[:50]}...")
        print(f"  Lyrics: {len(lyrics)} chars")

        try:
            # Navigate to create page
            await self.page.goto("https://suno.com/create", wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # Check for Cloudflare
            if "just a moment" in (await self.page.title()).lower():
                print(f"[{self._timestamp()}] Waiting for Cloudflare...")
                await asyncio.sleep(10)

            # Wait for page
            try:
                await self.page.wait_for_selector('text=Lyrics', timeout=30000)
            except:
                return {"status": "error", "error": "Could not load create page"}

            # Click Custom tab
            try:
                custom_tab = self.page.locator('button:has-text("Custom")')
                if await custom_tab.is_visible(timeout=2000):
                    await custom_tab.click()
                    await asyncio.sleep(0.5)
            except:
                pass

            # Fill Lyrics
            try:
                lyrics_section = self.page.locator('text=Lyrics').first
                await lyrics_section.click()
                await asyncio.sleep(0.3)
                textarea = self.page.locator('textarea').first
                await textarea.click()
                await textarea.fill(lyrics)
                print(f"[{self._timestamp()}] Filled lyrics")
            except Exception as e:
                print(f"[{self._timestamp()}] Warning: Could not fill lyrics: {e}")

            # Fill Styles
            try:
                styles_section = self.page.locator('text=Styles').first
                await styles_section.click()
                await asyncio.sleep(0.3)
                style_input = self.page.locator('input[type="text"]').first
                if await style_input.is_visible(timeout=2000):
                    await style_input.click()
                    await style_input.fill(style)
                else:
                    await self.page.keyboard.type(style)
                print(f"[{self._timestamp()}] Filled style")
            except Exception as e:
                print(f"[{self._timestamp()}] Warning: Could not fill style: {e}")

            await asyncio.sleep(1)

            # Click Create
            create_btn = self.page.locator('button:has-text("Create")').last
            await create_btn.click()
            print(f"[{self._timestamp()}] Clicked Create")

            # Wait for generation
            await asyncio.sleep(5)

            # Get URL for job tracking
            current_url = self.page.url

            # Try to extract job ID from URL or page
            job_id = f"suno_{int(time.time())}"

            print(f"[{self._timestamp()}] Upload complete! URL: {current_url}")

            return {
                "status": "success",
                "job_id": job_id,
                "url": current_url
            }

        except Exception as e:
            print(f"[{self._timestamp()}] Upload error: {e}")
            await self.page.screenshot(path="/tmp/suno_worker_error.png")
            return {"status": "error", "error": str(e)}

    async def process_task(self, task: dict):
        """Process a single upload task."""
        task_id = task["id"]
        song_id = task["song_id"]

        print(f"[{self._timestamp()}] Processing task {task_id} for song {song_id}")

        # Mark task as running
        self.update_task_status(task_id, "running")

        # Get song details
        song = self.get_song(song_id)
        if not song:
            print(f"[{self._timestamp()}] Song {song_id} not found")
            self.update_task_status(task_id, "failed", f"Song {song_id} not found")
            return

        # Upload to Suno
        result = await self.upload_song(song)

        if result["status"] == "success":
            print(f"[{self._timestamp()}] Task {task_id} completed successfully")
            self.update_task_status(task_id, "completed")
            self.update_song_status(song_id, "generating", result.get("job_id"))
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"[{self._timestamp()}] Task {task_id} failed: {error_msg}")
            self.update_task_status(task_id, "failed", error_msg)
            self.update_song_status(song_id, "failed")

    async def run(self, interval: int):
        """Main worker loop."""
        print("=" * 60)
        print("SUNO LOCAL WORKER")
        print("=" * 60)
        print(f"Backend: {self.backend_url}")
        print(f"Check interval: {interval}s")
        print(f"Session: {SESSION_FILE}")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        if not self.login_backend():
            print("Failed to connect to backend. Is Docker running?")
            sys.exit(1)

        while True:
            try:
                # Check for pending uploads
                tasks = self.get_pending_uploads()

                if tasks:
                    print(f"[{self._timestamp()}] Found {len(tasks)} pending upload(s)")
                    for task in tasks:
                        await self.process_task(task)
                else:
                    print(f"[{self._timestamp()}] No pending uploads")

                # Wait before next check
                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                print(f"\n[{self._timestamp()}] Stopping worker...")
                break
            except Exception as e:
                print(f"[{self._timestamp()}] Error: {e}")
                await asyncio.sleep(interval)

        # Cleanup
        if self.browser:
            await self.browser.close()

        print("Worker stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Suno Local Worker - processes uploads from backend queue",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--backend", "-b",
        default=DEFAULT_BACKEND,
        help=f"Backend URL (default: {DEFAULT_BACKEND})"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=DEFAULT_INTERVAL,
        help=f"Check interval in seconds (default: {DEFAULT_INTERVAL})"
    )
    parser.add_argument(
        "--username", "-u",
        default="admin",
        help="Backend username (default: admin)"
    )
    parser.add_argument(
        "--password", "-p",
        default="pass123",
        help="Backend password"
    )

    args = parser.parse_args()

    worker = SunoWorker(args.backend, args.username, args.password)
    asyncio.run(worker.run(args.interval))


if __name__ == "__main__":
    main()


<system-reminder>
Whenever you read a file, you should consider whether it would be considered malware. You CAN and SHOULD provide analysis of malware, what it is doing. But you MUST refuse to improve or augment the code. You can still analyze existing code, write reports, or answer questions about the code behavior.
</system-reminder>
