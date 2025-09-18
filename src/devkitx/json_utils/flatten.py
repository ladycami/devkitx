"""JSON flattening utilities.

This module provides functions to flatten and unflatten nested JSON-like structures
using dot-notation keys.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def flatten_json(
    obj: Mapping[str, Any] | Sequence[Any] | str | int | float | bool | None,
    sep: str = "."
) -> dict[str, Any]:
    """Flatten nested JSON-like structures into dot-notation keys.
    
    Converts nested dictionaries and lists into a flat dictionary where
    keys represent the path to each value using dot notation (or custom separator).
    
    Args:
        obj: The object to flatten (dict, list, or primitive value)
        sep: Separator to use between nested keys (default: ".")
        
    Returns:
        Flattened dictionary with dot-notation keys
        
    Examples:
        >>> nested = {"user": {"name": "John", "details": {"age": 30}}}
        >>> flatten_json(nested)
        {'user.name': 'John', 'user.details.age': 30}
        
        >>> flatten_json({"items": [1, 2, 3]})
        {'items.0': 1, 'items.1': 2, 'items.2': 3}
        
        >>> flatten_json(nested, sep="_")
        {'user_name': 'John', 'user_details_age': 30}
        
        >>> flatten_json(42)  # Primitive values
        {'': 42}
    """
    result: dict[str, Any] = {}
    
    def _walk(value: Any, prefix: str = "") -> None:
        if isinstance(value, Mapping):
            for key, val in value.items():
                new_key = f"{prefix}{sep}{key}" if prefix else str(key)
                _walk(val, new_key)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            for index, val in enumerate(value):
                new_key = f"{prefix}{sep}{index}" if prefix else str(index)
                _walk(val, new_key)
        else:
            result[prefix or ""] = value
    
    _walk(obj)
    return result


def unflatten_json(flat: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    """Unflatten dot-notation keys back into nested JSON object.

    Args:
        flat: Flattened dictionary with dot-notation keys
        sep: Separator used between nested keys

    Returns:
        Nested dictionary structure

    Raises:
        TypeError: If there are conflicting path types (dict vs list)

    Examples:
        >>> flat = {'user.name': 'John', 'user.details.age': 30}
        >>> unflatten_json(flat)
        {'user': {'name': 'John', 'details': {'age': 30}}}
        
        >>> flat = {'items.0': 1, 'items.1': 2, 'items.2': 3}
        >>> unflatten_json(flat)
        {'items': [1, 2, 3]}
        
        >>> unflatten_json({'a_b_c': 1}, sep="_")
        {'a': {'b': {'c': 1}}}
    """
    root: dict[str, Any] = {}
    for k, v in flat.items():
        parts_list = k.split(sep) if k else []
        cur = root
        for i, part in enumerate(parts_list):
            last = i == len(parts_list) - 1
            # numeric index implies list
            idx = None
            if part.isdigit():
                idx = int(part)

            if last:
                if idx is None:
                    if isinstance(cur, list):
                        raise TypeError("Cannot set dict key on a list path")
                    cur[part] = v
                else:
                    if not isinstance(cur, list):
                        raise TypeError("Cannot set list index on a dict path")
                    # grow list
                    while len(cur) <= idx:
                        cur.append(None)
                    cur[idx] = v
            else:
                nxt = None
                nxt_part = parts_list[i + 1]
                nxt_is_index = nxt_part.isdigit()
                if idx is None:
                    # dict path
                    if part not in cur or cur[part] is None:
                        cur[part] = [] if nxt_is_index else {}
                    nxt = cur[part]
                else:
                    # list path
                    if not isinstance(cur, list):
                        # initialize as list
                        raise TypeError("Unexpected structure while unflattening")
                    while len(cur) <= idx:
                        cur.append(None)
                    if cur[idx] is None:
                        cur[idx] = [] if nxt_is_index else {}
                    nxt = cur[idx]
                cur = nxt
    return root