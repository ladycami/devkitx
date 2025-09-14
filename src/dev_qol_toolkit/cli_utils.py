from __future__ import annotations

import argparse
import getpass
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