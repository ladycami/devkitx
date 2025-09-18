from __future__ import annotations

import argparse
import getpass
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator, TypeVar

from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.text import Text

T = TypeVar("T")


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


def password_prompt(prompt: str, confirm: bool = False) -> str:
    """
    Prompt for a password with optional confirmation.

    Args:
        prompt: The prompt message to display
        confirm: Whether to ask for password confirmation

    Returns:
        The entered password

    Raises:
        ValueError: If confirmation passwords don't match

    Example:
        >>> password = password_prompt("Enter password:")
        >>> password = password_prompt("Enter new password:", confirm=True)
    """
    password = getpass.getpass(f"{prompt} ")

    if confirm:
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            raise ValueError("Passwords do not match")

    return password


def multi_select(options: list[str], prompt: str = "Select multiple:") -> list[str]:
    """
    Allow selection of multiple options from a list.

    Args:
        options: List of options to choose from
        prompt: The prompt message to display

    Returns:
        List of selected options

    Raises:
        ValueError: If options list is empty

    Example:
        >>> selected = multi_select(["option1", "option2", "option3"])
        >>> selected = multi_select(["red", "green", "blue"], "Pick colors:")
    """
    if not options:
        raise ValueError("options must not be empty")

    print(f"\n{prompt}")
    print("Enter numbers separated by commas (e.g., 1,3,5) or 'all' for all options:")

    for i, opt in enumerate(options, 1):
        print(f"{i}) {opt}")

    while True:
        resp = input(f"Selection [1-{len(options)}]: ").strip().lower()

        if resp == "all":
            return options.copy()

        if not resp:
            continue

        try:
            # Parse comma-separated numbers
            indices = [int(x.strip()) for x in resp.split(",") if x.strip()]

            # Validate all indices are in range
            if all(1 <= idx <= len(options) for idx in indices):
                # Remove duplicates while preserving order
                unique_indices = []
                seen = set()
                for idx in indices:
                    if idx not in seen:
                        unique_indices.append(idx)
                        seen.add(idx)

                return [options[idx - 1] for idx in unique_indices]
            else:
                print(f"Please enter numbers between 1 and {len(options)}")

        except ValueError:
            print("Please enter valid numbers separated by commas")


def progress_bar(iterable: Iterator[T], desc: str = "", total: int | None = None) -> Iterator[T]:
    """
    Wrap an iterable with a progress bar.

    Args:
        iterable: The iterable to wrap
        desc: Description to show with the progress bar
        total: Total number of items (if known)

    Yields:
        Items from the original iterable

    Example:
        >>> for item in progress_bar(range(100), "Processing"):
        ...     # Do work with item
        ...     pass
    """
    console = Console()

    # Convert to list if we need to determine length
    if total is None:
        try:
            # Try to get length without consuming iterator
            total = len(iterable)  # type: ignore
        except TypeError:
            # If no length available, convert to list
            items = list(iterable)
            total = len(items)
            iterable = iter(items)

    with Progress(console=console) as progress:
        task = progress.add_task(desc or "Processing...", total=total)

        for item in iterable:
            yield item
            progress.advance(task)


@contextmanager
def spinner(message: str = "Processing..."):
    """
    Display a spinner while code is executing.

    Args:
        message: Message to display with the spinner

    Example:
        >>> with spinner("Loading data..."):
        ...     # Do some work
        ...     time.sleep(2)
    """
    console = Console()

    # Simple spinner implementation using threading
    stop_spinner = threading.Event()
    spinner_chars = "|/-\\"

    def spin():
        idx = 0
        while not stop_spinner.is_set():
            console.print(f"\r{spinner_chars[idx % len(spinner_chars)]} {message}", end="")
            idx += 1
            time.sleep(0.1)
        console.print(f"\r✓ {message}")

    spinner_thread = threading.Thread(target=spin)
    spinner_thread.daemon = True
    spinner_thread.start()

    try:
        yield
    finally:
        stop_spinner.set()
        spinner_thread.join(timeout=0.5)


def colored_text(text: str, color: str, bold: bool = False) -> str:
    """
    Return colored text for terminal output.

    Args:
        text: The text to color
        color: Color name (red, green, blue, yellow, magenta, cyan, white, black)
        bold: Whether to make the text bold

    Returns:
        Formatted text string

    Example:
        >>> print(colored_text("Success!", "green", bold=True))
        >>> print(colored_text("Warning", "yellow"))
    """
    # Use console with force_terminal=True to ensure ANSI codes are included
    console = Console(force_terminal=True, width=200)

    style = color
    if bold:
        style = f"bold {color}"

    # Create a Text object and render it to string
    rich_text = Text(text, style=style)

    # Use console to render the text with markup
    with console.capture() as capture:
        console.print(rich_text, end="")

    return capture.get()


def table_format(data: list[dict[str, Any]], headers: list[str] | None = None) -> str:
    """
    Format data as a table.

    Args:
        data: List of dictionaries representing table rows
        headers: Optional list of column headers (uses dict keys if not provided)

    Returns:
        Formatted table as string

    Example:
        >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        >>> print(table_format(data))
        >>> print(table_format(data, headers=["Name", "Age"]))
    """
    if not data:
        return ""

    console = Console()

    # Determine headers and create mapping
    if headers is None:
        headers = list(data[0].keys())
        key_mapping = {h: h for h in headers}
    else:
        # If custom headers provided, map them to original keys
        original_keys = list(data[0].keys())
        key_mapping = {}
        for i, header in enumerate(headers):
            if i < len(original_keys):
                key_mapping[header] = original_keys[i]
            else:
                key_mapping[header] = header

    # Create table
    table = Table()

    # Add columns
    for header in headers:
        table.add_column(header, style="cyan")

    # Add rows
    for row in data:
        row_values = []
        for header in headers:
            # Use the mapping to get the correct key from the data
            data_key = key_mapping[header]
            value = row.get(data_key, "")
            row_values.append(str(value))
        table.add_row(*row_values)

    # Render table to string
    with console.capture() as capture:
        console.print(table)

    return capture.get()
