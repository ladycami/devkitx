from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import json_utils, file_utils

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dev-qol-toolkit", description="Developer QoL helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_flat = sub.add_parser("flatten-json", help="Flatten JSON file to stdout")
    p_flat.add_argument("path", type=Path)

    p_find = sub.add_parser("find-file", help="Find files by name under a root directory")
    p_find.add_argument("name", help="Filename or glob pattern")
    p_find.add_argument("--root", type=Path, default=Path("."))

    args = parser.parse_args(argv)

    if args.cmd == "flatten-json":
        data = json_utils.load_json(args.path)
        print(json_utils.pretty_json(json_utils.flatten_json(data)))
        return 0

    if args.cmd == "find-file":
        for p in file_utils.find_file(args.name, args.root):
            print(p)
        return 0

    return 1

if __name__ == "__main__":
    raise SystemExit(main())