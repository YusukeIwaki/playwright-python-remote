from playwright_remote.sync_api import connect_to_browser
from PIL import Image
import os


def test_connect():
    try:
        with connect_to_browser(os.environ['BROWSER_SERVER_WS_ENDPOINT']) as browser:
            page = browser.new_page(viewport={'width': 1200, 'height': 800})
            page.goto('https://github.com/')
            page.screenshot(path="YusukeIwaki.png")

        png = Image.open('YusukeIwaki.png')
        assert png.width == 1200
        assert png.height == 800
    finally:
        if os.path.exists('YusukeIwaki.png'):
            os.remove('YusukeIwaki.png')
