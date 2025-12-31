"""JSON utilities for DevKitX."""

from __future__ import annotations

from typing import Any


def flatten_json(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """Flatten nested JSON structure into dot-notation keys.
    
    Args:
        data: Dictionary to flatten
        separator: Key separator (default: ".")
        
    Returns:
        Flattened dictionary
        
    Example:
        >>> data = {"user": {"name": "John", "age": 30}, "active": True}
        >>> flatten_json(data)
        {'user.name': 'John', 'user.age': 30, 'active': True}
    """
    def _flatten(obj: Any, parent_key: str = "") -> dict[str, Any]:
        items = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}{separator}{key}" if parent_key else key
                items.extend(_flatten(value, new_key).items())
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                items.extend(_flatten(value, new_key).items())
        else:
            return {parent_key: obj}
        
        return dict(items)
    
    return _flatten(data)


def unflatten_json(data: dict[str, Any], separator: str = ".") -> dict[str, Any]:
    """Unflatten dot-notation keys back to nested structure.
    
    Args:
        data: Flattened dictionary
        separator: Key separator (default: ".")
        
    Returns:
        Nested dictionary
        
    Example:
        >>> flat = {'user.name': 'John', 'user.age': 30, 'active': True}
        >>> unflatten_json(flat)
        {'user': {'name': 'John', 'age': 30}, 'active': True}
    """
    result: dict[str, Any] = {}
    
    for key, value in data.items():
        parts = key.split(separator)
        current = result
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    return result