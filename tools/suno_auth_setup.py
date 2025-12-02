#!/usr/bin/env python3
"""
Suno Authentication Setup Tool

One-time setup script to authenticate with Suno.com and save the session.
Run this manually, sign in with your Google account, and the session will
be saved for the automation pipeline to use.

Usage:
    python tools/suno_auth_setup.py

The script will:
1. Open a browser window (visible, not headless)
2. Navigate to Suno.com
3. Wait for you to sign in manually (via Google)
4. Save the session to data/suno_session.json
5. Close the browser

After this, the automation can use the saved session without manual login.
Session typically lasts days/weeks before needing to re-authenticate.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright


async def setup_suno_auth():
    """Run interactive Suno authentication setup."""

    # Default session file path
    session_file = Path(__file__).parent.parent / "data" / "suno_session.json"

    # Create data directory if it doesn't exist
    session_file.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SUNO AUTHENTICATION SETUP")
    print("=" * 60)
    print()
    print("This tool will open a browser for you to sign in to Suno.com")
    print("with your Google account.")
    print()
    print(f"Session will be saved to: {session_file}")
    print()
    print("Instructions:")
    print("  1. A browser window will open")
    print("  2. Click 'Sign In' on Suno.com")
    print("  3. Choose 'Continue with Google'")
    print("  4. Complete the Google sign-in process")
    print("  5. Once you see the Suno dashboard, press ENTER here")
    print()
    input("Press ENTER to start the browser...")

    async with async_playwright() as p:
        # Launch browser in visible mode (not headless)
        browser = await p.chromium.launch(
            headless=False,  # Show the browser window
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        # Create context with realistic settings
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/Los_Angeles",
        )

        # Hide webdriver property
        await context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            """
        )

        page = await context.new_page()

        print()
        print("Browser opened. Navigating to Suno.com...")

        # Navigate to Suno
        await page.goto("https://suno.com", wait_until="domcontentloaded")

        print()
        print("-" * 60)
        print("SIGN IN NOW")
        print("-" * 60)
        print()
        print("1. Click 'Sign In' in the top right")
        print("2. Choose 'Continue with Google'")
        print("3. Complete Google sign-in")
        print("4. Wait until you see the Suno dashboard")
        print()
        print("When you're fully signed in and see the dashboard,")
        input("press ENTER here to save the session...")

        # Save the session state
        await context.storage_state(path=str(session_file))

        print()
        print("=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print()
        print(f"Session saved to: {session_file}")
        print()
        print("The automation pipeline will now use this session.")
        print("You'll need to re-run this script if the session expires")
        print("(typically every few days/weeks).")
        print()

        # Close browser
        await browser.close()

        return str(session_file)


async def verify_session():
    """Verify that a saved session is still valid."""

    session_file = Path(__file__).parent.parent / "data" / "suno_session.json"

    if not session_file.exists():
        print(f"No session file found at: {session_file}")
        print("Run 'python tools/suno_auth_setup.py' to create one.")
        return False

    print(f"Verifying session from: {session_file}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # Load saved session
        context = await browser.new_context(
            storage_state=str(session_file),
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        page = await context.new_page()

        # Navigate to Suno
        await page.goto("https://suno.com", wait_until="domcontentloaded")
        await asyncio.sleep(3)  # Wait for page to load

        # Check if we're logged in by looking for user-specific elements
        # or absence of login button
        try:
            # Look for signs we're logged in
            logged_in_indicators = [
                'button:has-text("Create")',
                '[data-testid="user-menu"]',
                '[aria-label="User menu"]',
                '.user-avatar',
            ]

            for selector in logged_in_indicators:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=2000):
                        print("Session is VALID - still logged in!")
                        await browser.close()
                        return True
                except:
                    continue

            # Check if login button is visible (means we're NOT logged in)
            login_button = page.locator('button:has-text("Sign In"), a:has-text("Sign In")').first
            if await login_button.is_visible(timeout=2000):
                print("Session is EXPIRED - login button visible")
                print("Please re-run authentication setup.")
                await browser.close()
                return False

            # If we can't determine, assume it might be valid
            print("Session status unclear - please verify manually")
            await browser.close()
            return True

        except Exception as e:
            print(f"Error verifying session: {e}")
            await browser.close()
            return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Suno Authentication Setup Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing session is still valid"
    )

    args = parser.parse_args()

    if args.verify:
        result = asyncio.run(verify_session())
        sys.exit(0 if result else 1)
    else:
        asyncio.run(setup_suno_auth())


if __name__ == "__main__":
    main()
