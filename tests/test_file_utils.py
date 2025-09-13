from __future__ import annotations
from dev_qol_toolkit import file_utils
from pathlib import Path

def test_atomic_write(tmp_path: Path):
    p = tmp_path / "x.txt"
    file_utils.atomic_write(p, "hello")
    assert p.read_text() == "hello"