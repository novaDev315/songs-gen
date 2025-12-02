#!/usr/bin/env python3
"""Local file watcher that monitors generated/songs and creates songs via API."""

import argparse
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from queue import Queue, Empty

import requests
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:7000"
DEFAULT_WATCH_FOLDER = "generated/songs"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "pass123"


class SongFileHandler(FileSystemEventHandler):
    """Handler for new song files with queue-based batch processing."""

    def __init__(self, backend_url: str, token: str, auto_upload: bool = True, data_dir: Path = None):
        super().__init__()
        self.backend_url = backend_url
        self.token = token
        self.auto_upload = auto_upload
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.processed_file = self.data_dir / "processed_songs.json"
        self.processed_files: set[str] = self._load_processed_files()

        # Queue for batch processing
        self.file_queue: Queue[Path] = Queue()
        self.worker_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _load_processed_files(self) -> set[str]:
        """Load processed files from persistent storage."""
        if self.processed_file.exists():
            try:
                with open(self.processed_file, "r") as f:
                    return set(json.load(f))
            except Exception:
                pass
        return set()

    def _save_processed_files(self) -> None:
        """Save processed files to persistent storage."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.processed_file, "w") as f:
            json.dump(list(self.processed_files), f, indent=2)

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, msg: str) -> None:
        print(f"[{self._timestamp()}] {msg}")

    def _check_song_exists(self, file_path: Path) -> bool:
        """Check if song already exists in backend by file path."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.backend_url}/api/v1/songs",
                params={"file_path": str(file_path.absolute()), "limit": 1},
                headers=headers,
                timeout=10,
            )
            if response.status_code == 200:
                items = response.json().get("items", [])
                return len(items) > 0
        except Exception as e:
            self._log(f"Error checking if song exists: {e}")
        return False

    def _process_queue(self) -> None:
        """Worker thread that processes files from the queue."""
        batch_save_count = 0

        while self.worker_running:
            try:
                # Wait for file with timeout (allows clean shutdown)
                file_path = self.file_queue.get(timeout=1)
            except Empty:
                # Save periodically even if no new files
                if batch_save_count > 0:
                    self._save_processed_files()
                    batch_save_count = 0
                continue

            try:
                abs_path = str(file_path.absolute())

                # Skip if already processed
                if abs_path in self.processed_files:
                    self.file_queue.task_done()
                    continue

                # Check backend
                if self._check_song_exists(file_path):
                    self._log(f"Already in backend: {file_path.name}")
                    self.processed_files.add(abs_path)
                    batch_save_count += 1
                    self.file_queue.task_done()
                    continue

                # Wait for file to be fully written
                time.sleep(0.5)

                # Process the file
                self._log(f"Processing: {file_path.name}")
                self.process_song_file(file_path)
                self.processed_files.add(abs_path)
                batch_save_count += 1

                # Batch save every 5 files
                if batch_save_count >= 5:
                    self._save_processed_files()
                    batch_save_count = 0

                self.file_queue.task_done()

            except Exception as e:
                self._log(f"Error processing {file_path.name}: {e}")
                self.file_queue.task_done()

        # Final save on shutdown
        if batch_save_count > 0:
            self._save_processed_files()

    def stop(self) -> None:
        """Stop the worker thread."""
        self.worker_running = False
        self.worker_thread.join(timeout=5)

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle new file creation - adds to queue for processing."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .md files
        if file_path.suffix != ".md":
            return

        # Quick check - skip if already processed locally
        if str(file_path.absolute()) in self.processed_files:
            return

        self._log(f"Queued: {file_path.name} (queue size: {self.file_queue.qsize() + 1})")
        self.file_queue.put(file_path)

    def process_song_file(self, file_path: Path) -> None:
        """Process new song file and create via API."""
        # Read song file content
        content = file_path.read_text(encoding="utf-8")

        # Extract metadata from file content
        metadata = self.parse_song_file(content)

        # Check for accompanying .meta.json file
        meta_file = file_path.with_suffix(".meta.json")
        if meta_file.exists():
            with open(meta_file, "r") as f:
                extra_meta = json.load(f)
                metadata.update(extra_meta)

        # Create song via API
        song_data = {
            "title": metadata.get("title", file_path.stem),
            "genre": metadata.get("genre", "Unknown"),
            "style_prompt": metadata.get("style_prompt", ""),
            "lyrics": metadata.get("lyrics", content),
            "file_path": str(file_path.absolute()),
        }

        headers = {"Authorization": f"Bearer {self.token}"}

        # Create song
        response = requests.post(
            f"{self.backend_url}/api/v1/songs",
            json=song_data,
            headers=headers,
            timeout=30,
        )

        if response.status_code == 200:
            song = response.json()
            self._log(f"Song created: {song['title']} (ID: {song['id']})")

            # Queue for Suno upload if auto_upload enabled
            if self.auto_upload:
                upload_resp = requests.post(
                    f"{self.backend_url}/api/v1/songs/{song['id']}/upload-to-suno",
                    headers=headers,
                    timeout=30,
                )
                if upload_resp.status_code == 200:
                    self._log(f"Queued for Suno upload: {song['title']}")
                else:
                    self._log(f"Failed to queue for Suno: {upload_resp.text}")
        else:
            self._log(f"Failed to create song: {response.text}")

    def parse_song_file(self, content: str) -> dict:
        """Parse song file content to extract metadata.

        Handles both plain text and code block formats:
        - ## Style Prompt followed by text or ```code block```
        - ## Lyrics followed by text or ```code block```
        """
        lines = content.split("\n")
        metadata = {
            "title": "",
            "genre": "",
            "style_prompt": "",
            "lyrics": content,
        }

        # Extract title (first # heading)
        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                metadata["title"] = line[2:].strip()
                break

        # Extract style prompt and lyrics sections
        in_style = False
        in_lyrics = False
        in_code_block = False
        style_lines = []
        lyrics_lines = []

        for line in lines:
            # Check for code block markers
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Check for section headers (only outside code blocks)
            if not in_code_block:
                # Handle various style prompt header formats
                if line.startswith("## Style Prompt") or line.startswith("## AI Style Prompt"):
                    in_style = True
                    in_lyrics = False
                    continue
                elif line.startswith("## Lyrics"):
                    in_lyrics = True
                    in_style = False
                    continue
                elif line.startswith("## "):
                    in_style = False
                    in_lyrics = False
                    continue

            # Collect content from active sections
            if in_style and line.strip():
                style_lines.append(line.strip())
            elif in_lyrics:
                lyrics_lines.append(line)

        # Join collected lines
        if style_lines:
            metadata["style_prompt"] = " ".join(style_lines)

        if lyrics_lines:
            # Preserve line breaks in lyrics
            metadata["lyrics"] = "\n".join(lyrics_lines).strip()

        # Try to extract genre from style prompt (avoid "no <genre>" patterns)
        import re
        style_lower = metadata["style_prompt"].lower()

        # Order by specificity (more specific genres first)
        genres = [
            "hip-hop", "r&b", "r-b", "edm", "electronic",
            "country", "rock", "jazz", "pop", "rap", "folk", "blues"
        ]

        for genre in genres:
            # Use word boundary to match genre, but not "no genre"
            pattern = rf"(?<!no\s)(?<!no-)\b{re.escape(genre)}\b"
            if re.search(pattern, style_lower):
                # Normalize genre name
                genre_name = genre.replace("-", " ").replace("&", " and ")
                metadata["genre"] = genre_name.title().replace(" And ", " & ")
                break

        # Fallback: try to get from folder path if available
        if not metadata["genre"]:
            metadata["genre"] = "Unknown"

        return metadata


def login(backend_url: str, username: str, password: str) -> str | None:
    """Login to backend and get access token."""
    try:
        response = requests.post(
            f"{backend_url}/api/v1/auth/login",
            json={"username": username, "password": password},
            timeout=30,
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None


def scan_existing_files(watch_folder: Path, handler: SongFileHandler) -> None:
    """Scan and queue existing .md files that haven't been processed."""
    print(f"Scanning existing files in {watch_folder}...")
    queued_count = 0
    skipped_count = 0

    for md_file in watch_folder.rglob("*.md"):
        abs_path = str(md_file.absolute())

        # Skip if already in local processed list
        if abs_path in handler.processed_files:
            skipped_count += 1
            continue

        # Queue for processing (worker thread will check backend)
        handler.file_queue.put(md_file)
        queued_count += 1

    print(f"Scan complete: {queued_count} queued, {skipped_count} already processed")

    if queued_count > 0:
        print(f"Processing {queued_count} files in background...")


def main():
    parser = argparse.ArgumentParser(description="File watcher for song files")
    parser.add_argument(
        "--backend",
        default=os.environ.get("BACKEND_URL", DEFAULT_BACKEND_URL),
        help="Backend API URL",
    )
    parser.add_argument(
        "--watch-folder",
        default=os.environ.get("WATCH_FOLDER", DEFAULT_WATCH_FOLDER),
        help="Folder to watch for new songs",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("ADMIN_USERNAME", DEFAULT_USERNAME),
        help="Admin username",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("ADMIN_PASSWORD", DEFAULT_PASSWORD),
        help="Admin password",
    )
    parser.add_argument(
        "--no-auto-upload",
        action="store_true",
        help="Don't automatically queue songs for Suno upload",
    )
    parser.add_argument(
        "--scan-existing",
        action="store_true",
        help="Scan and process existing files on startup",
    )

    args = parser.parse_args()

    # Resolve watch folder path
    watch_folder = Path(args.watch_folder)
    if not watch_folder.is_absolute():
        # Relative to script location's parent (project root)
        script_dir = Path(__file__).parent.parent
        watch_folder = script_dir / args.watch_folder

    if not watch_folder.exists():
        print(f"Error: Watch folder does not exist: {watch_folder}")
        sys.exit(1)

    print("=" * 60)
    print("FILE WATCHER")
    print("=" * 60)
    print(f"Backend: {args.backend}")
    print(f"Watch folder: {watch_folder}")
    print(f"Auto-upload to Suno: {not args.no_auto_upload}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    # Login to backend
    token = login(args.backend, args.username, args.password)
    if not token:
        print("Failed to authenticate with backend")
        sys.exit(1)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Logged in to backend")

    # Create handler
    handler = SongFileHandler(
        backend_url=args.backend,
        token=token,
        auto_upload=not args.no_auto_upload,
    )

    # Scan existing files if requested
    if args.scan_existing:
        scan_existing_files(watch_folder, handler)

    # Start observer
    observer = Observer()
    observer.schedule(handler, str(watch_folder), recursive=True)
    observer.start()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Watching for new files...")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Previously processed: {len(handler.processed_files)} files")

    try:
        while True:
            # Show queue status periodically
            queue_size = handler.file_queue.qsize()
            if queue_size > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Queue: {queue_size} files pending")
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopping file watcher...")

    # Stop handler (waits for queue to drain)
    print("Waiting for queue to finish...")
    handler.file_queue.join()  # Wait for all queued items
    handler.stop()

    observer.stop()
    observer.join()
    print("File watcher stopped")


if __name__ == "__main__":
    main()
