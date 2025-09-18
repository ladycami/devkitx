"""JSON utilities for DevKitX.

This module provides utilities for loading, saving, and manipulating JSON data
with enhanced error handling and formatting options.
"""

from .flatten import flatten_json, unflatten_json

# Import other functions from the legacy json_utils module for backward compatibility
# We need to import from the parent directory where the legacy json_utils.py file exists
from pathlib import Path

# Get the parent directory (src/devkitx) and add it to path temporarily
parent_dir = Path(__file__).parent.parent
legacy_module_path = parent_dir / "json_utils.py"

if legacy_module_path.exists():
    # Import the legacy module
    import importlib.util
    spec = importlib.util.spec_from_file_location("legacy_json_utils", legacy_module_path)
    if spec and spec.loader:
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        
        # Re-export the functions from the legacy module
        load_json = legacy_module.load_json
        save_json = legacy_module.save_json
        pretty_json = legacy_module.pretty_json
        detect_jsonl = legacy_module.detect_jsonl
        # Note: we override the flatten_json from legacy with our new implementation
        # unflatten_json is also from our new implementation

__all__ = [
    "flatten_json",
    "unflatten_json",
    "load_json", 
    "save_json",
    "pretty_json",
    "detect_jsonl",
]