#!/usr/bin/env python3
"""
Suno Local Upload Tool

Upload songs to Suno using a visible browser (bypasses Cloudflare).
Run this locally on your desktop, NOT in Docker.

Usage:
    python tools/suno_upload.py --style "pop, upbeat" --lyrics "[Verse]\nHello world"
    python tools/suno_upload.py --file generated/songs/pop/my-song.md

The script will:
1. Open a visible browser with your saved session
2. Navigate to Suno's create page
3. Fill in style and lyrics
4. Click Create
5. Wait for generation to start
6. Return the song URL
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright


# Session file path
SESSION_FILE = Path(__file__).parent.parent / "data" / "suno_session.json"


def parse_song_file(file_path: str) -> tuple[str, str, str]:
    """Parse a song markdown file to extract title, style, and lyrics."""
    content = Path(file_path).read_text()

    # Extract title from # heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Untitled"

    # Extract style prompt
    style_match = re.search(r'## Style Prompt\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    style = style_match.group(1).strip() if style_match else ""

    # Extract lyrics
    lyrics_match = re.search(r'## Lyrics\s*\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
    lyrics = lyrics_match.group(1).strip() if lyrics_match else ""

    return title, style, lyrics


async def upload_to_suno(style_prompt: str, lyrics: str, title: str = None) -> dict:
    """Upload a song to Suno using visible browser."""

    if not SESSION_FILE.exists():
        print(f"ERROR: No session file found at {SESSION_FILE}")
        print("Run 'python tools/suno_auth_setup.py' first to authenticate.")
        sys.exit(1)

    print("=" * 60)
    print("SUNO UPLOAD")
    print("=" * 60)
    print(f"Title: {title or 'Auto-generated'}")
    print(f"Style: {style_prompt[:50]}...")
    print(f"Lyrics: {len(lyrics)} characters")
    print()

    async with async_playwright() as p:
        # Launch VISIBLE browser (not headless) to bypass Cloudflare
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        # Load saved session
        context = await browser.new_context(
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

        # Hide webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        page = await context.new_page()

        print("Opening Suno...")
        await page.goto("https://suno.com/create", wait_until="domcontentloaded")

        # Wait for Cloudflare check (if any)
        print("Waiting for page to load...")
        await asyncio.sleep(5)

        # Check if we hit Cloudflare
        if "just a moment" in (await page.title()).lower():
            print("Cloudflare check detected, waiting...")
            await asyncio.sleep(10)

        # Wait for Create page to load
        try:
            await page.wait_for_selector('text=Lyrics', timeout=30000)
            print("Create page loaded!")
        except:
            print("ERROR: Could not load create page. Session may have expired.")
            print("Run 'python tools/suno_auth_setup.py' to re-authenticate.")
            await browser.close()
            sys.exit(1)

        # Click Custom tab if visible
        try:
            custom_tab = page.locator('button:has-text("Custom")')
            if await custom_tab.is_visible(timeout=2000):
                await custom_tab.click()
                await asyncio.sleep(0.5)
                print("Clicked Custom tab")
        except:
            pass

        # Fill Lyrics
        print("Filling lyrics...")
        try:
            # Click on Lyrics section to expand
            lyrics_section = page.locator('text=Lyrics').first
            await lyrics_section.click()
            await asyncio.sleep(0.3)

            # Find and fill textarea
            textarea = page.locator('textarea').first
            await textarea.click()
            await textarea.fill(lyrics)
            print(f"  Filled {len(lyrics)} characters")
        except Exception as e:
            print(f"  Warning: Could not fill lyrics: {e}")

        # Fill Styles
        print("Filling style...")
        try:
            # Click on Styles section to expand
            styles_section = page.locator('text=Styles').first
            await styles_section.click()
            await asyncio.sleep(0.3)

            # The style input might be a text field or chips
            # Try to find an input/textarea in the Styles section
            style_input = page.locator('input[type="text"]').first
            if await style_input.is_visible(timeout=2000):
                await style_input.click()
                await style_input.fill(style_prompt)
                print(f"  Filled style: {style_prompt[:30]}...")
            else:
                # Try typing directly
                await page.keyboard.type(style_prompt)
                print(f"  Typed style: {style_prompt[:30]}...")
        except Exception as e:
            print(f"  Warning: Could not fill style: {e}")

        await asyncio.sleep(1)

        # Take screenshot before clicking Create
        screenshot_path = "/tmp/suno_before_create.png"
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Ask user to confirm
        print()
        print("-" * 60)
        print("Ready to create song!")
        print("Check the browser window to verify fields are filled correctly.")
        print()
        confirm = input("Press ENTER to create, or 'q' to quit: ")

        if confirm.lower() == 'q':
            print("Cancelled.")
            await browser.close()
            return {"status": "cancelled"}

        # Click Create button
        print("Clicking Create...")
        try:
            create_btn = page.locator('button:has-text("Create")').last
            await create_btn.click()
            print("Create button clicked!")
        except Exception as e:
            print(f"ERROR: Could not click Create: {e}")
            await browser.close()
            sys.exit(1)

        # Wait for generation to start
        print("Waiting for generation to start...")
        await asyncio.sleep(5)

        # Get current URL (might have song ID)
        current_url = page.url
        print(f"Current URL: {current_url}")

        # Take final screenshot
        final_screenshot = "/tmp/suno_after_create.png"
        await page.screenshot(path=final_screenshot)
        print(f"Final screenshot: {final_screenshot}")

        print()
        print("=" * 60)
        print("UPLOAD COMPLETE!")
        print("=" * 60)
        print("Check the Suno website for your generated songs.")
        print()

        # Keep browser open for user to see results
        input("Press ENTER to close browser...")

        await browser.close()

        return {
            "status": "success",
            "url": current_url,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Upload songs to Suno (local browser)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--file", "-f",
        help="Path to song markdown file (with ## Style Prompt and ## Lyrics sections)"
    )
    parser.add_argument(
        "--style", "-s",
        help="Style prompt (e.g., 'pop, upbeat, female vocals')"
    )
    parser.add_argument(
        "--lyrics", "-l",
        help="Song lyrics (use \\n for newlines)"
    )
    parser.add_argument(
        "--title", "-t",
        help="Song title (optional)"
    )

    args = parser.parse_args()

    # Get style and lyrics from file or arguments
    if args.file:
        title, style, lyrics = parse_song_file(args.file)
        if args.title:
            title = args.title
        if args.style:
            style = args.style
        if args.lyrics:
            lyrics = args.lyrics.replace("\\n", "\n")
    elif args.style and args.lyrics:
        title = args.title or "Untitled"
        style = args.style
        lyrics = args.lyrics.replace("\\n", "\n")
    else:
        parser.error("Either --file or both --style and --lyrics are required")

    if not style or not lyrics:
        parser.error("Style prompt and lyrics are required")

    # Run upload
    result = asyncio.run(upload_to_suno(style, lyrics, title))

    if result.get("status") == "success":
        print("Done!")
    else:
        print(f"Status: {result.get('status')}")


if __name__ == "__main__":
    main()
