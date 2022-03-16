import asyncio
import importlib.metadata
from typing import Any, Dict, cast

from greenlet import greenlet

from playwright._impl._api_types import Error
from playwright._impl._browser import Browser as BrowserImpl
from playwright._impl._connection import Connection, from_channel
from playwright._impl._object_factory import create_remote_object
from playwright._impl._playwright import Playwright as PlaywrightImpl
from playwright._impl._transport import WebSocketTransport
from playwright.sync_api._generated import Browser as SyncBrowser


class ConnectToBrowserContextManager:
    def __init__(
        self,
        ws_endpoint: str,
        slow_mo: float = None,
        headers: Dict[str, str] = None,
    ) -> None:
        self._browser: SyncBrowser
        self._ws_endpoint = ws_endpoint
        self._slow_mo = slow_mo
        self._headers = headers

    def _make_connection(self, dispatcher_fiber, object_factory, transport, loop) -> Connection:
        if importlib.metadata.version('playwright') < '1.15.0':
            return Connection(
                dispatcher_fiber,
                create_remote_object,
                transport)
        else:
            return Connection(
                dispatcher_fiber,
                create_remote_object,
                transport,
                loop)

    def _setup_browser(self, browser: BrowserImpl):
        version = importlib.metadata.version('playwright')
        if version < '1.17.0':
            browser._is_remote = True
            browser._is_connected_over_websocket = True
        elif version < '1.19.0':
            browser._should_close_connection_on_close = True
        else:
            browser._should_close_connection_on_close = True
            browser._local_utils = self._playwright_impl._utils

    def __enter__(self) -> SyncBrowser:
        loop: asyncio.AbstractEventLoop
        own_loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            own_loop = loop
        if loop.is_running():
            raise Error(
                """It looks like you are using Playwright Sync API inside the asyncio loop.
Please use the Async API instead."""
            )

        def greenlet_main() -> None:
            loop.run_until_complete(self._connection.run_as_sync())

            if own_loop:
                loop.run_until_complete(loop.shutdown_asyncgens())
                loop.close()

        dispatcher_fiber = greenlet(greenlet_main)
        transport = WebSocketTransport(
            loop,
            self._ws_endpoint,
            self._headers,
            self._slow_mo)
        self._connection = self._make_connection(
            dispatcher_fiber,
            create_remote_object,
            transport,
            loop)

        g_self = greenlet.getcurrent()

        def callback_wrapper(playwright_impl: PlaywrightImpl) -> None:
            self._playwright_impl = playwright_impl
            g_self.switch()

        self._connection.call_on_object_with_known_name(
            "Playwright", callback_wrapper)

        dispatcher_fiber.switch()

        pre_launched_browser = self._playwright_impl._initializer.get(
            "preLaunchedBrowser")
        assert pre_launched_browser
        browser = cast(BrowserImpl, from_channel(pre_launched_browser))
        self._setup_browser(browser)

        def handle_transport_close() -> None:
            for context in browser.contexts:
                for page in context.pages:
                    page._on_close()
                context._on_close()
            browser._on_close()

        transport.once("close", handle_transport_close)

        self._browser = SyncBrowser(browser)
        return self._browser

    def start(self) -> SyncBrowser:
        return self.__enter__()

    def __exit__(self, *args: Any) -> None:
        self._browser.close()


def connect_to_browser(
    ws_endpoint: str,
    slow_mo: float = None,
    headers: Dict[str, str] = None,
) -> SyncBrowser:
    return ConnectToBrowserContextManager(ws_endpoint, slow_mo, headers)
