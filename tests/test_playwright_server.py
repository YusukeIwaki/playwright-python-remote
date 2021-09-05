from playwright_remote.sync_api import sync_playwright_remote
from PIL import Image
import os


def test_connect():
    try:
        with sync_playwright_remote(os.environ['PLAYWRIGHT_SERVER_WS_ENDPOINT']) as playwright:
            with playwright.chromium.launch() as browser:
                page = browser.new_page(
                    viewport={'width': 1200, 'height': 800})
                page.goto('https://github.com/')
                page.screenshot(path="YusukeIwaki.png")

        png = Image.open('YusukeIwaki.png')
        assert png.width == 1200
        assert png.height == 800
    finally:
        if os.path.exists('YusukeIwaki.png'):
            os.remove('YusukeIwaki.png')
