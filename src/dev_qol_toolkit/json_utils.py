from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


def load_json(path: str | Path) -> dict:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, path: str | Path, *, pretty: bool = True) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write("\n")
        else:
            json.dump(data, f, ensure_ascii=False, separators=(",", ":"))


def pretty_json(data: Any, *, color: bool = False) -> str:
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
    """Return True if file looks like JSON Lines (NDJSON)."""
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
    out: dict[str, Any] = {}

    def _rec(prefix: str, value: Any) -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                _rec(f"{prefix}{k}{sep}" if prefix else f"{k}{sep}", v)
        elif isinstance(value, list):
            for i, v in enumerate(value):
                _rec(f"{prefix}{i}{sep}", v)
        else:
            key = prefix[:-len(sep)] if prefix.endswith(sep) else prefix
            out[key] = value

    _rec("", obj)
    return out


def unflatten_json(flat: dict[str, Any], sep: str = ".") -> dict[str, Any]:
    root: dict[str, Any] = {}
    for k, v in flat.items():
        parts: Iterable[str] = k.split(sep) if k else []
        cur: Any = root
        prev: Any = None
        prev_key: str | None = None
        for i, part in enumerate(parts):
            is_last = i == len(list(parts)) - 1  # avoid re-splitting below
        # re-split once
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