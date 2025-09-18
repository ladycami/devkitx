"""Retry logic with exponential backoff for robust operations.

This module provides retry functionality with exponential backoff and jitter
to handle transient failures gracefully.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar, Tuple, Type, Union

T = TypeVar("T")


def with_retries(
    fn: Callable[[], T],
    *,
    retries: int = 3,
    base_delay: float = 0.2,
    jitter: float = 0.2,
    retry_on: Tuple[Type[BaseException], ...] = (Exception,),
) -> T:
    """Execute function with exponential backoff retry logic.
    
    Executes the provided function with automatic retry on specified exceptions,
    using exponential backoff with jitter to avoid thundering herd problems.
    
    Args:
        fn: Function to execute (should take no arguments)
        retries: Number of retry attempts (default: 3)
        base_delay: Base delay in seconds for exponential backoff (default: 0.2)
        jitter: Maximum jitter to add to delay in seconds (default: 0.2)
        retry_on: Tuple of exception types to retry on (default: (Exception,))
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception encountered if all retries are exhausted
        
    Examples:
        >>> import httpx
        >>> def make_request():
        ...     with httpx.Client() as client:
        ...         return client.get("https://api.example.com/data")
        >>> 
        >>> # Retry on any exception
        >>> response = with_retries(make_request)
        
        >>> # Retry only on specific exceptions
        >>> response = with_retries(
        ...     make_request,
        ...     retries=5,
        ...     base_delay=0.5,
        ...     retry_on=(httpx.RequestError, httpx.HTTPStatusError)
        ... )
        
        >>> # Custom function with parameters using lambda
        >>> def api_call(url, headers):
        ...     with httpx.Client() as client:
        ...         return client.get(url, headers=headers)
        >>> 
        >>> response = with_retries(
        ...     lambda: api_call("https://api.example.com", {"Auth": "token"})
        ... )
    """
    last_exception: Union[BaseException, None] = None
    
    for attempt in range(retries + 1):
        try:
            return fn()
        except retry_on as e:
            last_exception = e
            if attempt == retries:
                # Last attempt failed, re-raise the exception
                raise
            
            # Calculate delay with exponential backoff and jitter
            exponential_delay = base_delay * (2 ** attempt)
            jitter_amount = random.uniform(0, jitter)
            total_delay = exponential_delay + jitter_amount
            
            time.sleep(total_delay)
    
    # This should never be reached, but just in case
    if last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("Unexpected state in retry logic")