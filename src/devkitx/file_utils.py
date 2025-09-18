"""File system utilities for DevKitX.

This module provides utilities for file operations, directory management,
and file system queries with enhanced error handling.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def find_file(name_or_pattern: str, root: str | Path = ".") -> list[Path]:
    """Find files by exact name or glob pattern recursively.

    Args:
        name_or_pattern: Exact filename or glob pattern to search for
        root: Root directory to search from

    Returns:
        List of matching file paths, sorted alphabetically

    Examples:
        >>> find_file("settings.py", ".")
        [PosixPath('./config/settings.py')]
        >>> find_file("*.json", "src")
        [PosixPath('src/config.json'), PosixPath('src/data.json')]
        >>> find_file("README.md")  # Case-insensitive fallback
        [PosixPath('./readme.md')]
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
    """Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path to create

    Returns:
        Path object for the created directory

    Raises:
        PermissionError: If lacking permissions to create directory
        OSError: If unable to create directory for other reasons

    Examples:
        >>> ensure_dir("output/data")
        PosixPath('output/data')
        >>> ensure_dir(Path("logs"))
        PosixPath('logs')
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def is_readable(path: str | Path) -> bool:
    """Check if file or directory is readable.

    Args:
        path: Path to check for read access

    Returns:
        True if path exists and is readable, False otherwise

    Examples:
        >>> is_readable("config.json")
        True
        >>> is_readable("/root/secret.txt")  # May be False due to permissions
        False
        >>> is_readable("nonexistent.txt")
        False
    """
    p = Path(path)
    try:
        return p.exists() and os.access(p, os.R_OK)
    except Exception:
        return False


def is_writable(path: str | Path) -> bool:
    """Check if file or directory is writable.

    For existing files, checks write permissions on the file.
    For non-existing files, checks write permissions on the parent directory.

    Args:
        path: Path to check for write access

    Returns:
        True if path is writable, False otherwise

    Examples:
        >>> is_writable("output.txt")
        True
        >>> is_writable("/etc/hosts")  # May be False due to permissions
        False
        >>> is_writable("new_file.txt")  # Checks parent directory permissions
        True
    """
    p = Path(path)
    try:
        if p.exists():
            return os.access(p, os.W_OK)
        # check parent
        return os.access(p.parent, os.W_OK)
    except Exception:
        return False


def atomic_write(path: str | Path, data: bytes | str) -> Path:
    """Write data to file atomically using temporary file.

    Writes to a temporary file first, then atomically moves it to the target
    location. This prevents partial writes and corruption if the process is
    interrupted.

    Args:
        path: Target file path
        data: Data to write (string or bytes)

    Returns:
        Path object for the written file

    Raises:
        PermissionError: If lacking write permissions
        OSError: If unable to create temporary file or move it

    Examples:
        >>> atomic_write("config.json", '{"key": "value"}')
        PosixPath('config.json')
        >>> atomic_write("data.bin", b"binary data")
        PosixPath('data.bin')
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
    """Find all files with given extension recursively.

    Args:
        root: Root directory to search from
        ext: File extension (with or without leading dot)

    Returns:
        List of matching file paths, sorted alphabetically

    Examples:
        >>> glob_ext("src", "py")
        [PosixPath('src/main.py'), PosixPath('src/utils.py')]
        >>> glob_ext("data", ".json")
        [PosixPath('data/config.json'), PosixPath('data/users.json')]
        >>> glob_ext(Path("docs"), "md")
        [PosixPath('docs/README.md'), PosixPath('docs/guide.md')]
    """
    e = ext if ext.startswith(".") else f".{ext}"
    return sorted(Path(root).rglob(f"*{e}"))


def copy_file(src: str | Path, dst: str | Path, overwrite: bool = True) -> Path:
    """Copy file from source to destination.

    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Whether to overwrite existing destination file

    Returns:
        Path object for the destination file

    Raises:
        FileNotFoundError: If source file doesn't exist
        FileExistsError: If destination exists and overwrite is False
        PermissionError: If lacking read/write permissions
        OSError: If unable to create parent directories

    Examples:
        >>> copy_file("source.txt", "backup.txt")
        PosixPath('backup.txt')
        >>> copy_file("data.json", "archive/data.json")
        PosixPath('archive/data.json')
        >>> copy_file("file.txt", "existing.txt", overwrite=False)
        Traceback (most recent call last):
        ...
        FileExistsError: existing.txt
    """
    src_p, dst_p = Path(src), Path(dst)
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    if dst_p.exists() and not overwrite:
        raise FileExistsError(dst_p)
    shutil.copy2(src_p, dst_p)
    return dst_p
