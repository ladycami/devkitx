"""Simple, reliable async/sync conversion for Python.

Folded into devkitx from the standalone `asyncbridge` 1.0.0 package
(MIT, same author). Public names are unchanged.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Callable, Coroutine
from concurrent.futures import ThreadPoolExecutor
from typing import Any, ParamSpec, TypeVar

__all__ = ["async_to_sync", "sync_to_async"]

P = ParamSpec("P")
R = TypeVar("R")

_executor = ThreadPoolExecutor(max_workers=10)


def async_to_sync(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, R]:
    """Convert an async function to sync.

    Handles event loop detection and creation correctly:
    - If no loop is running, creates a new one
    - If a loop is running, uses run_in_executor to avoid conflicts

    Args:
        func: Async function to convert

    Returns:
        Synchronous wrapper function

    Example:
        >>> @async_to_sync
        ... async def fetch_data():
        ...     await asyncio.sleep(0.1)
        ...     return "data"
        >>> result = fetch_data()  # Blocks until complete
        >>> print(result)
        'data'
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        coro = func(*args, **kwargs)

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop - safe to use asyncio.run()
            return asyncio.run(coro)

        # Loop is running - we need to run in a new thread
        import concurrent.futures

        def run_in_new_loop() -> R:
            new_loop = asyncio.new_event_loop()
            try:
                return new_loop.run_until_complete(coro)
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(run_in_new_loop)
            return future.result()

    return wrapper


def sync_to_async(
    func: Callable[P, R],
    executor: ThreadPoolExecutor | None = None,
) -> Callable[P, Coroutine[Any, Any, R]]:
    """Convert a sync function to async.

    Runs the sync function in a thread pool executor to avoid
    blocking the event loop.

    Args:
        func: Sync function to convert
        executor: Optional custom executor (uses default if not provided)

    Returns:
        Async wrapper function

    Example:
        >>> @sync_to_async
        ... def blocking_io():
        ...     time.sleep(1)
        ...     return "done"
        >>> result = await blocking_io()  # Doesn't block event loop
    """
    pool = executor or _executor

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(pool, functools.partial(func, *args, **kwargs))

    return wrapper
