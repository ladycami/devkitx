from __future__ import annotations

import re
from typing import Any, Iterable


_CAMEL_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake(name: str) -> str:
    s1 = _CAMEL_1.sub(r"\1_\2", name)
    return _CAMEL_2.sub(r"\1_\2", s1).lower()


def to_camel(name: str) -> str:
    parts = re.split(r"[_\-\s]+", name)
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def chunk_list(lst: list[Any], size: int) -> list[list[Any]]:
    if size <= 0:
        raise ValueError("size must be > 0")
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten_list(lst: list[list[Any]]) -> list[Any]:
    out: list[Any] = []
    for sub in lst:
        out.extend(sub)
    return out


def deep_get(d: dict, keys: list[str], default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge two dictionaries, with dict2 values taking precedence.
    
    Args:
        dict1: The base dictionary
        dict2: The dictionary to merge into dict1
        
    Returns:
        A new dictionary with merged values
        
    Example:
        >>> d1 = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> d2 = {"b": {"c": 4, "e": 5}, "f": 6}
        >>> deep_merge(d1, d2)
        {"a": 1, "b": {"c": 4, "d": 3, "e": 5}, "f": 6}
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def deep_diff(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """
    Compare two dictionaries and return the differences.
    
    Args:
        dict1: The first dictionary
        dict2: The second dictionary
        
    Returns:
        A dictionary containing the differences with keys:
        - "added": keys present in dict2 but not dict1
        - "removed": keys present in dict1 but not dict2  
        - "modified": keys present in both but with different values
        - "unchanged": keys present in both with same values
        
    Example:
        >>> d1 = {"a": 1, "b": 2, "c": {"x": 1}}
        >>> d2 = {"a": 1, "b": 3, "d": 4, "c": {"x": 2}}
        >>> deep_diff(d1, d2)
        {
            "added": {"d": 4},
            "removed": {},
            "modified": {"b": {"old": 2, "new": 3}, "c": {"x": {"old": 1, "new": 2}}},
            "unchanged": {"a": 1}
        }
    """
    added: dict[str, Any] = {}
    removed: dict[str, Any] = {}
    modified: dict[str, Any] = {}
    unchanged: dict[str, Any] = {}
    
    # Find keys in dict2 but not in dict1 (added)
    for key in dict2:
        if key not in dict1:
            added[key] = dict2[key]
    
    # Find keys in dict1 but not in dict2 (removed)
    for key in dict1:
        if key not in dict2:
            removed[key] = dict1[key]
    
    # Compare common keys
    for key in dict1:
        if key in dict2:
            val1, val2 = dict1[key], dict2[key]
            
            if isinstance(val1, dict) and isinstance(val2, dict):
                # Recursively diff nested dictionaries
                nested_diff = deep_diff(val1, val2)
                if any(nested_diff[k] for k in ["added", "removed", "modified"]):
                    modified[key] = nested_diff
                else:
                    unchanged[key] = val1
            elif val1 == val2:
                unchanged[key] = val1
            else:
                modified[key] = {"old": val1, "new": val2}
    
    return {
        "added": added,
        "removed": removed,
        "modified": modified,
        "unchanged": unchanged
    }