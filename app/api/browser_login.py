"""
Browser-based login for Feishu/Lark.
Opens a browser window for the user to login and captures the session cookie.
"""
import os
import json
import asyncio
from loguru import logger

# Cookie storage path
from app.config.settings import settings
COOKIE_FILE = os.path.join(settings.DATA_DIR, "cookie.json")
LOGIN_URL = "https://www.feishu.cn/messenger/"
# Required cookie that indicates successful login
AUTH_COOKIE_NAME = "session"


def ensure_cookie_dir():
    """Ensure the cookie storage directory exists"""
    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)


def save_cookie_to_file(cookie_str: str):
    """Save cookie string to local file"""
    ensure_cookie_dir()
    with open(COOKIE_FILE, 'w') as f:
        json.dump({"cookie": cookie_str}, f)
    logger.info(f"Cookie saved to {COOKIE_FILE}")


def load_cookie_from_file() -> str:
    """Load cookie string from local file"""
    if not os.path.exists(COOKIE_FILE):
        return ""
    try:
        with open(COOKIE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("cookie", "")
    except Exception as e:
        logger.warning(f"Failed to load cookie from file: {e}")
        return ""


def clear_saved_cookie():
    """Remove saved cookie file"""
    if os.path.exists(COOKIE_FILE):
        os.remove(COOKIE_FILE)
        logger.info("Saved cookie cleared")


async def _launch_browser(p):
    """Launch the user's default system browser."""
    import subprocess

    # Detect default browser from system settings
    try:
        result = subprocess.run(
            ["xdg-mime", "query", "default", "x-scheme-handler/https"],
            capture_output=True, text=True
        )
        default_desktop = result.stdout.strip().lower()
    except Exception:
        default_desktop = ""

    # Map desktop file to Playwright browser type
    if "firefox" in default_desktop:
        browser = await p.firefox.launch(headless=False)
    elif "chromium" in default_desktop:
        browser = await p.chromium.launch(headless=False)
    elif "chrome" in default_desktop:
        browser = await p.chromium.launch(headless=False, channel="chrome")
    elif "edge" in default_desktop:
        browser = await p.chromium.launch(headless=False, channel="msedge")
    else:
        # Fallback to chromium
        browser = await p.chromium.launch(headless=False)
        default_desktop = "chromium (fallback)"

    logger.info(f"Using browser: {default_desktop}")
    return browser


async def browser_login(timeout: int = 180) -> str:
    """
    Open a browser for Feishu login and capture cookies.

    Args:
        timeout: Maximum wait time in seconds (default: 3 minutes)

    Returns:
        Cookie string for API authentication

    Raises:
        TimeoutError: If login is not completed within timeout
        ImportError: If playwright is not installed
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "playwright is required for browser login. "
            "Install with: pip install playwright && playwright install chromium"
        )

    logger.info("Starting browser login...")
    logger.info(f"Opening {LOGIN_URL}")
    logger.info(f"Please login within {timeout} seconds...")

    async with async_playwright() as p:
        browser = await _launch_browser(p)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(LOGIN_URL)

        # Poll for login completion by checking cookies
        import time
        start_time = time.time()
        cookie_str = ""

        while time.time() - start_time < timeout:
            cookies = await context.cookies()

            all_cookie_names = {c['name'] for c in cookies}
            current_url = page.url
            has_session = 'session' in all_cookie_names or 'session_list' in all_cookie_names
            on_messenger = 'messenger' in current_url

            if has_session and on_messenger:
                # Wait a moment for all cookies to settle, then capture
                await asyncio.sleep(2)
                cookies = await context.cookies()
                cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                logger.info("Login successful! Cookie captured.")
                break

            await asyncio.sleep(1)

        await browser.close()

    if not cookie_str:
        raise TimeoutError(f"Login not completed within {timeout} seconds")

    # Save cookie to file
    save_cookie_to_file(cookie_str)

    return cookie_str


def login_interactive(timeout: int = 180) -> str:
    """
    Synchronous wrapper for browser login.

    Returns:
        Cookie string for API authentication
    """
    return asyncio.run(browser_login(timeout))
