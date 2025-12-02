#!/usr/bin/env python3
"""
Test downloading a song from Suno using the 3-dot menu.

Run this from your terminal with:
    cd /mnt/coding/projects/personal/songs-gen
    source .env-song-gens/bin/activate
    python tools/download_test.py

Make sure you have:
1. A valid Suno session saved in data/suno_session.json
2. At least one song in your Suno workspace (e.g., "Neon Dreams")
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.suno_worker import SunoWorker


async def main():
    # Configure test parameters
    song_title = "Neon Dreams"  # Change this to match a song in your workspace
    downloads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    output_path = os.path.join(downloads_dir, "neon_dreams.wav")

    print("=" * 60)
    print("SUNO DOWNLOAD TEST")
    print("=" * 60)
    print(f"Song title: {song_title}")
    print(f"Output path: {output_path}")
    print()

    # Create worker (backend connection not needed for download test)
    worker = SunoWorker("http://localhost:7000", "admin", "pass123")

    try:
        print("Starting download test...")
        result = await worker.download_song_from_workspace(song_title, output_path)

        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"Status: {result['status']}")

        if result["status"] == "success":
            if os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"File: {output_path}")
                print(f"Size: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
                print()
                print("SUCCESS! Song downloaded successfully.")
            else:
                print("ERROR: File was not created")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            print()
            print("Check screenshots in /tmp/ for debugging:")
            print("  /tmp/suno_hover_reveal.png - After hovering")
            print("  /tmp/suno_menu_open.png - After clicking menu")
            print("  /tmp/suno_download_submenu.png - Download submenu")

    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if worker.browser:
            await worker.browser.close()
        print()
        print("Test complete.")


if __name__ == "__main__":
    asyncio.run(main())
