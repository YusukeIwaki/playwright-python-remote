import asyncio
import importlib.metadata
from typing import Any

from greenlet import greenlet

from playwright._impl._api_types import Error
from playwright._impl._connection import Connection
from playwright._impl._object_factory import create_remote_object
from playwright._impl._playwright import Playwright
from playwright._impl._transport import WebSocketTransport
from playwright.sync_api._generated import Playwright as SyncPlaywright


class SyncPlaywrightRemoteContextManager:
    def __init__(self, ws_endpoint: str) -> None:
        self._playwright: SyncPlaywright
        self._ws_endpoint = ws_endpoint

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

    def __enter__(self) -> SyncPlaywright:
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
        self._connection = self._make_connection(
            dispatcher_fiber,
            create_remote_object,
            WebSocketTransport(loop, self._ws_endpoint),
            loop)

        g_self = greenlet.getcurrent()

        def callback_wrapper(playwright_impl: Playwright) -> None:
            self._playwright = SyncPlaywright(playwright_impl)
            g_self.switch()

        self._connection.call_on_object_with_known_name(
            "Playwright", callback_wrapper)

        dispatcher_fiber.switch()
        playwright = self._playwright
        playwright.stop = self.__exit__  # type: ignore
        return playwright

    def start(self) -> SyncPlaywright:
        return self.__enter__()

    def __exit__(self, *args: Any) -> None:
        self._connection.stop_sync()


def sync_playwright_remote(ws_endpoint: str) -> SyncPlaywrightRemoteContextManager:
    return SyncPlaywrightRemoteContextManager(ws_endpoint)
