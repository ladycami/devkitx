"""Sync/async bridge utilities for DevKitX.

This module provides utilities for safely converting between synchronous
and asynchronous functions, handling event loop detection and thread execution.
"""

import asyncio
import functools
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")
R = TypeVar("R")

__all__ = [
    "async_to_sync",
    "sync_to_async",
]


def async_to_sync(fn: Callable[..., Awaitable[R]]) -> Callable[..., R]:
    """Convert async function to sync, handling event loop detection.
    
    This function wraps an async function to run synchronously by detecting
    whether an event loop is already running and handling appropriately.
    
    Args:
        fn: Asynchronous function to convert
        
    Returns:
        Sync version of the function
        
    Example:
        >>> async def async_add_one(x: int) -> int:
        ...     await asyncio.sleep(0.01)  # Simulate async work
        ...     return x + 1
        >>> sync_fn = async_to_sync(async_add_one)
        >>> result = sync_fn(2)  # Returns 3
    """
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        try:
            # Check if there's already a running event loop
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, safe to use asyncio.run()
            return asyncio.run(fn(*args, **kwargs))
        else:
            # Running loop exists, we need to run in a new thread
            # to avoid "RuntimeError: cannot be called from a running event loop"
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, fn(*args, **kwargs))
                return future.result()
    
    return wrapper


def sync_to_async(fn: Callable[..., R]) -> Callable[..., Awaitable[R]]:
    """Convert sync function to async using thread executor.
    
    This function wraps a synchronous function to run in a thread pool,
    making it awaitable without blocking the event loop.
    
    Args:
        fn: Synchronous function to convert
        
    Returns:
        Async version of the function
        
    Example:
        >>> def sync_multiply_two(x: int) -> int:
        ...     return x * 2
        >>> async_fn = sync_to_async(sync_multiply_two)
        >>> result = await async_fn(3)  # Returns 6
    """
    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> R:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))
    
    return wrapper