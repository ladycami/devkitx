"""Async-compatible utilities for DevKitX.

This module provides utilities for bridging sync/async code and
async-compatible versions of common operations.
"""

import asyncio
import functools
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")

__all__ = [
    "sync_to_async",
    "async_to_sync",
    "gather_with_limit",
    "retry_async",
    "AsyncFileManager",
]


def sync_to_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """Convert synchronous function to async.

    This function wraps a synchronous function to run in a thread pool,
    making it awaitable without blocking the event loop.

    Args:
        func: Synchronous function to convert

    Returns:
        Async version of the function

    Example:
        >>> def slow_sync_function(x: int) -> int:
        ...     time.sleep(1)
        ...     return x * 2
        >>> async_func = sync_to_async(slow_sync_function)
        >>> result = await async_func(5)  # Returns 10 without blocking
    """

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, functools.partial(func, *args, **kwargs))

    return async_wrapper


def async_to_sync(func: Callable[..., Awaitable[T]]) -> Callable[..., T]:
    """Convert asynchronous function to sync.

    This function wraps an async function to run synchronously by
    creating or using an existing event loop.

    Args:
        func: Asynchronous function to convert

    Returns:
        Sync version of the function

    Example:
        >>> async def async_function(x: int) -> int:
        ...     await asyncio.sleep(0.1)
        ...     return x * 2
        >>> sync_func = async_to_sync(async_function)
        >>> result = sync_func(5)  # Returns 10, blocks until complete
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            # Try to get the current event loop
            asyncio.get_running_loop()
            # If we're already in an async context, we can't use asyncio.run()
            # Instead, we need to schedule the coroutine
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, func(*args, **kwargs))
                return future.result()
        except RuntimeError:
            # No event loop running, we can use asyncio.run()
            return asyncio.run(func(*args, **kwargs))

    return sync_wrapper


async def gather_with_limit(limit: int, *awaitables: Awaitable[T]) -> list[T]:
    """Gather awaitables with concurrency limit.

    Executes multiple awaitable objects concurrently but limits the number
    of concurrent operations to prevent overwhelming the system.

    Args:
        limit: Maximum number of concurrent operations
        *awaitables: Awaitable objects to gather

    Returns:
        List of results in the same order as input awaitables

    Raises:
        ValueError: If limit is less than 1

    Example:
        >>> async def fetch_data(url: str) -> str:
        ...     # Simulate API call
        ...     await asyncio.sleep(0.1)
        ...     return f"Data from {url}"
        >>>
        >>> urls = [f"http://api.example.com/{i}" for i in range(10)]
        >>> tasks = [fetch_data(url) for url in urls]
        >>> results = await gather_with_limit(3, *tasks)  # Max 3 concurrent
    """
    if limit < 1:
        raise ValueError("Limit must be at least 1")

    if not awaitables:
        return []

    # Use asyncio.Semaphore to limit concurrency
    semaphore = asyncio.Semaphore(limit)

    async def _limited_awaitable(awaitable: Awaitable[T]) -> T:
        async with semaphore:
            return await awaitable

    # Wrap all awaitables with semaphore
    limited_awaitables = [_limited_awaitable(awaitable) for awaitable in awaitables]

    # Gather all results
    return await asyncio.gather(*limited_awaitables)


async def retry_async(
    func: Callable[..., Awaitable[T]],
    retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    *args: Any,
    **kwargs: Any,
) -> T:
    """Retry async function with exponential backoff.

    Attempts to execute an async function multiple times with increasing
    delays between attempts if it fails.

    Args:
        func: Async function to retry
        retries: Number of retry attempts (not including initial attempt)
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay after each failed attempt
        exceptions: Tuple of exception types to catch and retry on
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Function result

    Raises:
        The last exception raised by the function if all retries are exhausted

    Example:
        >>> async def unreliable_api_call(data: str) -> str:
        ...     if random.random() < 0.7:  # 70% chance of failure
        ...         raise ConnectionError("API temporarily unavailable")
        ...     return f"Success: {data}"
        >>>
        >>> result = await retry_async(
        ...     unreliable_api_call,
        ...     retries=3,
        ...     delay=0.5,
        ...     exceptions=(ConnectionError,),
        ...     "test_data"
        ... )
    """
    last_exception = None
    current_delay = delay

    for attempt in range(retries + 1):  # +1 for initial attempt
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt == retries:  # Last attempt failed
                break

            # Wait before retrying
            await asyncio.sleep(current_delay)
            current_delay *= backoff_factor

    # All attempts failed, raise the last exception
    if last_exception:
        raise last_exception
    else:
        # This shouldn't happen, but just in case
        raise RuntimeError("All retry attempts failed")


class AsyncFileManager:
    """Async file operations manager.

    Provides async versions of common file operations that don't block
    the event loop by running in a thread pool.

    Example:
        >>> async_fm = AsyncFileManager()
        >>> content = await async_fm.read_text("example.txt")
        >>> await async_fm.write_text("output.txt", "Hello, World!")
        >>> await async_fm.copy_file("source.txt", "destination.txt")
    """

    def __init__(self, encoding: str = "utf-8"):
        """Initialize AsyncFileManager.

        Args:
            encoding: Default text encoding for file operations
        """
        self.encoding = encoding

    async def read_text(self, path: str | Path, encoding: str | None = None) -> str:
        """Read text file asynchronously.

        Args:
            path: Path to file
            encoding: Text encoding (defaults to instance encoding)

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If lacking read permissions
            UnicodeDecodeError: If file can't be decoded with specified encoding
        """
        path_obj = Path(path)
        encoding = encoding or self.encoding

        def _read_sync() -> str:
            return path_obj.read_text(encoding=encoding)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _read_sync)

    async def write_text(
        self,
        path: str | Path,
        content: str,
        encoding: str | None = None,
        create_parents: bool = True,
    ) -> None:
        """Write text file asynchronously.

        Args:
            path: Path to file
            content: Content to write
            encoding: Text encoding (defaults to instance encoding)
            create_parents: Whether to create parent directories if they don't exist

        Raises:
            PermissionError: If lacking write permissions
            OSError: If unable to create parent directories
        """
        path_obj = Path(path)
        encoding = encoding or self.encoding

        def _write_sync() -> None:
            if create_parents:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            path_obj.write_text(content, encoding=encoding)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, _write_sync)

    async def copy_file(
        self, src: str | Path, dst: str | Path, create_parents: bool = True
    ) -> None:
        """Copy file asynchronously.

        Args:
            src: Source file path
            dst: Destination file path
            create_parents: Whether to create parent directories if they don't exist

        Raises:
            FileNotFoundError: If source file doesn't exist
            PermissionError: If lacking read/write permissions
            OSError: If unable to create parent directories
        """
        src_path = Path(src)
        dst_path = Path(dst)

        def _copy_sync() -> None:
            if create_parents:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, _copy_sync)

    async def read_bytes(self, path: str | Path) -> bytes:
        """Read binary file asynchronously.

        Args:
            path: Path to file

        Returns:
            File contents as bytes

        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If lacking read permissions
        """
        path_obj = Path(path)

        def _read_sync() -> bytes:
            return path_obj.read_bytes()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _read_sync)

    async def write_bytes(
        self, path: str | Path, content: bytes, create_parents: bool = True
    ) -> None:
        """Write binary file asynchronously.

        Args:
            path: Path to file
            content: Content to write as bytes
            create_parents: Whether to create parent directories if they don't exist

        Raises:
            PermissionError: If lacking write permissions
            OSError: If unable to create parent directories
        """
        path_obj = Path(path)

        def _write_sync() -> None:
            if create_parents:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            path_obj.write_bytes(content)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, _write_sync)

    async def exists(self, path: str | Path) -> bool:
        """Check if file exists asynchronously.

        Args:
            path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        path_obj = Path(path)

        def _exists_sync() -> bool:
            return path_obj.exists()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _exists_sync)

    async def mkdir(self, path: str | Path, parents: bool = True, exist_ok: bool = True) -> None:
        """Create directory asynchronously.

        Args:
            path: Directory path to create
            parents: Whether to create parent directories
            exist_ok: Whether to ignore if directory already exists

        Raises:
            FileExistsError: If directory exists and exist_ok is False
            PermissionError: If lacking permissions to create directory
        """
        path_obj = Path(path)

        def _mkdir_sync() -> None:
            path_obj.mkdir(parents=parents, exist_ok=exist_ok)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, _mkdir_sync)

    async def remove(self, path: str | Path) -> None:
        """Remove file asynchronously.

        Args:
            path: Path to file to remove

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If lacking permissions to remove file
            IsADirectoryError: If path is a directory
        """
        path_obj = Path(path)

        def _remove_sync() -> None:
            path_obj.unlink()

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, _remove_sync)

    async def list_dir(self, path: str | Path) -> list[Path]:
        """List directory contents asynchronously.

        Args:
            path: Directory path to list

        Returns:
            List of Path objects for directory contents

        Raises:
            FileNotFoundError: If directory doesn't exist
            NotADirectoryError: If path is not a directory
            PermissionError: If lacking permissions to read directory
        """
        path_obj = Path(path)

        def _list_sync() -> list[Path]:
            return list(path_obj.iterdir())

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, _list_sync)
