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