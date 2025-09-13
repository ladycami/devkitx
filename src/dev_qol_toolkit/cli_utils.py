from __future__ import annotations

import argparse
from typing import Any, Callable


def parse_args(schema: dict[str, Any]) -> argparse.Namespace:
    """
    Tiny wrapper around argparse.
    schema example:
      {
        "--input": str,
        "--count": (int, 3),
        "--verbose": bool,
      }
    """
    parser = argparse.ArgumentParser()
    for opt, spec in schema.items():
        if isinstance(spec, tuple) and len(spec) == 2:
            tp, default = spec
            if tp is bool:
                parser.add_argument(opt, action="store_true", default=bool(default))
            else:
                parser.add_argument(opt, type=tp, default=default)
        else:
            if spec is bool:
                parser.add_argument(opt, action="store_true")
            else:
                parser.add_argument(opt, type=spec)
    return parser.parse_args()


def confirm(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        resp = input(f"{prompt} {suffix} ").strip().lower()
        if not resp:
            return default
        if resp in {"y", "yes"}:
            return True
        if resp in {"n", "no"}:
            return False


def select(options: list[str], prompt: str = "Choose:") -> str:
    if not options:
        raise ValueError("options must not be empty")
    for i, opt in enumerate(options, 1):
        print(f"{i}) {opt}")
    while True:
        resp = input(f"{prompt} [1-{len(options)}] ").strip()
        if resp.isdigit():
            idx = int(resp)
            if 1 <= idx <= len(options):
                return options[idx - 1]