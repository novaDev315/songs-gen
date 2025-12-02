#!/usr/bin/env python3
"""Local file watcher that monitors generated/songs and creates songs via API."""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer

# Default configuration
DEFAULT_BACKEND_URL = "http://localhost:7000"
DEFAULT_WATCH_FOLDER = "generated/songs"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "pass123"


class SongFileHandler(FileSystemEventHandler):
    """Handler for new song files."""

    def __init__(self, backend_url: str, token: str, auto_upload: bool = True):
        super().__init__()
        self.backend_url = backend_url
        self.token = token
        self.auto_upload = auto_upload
        self.processed_files: set[str] = set()

    def _timestamp(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _log(self, msg: str) -> None:
        print(f"[{self._timestamp()}] {msg}")

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle new file creation."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process .md files
        if file_path.suffix != ".md":
            return

        # Skip if already processed
        if str(file_path) in self.processed_files:
            return

        self._log(f"New song file detected: {file_path.name}")

        # Wait for file to be fully written
        time.sleep(1)

        try:
            self.process_song_file(file_path)
            self.processed_files.add(str(file_path))
        except Exception as e:
            self._log(f"Error processing {file_path.name}: {e}")

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
        """Parse song file content to extract metadata."""
        lines = content.split("\n")
        metadata = {
            "title": "",
            "genre": "",
            "style_prompt": "",
            "lyrics": content,
        }

        # Extract title (first # heading)
        for line in lines:
            if line.startswith("# "):
                metadata["title"] = line[2:].strip()
                break

        # Extract style prompt and lyrics sections
        in_style = False
        style_lines = []
        in_lyrics = False
        lyrics_lines = []

        for line in lines:
            # Check for section headers
            if line.startswith("## Style Prompt"):
                in_style = True
                in_lyrics = False
                continue
            elif line.startswith("## Lyrics"):
                in_lyrics = True
                in_style = False
                continue
            elif line.startswith("##"):
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

        # Try to extract genre from style prompt or title
        style_lower = metadata["style_prompt"].lower()
        for genre in ["pop", "rock", "jazz", "hip-hop", "edm", "country", "rap", "electronic"]:
            if genre in style_lower:
                metadata["genre"] = genre.title()
                break

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
    """Scan and process existing .md files that haven't been processed."""
    print(f"Scanning existing files in {watch_folder}...")

    for md_file in watch_folder.rglob("*.md"):
        if str(md_file) not in handler.processed_files:
            # Check if song already exists in backend
            try:
                headers = {"Authorization": f"Bearer {handler.token}"}
                # Search by file path
                response = requests.get(
                    f"{handler.backend_url}/api/v1/songs",
                    params={"limit": 100},
                    headers=headers,
                    timeout=30,
                )
                if response.status_code == 200:
                    songs = response.json().get("items", [])
                    existing_paths = {s.get("file_path") for s in songs}

                    if str(md_file.absolute()) in existing_paths:
                        handler.processed_files.add(str(md_file))
                        continue

                    # Process new file
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing existing file: {md_file.name}")
                    handler.process_song_file(md_file)
                    handler.processed_files.add(str(md_file))
            except Exception as e:
                print(f"Error checking/processing {md_file.name}: {e}")


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

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping file watcher...")
        observer.stop()

    observer.join()
    print("File watcher stopped")


if __name__ == "__main__":
    main()
