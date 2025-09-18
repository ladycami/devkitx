"""JSON utilities for DevKitX.

This module provides utilities for loading, saving, and manipulating JSON data
with enhanced error handling and formatting options.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> dict:
    """Load JSON data from file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        PermissionError: If lacking read permissions

    Examples:
        >>> data = load_json("config.json")
        >>> data = load_json(Path("data/settings.json"))
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str | Path, *, pretty: bool = True) -> None:
    """Save data to JSON file.

    Args:
        data: Data to save as JSON
        path: Path to save JSON file
        pretty: Whether to format JSON with indentation and sorting

    Raises:
        PermissionError: If lacking write permissions
        OSError: If unable to create parent directories
        TypeError: If data is not JSON serializable

    Examples:
        >>> save_json({"name": "John", "age": 30}, "user.json")
        >>> save_json([1, 2, 3], "numbers.json", pretty=False)
        >>> save_json(data, Path("output/result.json"))
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        else:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def pretty_json(data: Any, *, color: bool = False) -> str:
    """Format data as pretty-printed JSON string.

    Args:
        data: Data to format as JSON
        color: Whether to add syntax highlighting (requires pygments)

    Returns:
        Pretty-formatted JSON string

    Raises:
        TypeError: If data is not JSON serializable

    Examples:
        >>> data = {"name": "John", "items": [1, 2, 3]}
        >>> print(pretty_json(data))
        {
          "items": [
            1,
            2,
            3
          ],
          "name": "John"
        }
        >>> colored = pretty_json(data, color=True)  # Adds syntax highlighting
    """
    s = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    if not color:
        return s
    try:
        # Optional colorization if pygments is present (no hard dep)
        from pygments import highlight  # type: ignore
        from pygments.formatters import TerminalFormatter  # type: ignore
        from pygments.lexers import JsonLexer  # type: ignore

        return highlight(s, JsonLexer(), TerminalFormatter())
    except Exception:
        return s


def detect_jsonl(path: str | Path, *, sample: int = 10) -> bool:
    """Detect if file contains JSON Lines (NDJSON) format.

    Args:
        path: Path to file to check
        sample: Number of lines to sample for detection

    Returns:
        True if file appears to be JSON Lines format, False otherwise

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If lacking read permissions

    Examples:
        >>> detect_jsonl("data.jsonl")
        True
        >>> detect_jsonl("regular.json")
        False
        >>> detect_jsonl("mixed.txt", sample=5)  # Check first 5 lines
        False
    """
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= sample:
                break
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError:
                return False
    return True


def flatten_json(obj: dict, sep: str = ".") -> dict[str, Any]:
    """Flatten nested JSON object into dot-notation keys.

    Args:
        obj: Dictionary to flatten
        sep: Separator to use between nested keys

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
    """
    out: dict[str, Any] = {}

    def _rec(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                _rec(f"{prefix}{k}{sep}" if prefix else f"{k}{sep}", v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _rec(f"{prefix}{i}{sep}", v)
        else:
            key = prefix[: -len(sep)] if prefix.endswith(sep) else prefix
            out[key] = value

    _rec("", obj)
    return out


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
