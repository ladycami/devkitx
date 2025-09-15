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
        tz_name: Timezone name (e.g., 'US/Eastern', 'Europe/London', 'UTC')
        
    Returns:
        Timezone offset as timedelta
        
    Raises:
        ValueError: If timezone name is not recognized
        
    Examples:
        >>> get_timezone_offset("UTC")
        datetime.timedelta(0)
        >>> # Note: Actual offsets depend on current date due to DST
    """
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        # Fallback for Python < 3.9 or systems without zoneinfo
        try:
            import pytz
            tz = pytz.timezone(tz_name)
            # Get current offset (this will vary with DST)
            now = datetime.now(tz)
            return now.utcoffset() or timedelta(0)
        except ImportError:
            # Basic fallback for common timezones
            common_offsets = {
                "UTC": timedelta(0),
                "GMT": timedelta(0),
                "EST": timedelta(hours=-5),
                "CST": timedelta(hours=-6),
                "MST": timedelta(hours=-7),
                "PST": timedelta(hours=-8),
                "EDT": timedelta(hours=-4),
                "CDT": timedelta(hours=-5),
                "MDT": timedelta(hours=-6),
                "PDT": timedelta(hours=-7),
            }
            if tz_name in common_offsets:
                return common_offsets[tz_name]
            raise ValueError(f"Timezone '{tz_name}' not recognized and zoneinfo/pytz not available")
    
    try:
        tz = ZoneInfo(tz_name)
        # Get current offset (this will vary with DST)
        now = datetime.now(tz)
        return now.utcoffset() or timedelta(0)
    except Exception as e:
        raise ValueError(f"Invalid timezone name '{tz_name}': {e}")


def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (Monday-Friday).
    
    Args:
        date: Date to check
        
    Returns:
        True if business day, False otherwise
        
    Examples:
        >>> # Monday is a business day
        >>> is_business_day(datetime(2024, 1, 15))  # Monday
        True
        >>> # Saturday is not a business day
        >>> is_business_day(datetime(2024, 1, 13))  # Saturday
        False
        >>> # Sunday is not a business day
        >>> is_business_day(datetime(2024, 1, 14))  # Sunday
        False
    """
    # Monday is 0, Sunday is 6
    return date.weekday() < 5


def next_business_day(date: datetime) -> datetime:
    """Get next business day from given date.
    
    Args:
        date: Starting date
        
    Returns:
        Next business day (preserves time component)
        
    Examples:
        >>> # From Friday, next business day is Monday
        >>> next_business_day(datetime(2024, 1, 12, 14, 30))  # Friday
        datetime.datetime(2024, 1, 15, 14, 30)
        >>> # From Wednesday, next business day is Thursday
        >>> next_business_day(datetime(2024, 1, 10, 9, 0))   # Wednesday
        datetime.datetime(2024, 1, 11, 9, 0)
    """
    next_date = date + timedelta(days=1)
    
    # Keep adding days until we find a business day
    while not is_business_day(next_date):
        next_date += timedelta(days=1)
    
    return next_date


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