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
    """
    Quick logger setup for scripts/apps. Libraries should not call this by default.
    """
    if use_loguru:
        try:
            from loguru import logger as _loguru  # type: ignore

            _loguru.remove()
            fmt = (
                "{{\"time\": \"{time}\", \"level\": \"{level}\", \"message\": \"{message}\"}}"
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

            logging.basicConfig(handlers=[Intercept()], level=getattr(logging, level.upper(), logging.INFO))
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
    lg = logger or logging.getLogger("dev_qol_toolkit")
    start = time.perf_counter()
    try:
        yield
    finally:
        dur = (time.perf_counter() - start) * 1000.0
        lg.info("%s took %.2f ms", name, dur)


def log_calls(fn: Callable[..., _T]) -> Callable[..., _T]:
    import functools

    logger = logging.getLogger("dev_qol_toolkit")

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> _T:
        logger.debug("Calling %s args=%r kwargs=%r", fn.__name__, args, kwargs)
        result = fn(*args, **kwargs)
        logger.debug("Returned %s -> %r", fn.__name__, result)
        return result

    return wrapper