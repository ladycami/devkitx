"""Logging utilities for DevKitX.

This module provides utilities for setting up logging, timing operations,
and decorating functions with logging capabilities.
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from typing import Any, Callable, TypeVar

_T = TypeVar("_T")


def setup_logging(
    level: str = "INFO",
    to_file: str | None = None,
    json: bool = False,
    use_loguru: bool = False,
) -> logging.Logger:
    """Set up logging configuration for applications.

    Note: Libraries should not call this function by default as it configures
    global logging state. This is intended for application entry points.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        to_file: Optional file path to write logs to
        json: Whether to format logs as JSON
        use_loguru: Whether to use loguru library if available

    Returns:
        Configured logger instance

    Examples:
        >>> logger = setup_logging("DEBUG")
        >>> logger = setup_logging("INFO", to_file="app.log")
        >>> logger = setup_logging("INFO", json=True, use_loguru=True)
    """
    if use_loguru:
        try:
            from loguru import logger as _loguru  # type: ignore

            _loguru.remove()
            fmt = (
                '{{"time": "{time}", "level": "{level}", "message": "{message}"}}'
                if json
                else "<green>{time}</green> | <level>{level}</level> | <cyan>{message}</cyan>"
            )
            sink = to_file or sys.stderr
            _loguru.add(sink, format=fmt, level=level)

            # bridge to stdlib logger
            class Intercept(logging.Handler):
                def emit(self, record: logging.LogRecord) -> None:
                    _loguru.opt(depth=6, exception=record.exc_info).log(
                        record.levelname, record.getMessage()
                    )

            logging.basicConfig(
                handlers=[Intercept()], level=getattr(logging, level.upper(), logging.INFO)
            )
            return logging.getLogger("dev_qol_toolkit")
        except Exception:
            # fall back
            pass

    logger = logging.getLogger("dev_qol_toolkit")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    fmt = (
        '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
        if json
        else "%(asctime)s | %(levelname)s | %(message)s"
    )
    formatter = logging.Formatter(fmt)

    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if to_file:
        fh = logging.FileHandler(to_file, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


@contextmanager
def log_time(name: str = "block", logger: logging.Logger | None = None):
    """Context manager to log execution time of a code block.

    Args:
        name: Name to use in the log message
        logger: Optional logger instance (uses default if None)

    Examples:
        >>> with log_time("database_query"):
        ...     # Some database operation
        ...     time.sleep(0.1)
        # Logs: "database_query took 100.23 ms"

        >>> import logging
        >>> custom_logger = logging.getLogger("myapp")
        >>> with log_time("api_call", custom_logger):
        ...     # Some API call
        ...     pass
    """
    lg = logger or logging.getLogger("dev_qol_toolkit")
    start = time.perf_counter()
    try:
        yield
    finally:
        dur = (time.perf_counter() - start) * 1000.0
        lg.info("%s took %.2f ms", name, dur)


def log_calls(fn: Callable[..., _T]) -> Callable[..., _T]:
    """Decorator to log function calls and returns at DEBUG level.

    Args:
        fn: Function to decorate

    Returns:
        Decorated function that logs calls and returns

    Examples:
        >>> @log_calls
        ... def add(a: int, b: int) -> int:
        ...     return a + b
        >>> result = add(2, 3)
        # Logs at DEBUG level:
        # "Calling add args=(2, 3) kwargs={}"
        # "Returned add -> 5"

        >>> @log_calls
        ... def process_data(data: list, **options) -> dict:
        ...     return {"processed": len(data)}
        >>> result = process_data([1, 2, 3], format="json")
        # Logs function call with arguments and return value
    """
    import functools

    logger = logging.getLogger("dev_qol_toolkit")

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> _T:
        logger.debug("Calling %s args=%r kwargs=%r", fn.__name__, args, kwargs)
        result = fn(*args, **kwargs)
        logger.debug("Returned %s -> %r", fn.__name__, result)
        return result

    return wrapper
