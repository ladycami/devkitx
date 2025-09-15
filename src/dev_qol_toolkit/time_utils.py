"""Date and time utilities for the dev-qol-toolkit.

This module provides utilities for date parsing, formatting, timezone handling,
business day calculations, and scheduling.
"""

from datetime import datetime, timedelta
from typing import Any

__all__ = [
    "parse_date",
    "format_duration",
    "get_timezone_offset",
    "is_business_day",
    "next_business_day",
    "cron_next_run",
    "Timer",
]


def parse_date(date_str: str, formats: list[str] | None = None) -> datetime:
    """Parse date string using multiple format attempts.
    
    Args:
        date_str: Date string to parse
        formats: Optional list of date formats to try
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date string cannot be parsed with any format
        
    Examples:
        >>> parse_date("2024-01-15")
        datetime.datetime(2024, 1, 15, 0, 0)
        >>> parse_date("15/01/2024", ["%d/%m/%Y"])
        datetime.datetime(2024, 1, 15, 0, 0)
    """
    if formats is None:
        # Common date formats to try
        formats = [
            "%Y-%m-%d",           # 2024-01-15
            "%Y-%m-%d %H:%M:%S",  # 2024-01-15 14:30:00
            "%Y-%m-%d %H:%M",     # 2024-01-15 14:30
            "%Y/%m/%d",           # 2024/01/15
            "%Y/%m/%d %H:%M:%S",  # 2024/01/15 14:30:00
            "%Y/%m/%d %H:%M",     # 2024/01/15 14:30
            "%d-%m-%Y",           # 15-01-2024
            "%d-%m-%Y %H:%M:%S",  # 15-01-2024 14:30:00
            "%d-%m-%Y %H:%M",     # 15-01-2024 14:30
            "%d/%m/%Y",           # 15/01/2024
            "%d/%m/%Y %H:%M:%S",  # 15/01/2024 14:30:00
            "%d/%m/%Y %H:%M",     # 15/01/2024 14:30
            "%m-%d-%Y",           # 01-15-2024
            "%m-%d-%Y %H:%M:%S",  # 01-15-2024 14:30:00
            "%m-%d-%Y %H:%M",     # 01-15-2024 14:30
            "%m/%d/%Y",           # 01/15/2024
            "%m/%d/%Y %H:%M:%S",  # 01/15/2024 14:30:00
            "%m/%d/%Y %H:%M",     # 01/15/2024 14:30
            "%Y%m%d",             # 20240115
            "%Y%m%d%H%M%S",       # 20240115143000
            "%Y%m%d%H%M",         # 202401151430
            "%B %d, %Y",          # January 15, 2024
            "%b %d, %Y",          # Jan 15, 2024
            "%d %B %Y",           # 15 January 2024
            "%d %b %Y",           # 15 Jan 2024
            "%Y-%m-%dT%H:%M:%S",  # ISO format without timezone
            "%Y-%m-%dT%H:%M:%SZ", # ISO format with Z
            "%Y-%m-%dT%H:%M:%S.%f", # ISO format with microseconds
            "%Y-%m-%dT%H:%M:%S.%fZ", # ISO format with microseconds and Z
        ]
    
    # Try each format until one works
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    # If no format worked, raise an error
    raise ValueError(f"Unable to parse date string '{date_str}' with any of the provided formats")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human-readable duration string
        
    Examples:
        >>> format_duration(30)
        '30.0s'
        >>> format_duration(90)
        '1m 30.0s'
        >>> format_duration(3661)
        '1h 1m 1.0s'
        >>> format_duration(90061)
        '1d 1h 1m 1.0s'
    """
    if seconds < 0:
        return f"-{format_duration(-seconds)}"
    
    if seconds == 0:
        return "0.0s"
    
    # Time units in seconds
    units = [
        ("d", 86400),  # days
        ("h", 3600),   # hours
        ("m", 60),     # minutes
        ("s", 1),      # seconds
    ]
    
    parts = []
    remaining = seconds
    started = False  # Track if we've started adding units
    
    for unit_name, unit_seconds in units:
        if remaining >= unit_seconds or started:
            if unit_name == "s":
                # For seconds, show decimal places
                parts.append(f"{remaining:.1f}{unit_name}")
                break
            else:
                # For other units, use integer division
                count = int(remaining // unit_seconds)
                parts.append(f"{count}{unit_name}")
                remaining = remaining % unit_seconds
                if count > 0:
                    started = True
    
    # If we only have fractional seconds left and no other parts
    if not parts and remaining > 0:
        parts.append(f"{remaining:.1f}s")
    
    return " ".join(parts)


def get_timezone_offset(tz_name: str) -> timedelta:
    """Get timezone offset from UTC.
    
    Args:
        tz_name: Timezone name (e.g., 'US/Eastern')
        
    Returns:
        Timezone offset as timedelta
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 10.2")


def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (Monday-Friday).
    
    Args:
        date: Date to check
        
    Returns:
        True if business day, False otherwise
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 10.2")


def next_business_day(date: datetime) -> datetime:
    """Get next business day from given date.
    
    Args:
        date: Starting date
        
    Returns:
        Next business day
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 10.2")


def cron_next_run(cron_expr: str, from_time: datetime | None = None) -> datetime:
    """Calculate next run time for cron expression.
    
    Args:
        cron_expr: Cron expression
        from_time: Starting time, defaults to now
        
    Returns:
        Next scheduled run time
    """
    # Placeholder implementation
    raise NotImplementedError("Function will be implemented in task 10.3")


class Timer:
    """Simple timer for measuring elapsed time."""
    
    def __init__(self) -> None:
        """Initialize timer."""
        # Placeholder implementation
        raise NotImplementedError("Class will be implemented in task 10.3")
    
    def start(self) -> None:
        """Start the timer."""
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 10.3")
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time.
        
        Returns:
            Elapsed time in seconds
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 10.3")
    
    def elapsed(self) -> float:
        """Get elapsed time without stopping timer.
        
        Returns:
            Elapsed time in seconds
        """
        # Placeholder implementation
        raise NotImplementedError("Method will be implemented in task 10.3")