from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterable


def find_file(name_or_pattern: str, root: str | Path = ".") -> list[Path]:
    """
    Find files by exact name or glob pattern, under root (recursive).
    Examples:
      find_file("settings.py", ".")
      find_file("*.json", "src")
    """
    root_path = Path(root)
    if any(ch in name_or_pattern for ch in "*?[]"):
        return sorted(root_path.rglob(name_or_pattern))
    # exact name match, case-sensitive then case-insensitive fallback
    exact = [p for p in root_path.rglob("*") if p.is_file() and p.name == name_or_pattern]
    if exact:
        return sorted(exact)
    lowered = name_or_pattern.lower()
    return sorted(p for p in root_path.rglob("*") if p.is_file() and p.name.lower() == lowered)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_readable(path: str | Path) -> bool:
    p = Path(path)
    try:
        return p.exists() and os.access(p, os.R_OK)
    except Exception:
        return False


def is_writable(path: str | Path) -> bool:
    p = Path(path)
    try:
        if p.exists():
            return os.access(p, os.W_OK)
        # check parent
        return os.access(p.parent, os.W_OK)
    except Exception:
        return False


def atomic_write(path: str | Path, data: bytes | str) -> Path:
    """
    Write to a temp file and atomically move into place.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(data, (bytes, bytearray)) else "w"
    with tempfile.NamedTemporaryFile(delete=False, dir=target.parent) as tf:
        tmp_path = Path(tf.name)
        with tmp_path.open(mode, encoding=None if "b" in mode else "utf-8") as f:
            f.write(data)  # type: ignore[arg-type]
    os.replace(tmp_path, target)
    return target


def glob_ext(root: str | Path, ext: str) -> list[Path]:
    """
    Return files under root with given extension, ext may be 'json' or '.json'.
    """
    e = ext if ext.startswith(".") else f".{ext}"
    return sorted(Path(root).rglob(f"*{e}"))


def copy_file(src: str | Path, dst: str | Path, overwrite: bool = True) -> Path:
    src_p, dst_p = Path(src), Path(dst)
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    if dst_p.exists() and not overwrite:
        raise FileExistsError(dst_p)
    shutil.copy2(src_p, dst_p)
    return dst_p