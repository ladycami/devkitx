#!/usr/bin/env python3
"""Publish devkitx to PyPI or TestPyPI from your machine, using tokens in .env.

The normal release path is CI: push a ``vX.Y.Z`` tag and
``.github/workflows/release.yml`` publishes with PyPI trusted publishing.
Use this script when you need to publish locally instead.

Tokens are read from ``.env`` (never committed; see ``.env.example``) in this
checkout, or in the repository's main checkout when run from a git worktree.
The file is parsed, not executed, and tokens are passed to twine through its
environment only: never on the command line and never printed.

Usage:
    python scripts/publish.py --dry-run     # build and check only
    python scripts/publish.py --test        # upload to TestPyPI
    python scripts/publish.py               # upload to PyPI

Requires the dev extra: pip install -e ".[dev]"
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

TARGETS = {
    "pypi": {
        "token_key": "PYPI_TOKEN",
        "upload_url": "https://upload.pypi.org/legacy/",
        "json_url": "https://pypi.org/pypi/devkitx/{version}/json",
    },
    "testpypi": {
        "token_key": "TEST_PYPI_TOKEN",
        "upload_url": "https://test.pypi.org/legacy/",
        "json_url": "https://test.pypi.org/pypi/devkitx/{version}/json",
    },
}
_ENV_LINE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def _run_git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    cmd = ["git", *args]
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)  # noqa: S603, S607


def git(*args: str, cwd: Path) -> str:
    result = _run_git(*args, cwd=cwd)
    if result.returncode != 0:
        fail(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def find_env_file(repo: Path) -> Path:
    """.env in this checkout, else in the main checkout (for git worktrees)."""
    candidates = [repo / ".env"]
    common = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=repo))
    candidates.append(common.parent / ".env")
    for path in candidates:
        if path.is_file():
            return path
    fail("no .env found. Copy .env.example to .env in the repo root and add your token.")
    raise AssertionError  # unreachable


def read_env(path: Path) -> dict[str, str]:
    """Parse KEY=VALUE lines without executing anything."""
    if path.stat().st_mode & 0o077:
        print(f"warning: {path} is readable by other users; run: chmod 600 {path}", file=sys.stderr)
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = _ENV_LINE.match(line)
        if match:
            key, value = match.groups()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            values[key] = value
    return values


def package_version(repo: Path) -> str:
    text = (repo / "src" / "devkitx" / "_version.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    if not match:
        fail("could not read __version__ from src/devkitx/_version.py")
        raise AssertionError
    return match.group(1)


def already_published(json_url: str) -> bool:
    # Bypass PyPI's CDN cache: a cached 404 can outlive an upload by minutes,
    # and this lookup itself would otherwise prime that cache.
    request = urllib.request.Request(
        f"{json_url}?nocache={time.time_ns()}", headers={"Cache-Control": "no-cache"}
    )
    try:
        with urllib.request.urlopen(request, timeout=20):  # noqa: S310 - fixed https URL
            return True
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return False
        fail(f"could not check {json_url}: HTTP {err.code}")
    except urllib.error.URLError as err:
        fail(f"could not check {json_url}: {err.reason}")
    return False


def preflight(repo: Path, version: str, target: str) -> None:
    if git("status", "--porcelain", cwd=repo):
        fail("working tree has uncommitted changes; commit or stash them first.")
    tags = git("tag", "--points-at", "HEAD", cwd=repo).split()
    if f"v{version}" not in tags:
        fail(f"HEAD is not tagged v{version}. Tag the release commit first.")
    if target == "pypi":
        git("fetch", "--quiet", "origin", "develop", cwd=repo)
        on_develop = _run_git("merge-base", "--is-ancestor", "HEAD", "origin/develop", cwd=repo)
        if on_develop.returncode != 0:
            fail("HEAD is not on origin/develop; only publish merged code to PyPI.")
    if already_published(TARGETS[target]["json_url"].format(version=version)):
        fail(f"devkitx {version} is already on {target}; bump the version.")


def build(repo: Path, outdir: Path) -> list[Path]:
    build_cmd = [sys.executable, "-m", "build", "--outdir", str(outdir)]
    subprocess.run(build_cmd, cwd=repo, check=True)  # noqa: S603
    files = sorted(outdir.iterdir())
    check_cmd = [sys.executable, "-m", "twine", "check", "--strict", *map(str, files)]
    subprocess.run(check_cmd, check=True)  # noqa: S603
    return files


def upload(files: list[Path], target: str, env: dict[str, str]) -> None:
    token = env.get(TARGETS[target]["token_key"], "")
    if not token.startswith("pypi-"):
        fail(f"{TARGETS[target]['token_key']} in .env is missing or is not a PyPI API token.")
    twine_env = {
        **os.environ,
        "TWINE_USERNAME": env.get("PYPI_USERNAME") or "__token__",
        "TWINE_PASSWORD": token,
        "TWINE_REPOSITORY_URL": TARGETS[target]["upload_url"],
        "TWINE_NON_INTERACTIVE": "1",
    }
    subprocess.run(  # noqa: S603
        [sys.executable, "-m", "twine", "upload", *map(str, files)], env=twine_env, check=True
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--test", action="store_true", help="upload to TestPyPI instead of PyPI")
    parser.add_argument("--dry-run", action="store_true", help="build and check only; no upload")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()

    for module in ("build", "twine"):
        if importlib.util.find_spec(module) is None:
            fail(f"'{module}' is not installed; run: pip install -e '.[dev]'")

    repo = Path(git("rev-parse", "--show-toplevel", cwd=Path.cwd()))
    target = "testpypi" if args.test else "pypi"
    version = package_version(repo)
    env: dict[str, str] = {}
    if not args.dry_run:
        env = read_env(find_env_file(repo))
        preflight(repo, version, target)
    with tempfile.TemporaryDirectory() as tmp:
        files = build(repo, Path(tmp))
        print("\nBuilt:", *(f"  {f.name}" for f in files), sep="\n")
        if args.dry_run:
            print("\nDry run: nothing uploaded.")
            return
        if not args.yes:
            answer = input(f"\nUpload devkitx {version} to {target}? Type the version to confirm: ")
            if answer.strip() != version:
                fail("not confirmed; nothing uploaded.")
        upload(files, target, env)
    print(f"\nPublished devkitx {version} to {target}.")


if __name__ == "__main__":
    main()
