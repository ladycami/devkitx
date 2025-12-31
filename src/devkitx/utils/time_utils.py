"""Time and duration utilities."""

from __future__ import annotations

import re
from typing import Optional


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds.
    
    Args:
        duration_str: Duration string (e.g., "1h30m", "90s", "2d")
        
    Returns:
        Duration in seconds
        
    Raises:
        ValueError: If duration string is invalid
        
    Example:
        >>> parse_duration("1h30m")
        5400
        >>> parse_duration("2d")
        172800
    """
    duration_str = duration_str.strip().lower()
    
    # Pattern to match number + unit
    pattern = r'(\d+(?:\.\d+)?)\s*([smhdw])'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        raise ValueError(f"Invalid duration format: {duration_str}")
    
    total_seconds = 0
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400,
        'w': 604800,
    }
    
    for value_str, unit in matches:
        value = float(value_str)
        if unit not in units:
            raise ValueError(f"Unknown time unit: {unit}")
        total_seconds += value * units[unit]
    
    return int(total_seconds)


def format_duration(seconds: int, precision: int = 2) -> str:
    """Format seconds as human-readable duration.
    
    Args:
        seconds: Duration in seconds
        precision: Number of units to include
        
    Returns:
        Formatted duration string
        
    Example:
        >>> format_duration(5400)
        '1h 30m'
        >>> format_duration(90)
        '1m 30s'
    """
    if seconds == 0:
        return "0s"
    
    units = [
        ('w', 604800),
        ('d', 86400),
        ('h', 3600),
        ('m', 60),
        ('s', 1),
    ]
    
    parts = []
    remaining = abs(seconds)
    
    for unit_name, unit_seconds in units:
        if remaining >= unit_seconds:
            count = remaining // unit_seconds
            remaining = remaining % unit_seconds
            parts.append(f"{count}{unit_name}")
            
            if len(parts) >= precision:
                break
    
    if not parts:
        return "0s"
    
    result = " ".join(parts)
    return f"-{result}" if seconds < 0 else result