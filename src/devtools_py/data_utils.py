"""Data manipulation utilities for DevKitX.

This module provides utilities for data processing, transformation,
and manipulation including case conversion, list operations, and
dictionary utilities.
"""

from __future__ import annotations

import re
from typing import Any


_CAMEL_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_2 = re.compile(r"([a-z0-9])([A-Z])")


def to_snake(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case.

    Args:
        name: String to convert

    Returns:
        String in snake_case format

    Examples:
        >>> to_snake("camelCase")
        'camel_case'
        >>> to_snake("PascalCase")
        'pascal_case'
        >>> to_snake("XMLHttpRequest")
        'xml_http_request'
    """
    s1 = _CAMEL_1.sub(r"\1_\2", name)
    return _CAMEL_2.sub(r"\1_\2", s1).lower()


def to_camel(name: str) -> str:
    """Convert snake_case, kebab-case, or space-separated to camelCase.

    Args:
        name: String to convert

    Returns:
        String in camelCase format

    Examples:
        >>> to_camel("snake_case")
        'snakeCase'
        >>> to_camel("kebab-case")
        'kebabCase'
        >>> to_camel("space separated")
        'spaceSeparated'
    """
    parts = re.split(r"[_\-\s]+", name)
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def chunk_list(lst: list[Any], size: int) -> list[list[Any]]:
    """Split list into chunks of specified size.

    Args:
        lst: List to split into chunks
        size: Size of each chunk

    Returns:
        List of chunks (sublists)

    Raises:
        ValueError: If size is less than or equal to 0

    Examples:
        >>> chunk_list([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
        >>> chunk_list(['a', 'b', 'c', 'd'], 3)
        [['a', 'b', 'c'], ['d']]
        >>> chunk_list([], 2)
        []
    """
    if size <= 0:
        raise ValueError("size must be > 0")
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten_list(lst: list[list[Any]]) -> list[Any]:
    """Flatten a list of lists into a single list.

    Args:
        lst: List of lists to flatten

    Returns:
        Flattened list containing all elements

    Examples:
        >>> flatten_list([[1, 2], [3, 4], [5]])
        [1, 2, 3, 4, 5]
        >>> flatten_list([['a', 'b'], ['c']])
        ['a', 'b', 'c']
        >>> flatten_list([])
        []
    """
    out: list[Any] = []
    for sub in lst:
        out.extend(sub)
    return out


def deep_get(d: dict, keys: list[str], default: Any = None) -> Any:
    """Get value from nested dictionary using list of keys.

    Args:
        d: Dictionary to search in
        keys: List of keys representing the path to the value
        default: Default value to return if path doesn't exist

    Returns:
        Value at the specified path, or default if not found

    Examples:
        >>> data = {"user": {"profile": {"name": "John"}}}
        >>> deep_get(data, ["user", "profile", "name"])
        'John'
        >>> deep_get(data, ["user", "settings", "theme"], "default")
        'default'
        >>> deep_get(data, ["nonexistent"])
        None
    """
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

    return {"added": added, "removed": removed, "modified": modified, "unchanged": unchanged}


def group_by(items: list[Any], key_func: callable) -> dict[Any, list[Any]]:
    """
    Group items in a list by the result of a key function.

    Args:
        items: List of items to group
        key_func: Function that takes an item and returns a grouping key

    Returns:
        Dictionary where keys are the grouping keys and values are lists of items

    Example:
        >>> items = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 25}, {"name": "Charlie", "age": 30}]
        >>> group_by(items, lambda x: x["age"])
        {25: [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 25}], 30: [{"name": "Charlie", "age": 30}]}
    """
    groups: dict[Any, list[Any]] = {}

    for item in items:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)

    return groups


def filter_dict(d: dict[str, Any], predicate: callable) -> dict[str, Any]:
    """
    Filter dictionary items based on a predicate function.

    Args:
        d: Dictionary to filter
        predicate: Function that takes (key, value) and returns True to keep the item

    Returns:
        New dictionary containing only items that match the predicate

    Example:
        >>> data = {"a": 1, "b": 2, "c": 3, "d": 4}
        >>> filter_dict(data, lambda k, v: v > 2)
        {"c": 3, "d": 4}
    """
    return {key: value for key, value in d.items() if predicate(key, value)}


def transform_values(d: dict[str, Any], transformer: callable) -> dict[str, Any]:
    """
    Transform all values in a dictionary using a transformer function.

    Args:
        d: Dictionary to transform
        transformer: Function that takes a value and returns the transformed value

    Returns:
        New dictionary with transformed values

    Example:
        >>> data = {"a": 1, "b": 2, "c": 3}
        >>> transform_values(data, lambda x: x * 2)
        {"a": 2, "b": 4, "c": 6}
    """
    return {key: transformer(value) for key, value in d.items()}
