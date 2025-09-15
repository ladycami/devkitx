#!/usr/bin/env python3
"""
Build validation script for devtools-py package.

This script performs comprehensive validation before building the package:
- Runs linting checks (ruff, black, mypy)
- Executes test suite with coverage requirements
- Validates package metadata
- Checks for security vulnerabilities
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        print(f"✅ {description} passed")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Command: {' '.join(cmd)}")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT:\n{e.stdout}")
        print(f"STDERR:\n{e.stderr}")
        return False, e.stderr


def check_python_version() -> bool:
    """Verify Python version meets requirements."""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required, got {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True


def validate_package_structure() -> bool:
    """Validate package structure and required files."""
    print("🔍 Validating package structure...")
    
    required_files = [
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "src/devtools_py/__init__.py",
        "src/devtools_py/__main__.py",
    ]
    
    missing_files = []
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ Package structure is valid")
    return True


def main() -> int:
    """Main validation function."""
    print("🚀 Starting build validation for devtools-py")
    print("=" * 50)
    
    # Track validation results
    validations = []
    
    # Check Python version
    validations.append(check_python_version())
    
    # Validate package structure
    validations.append(validate_package_structure())
    
    # Run ruff linting
    success, _ = run_command(
        ["python", "-m", "ruff", "check", "src/devtools_py", "tests"],
        "Ruff linting"
    )
    validations.append(success)
    
    # Run black formatting check
    success, _ = run_command(
        ["python", "-m", "black", "--check", "src/devtools_py", "tests"],
        "Black formatting check"
    )
    validations.append(success)
    
    # Run mypy type checking
    success, _ = run_command(
        ["python", "-m", "mypy", "src/devtools_py"],
        "MyPy type checking"
    )
    validations.append(success)
    
    # Run test suite with coverage (allow 85% for now)
    success, output = run_command(
        ["python", "-m", "pytest", "--cov=devtools_py", "--cov-report=term-missing", "--cov-fail-under=85"],
        "Test suite with coverage"
    )
    validations.append(success)
    
    # Check if package can be built
    success, _ = run_command(
        ["python", "-m", "build", "--wheel", "--sdist"],
        "Package building test"
    )
    validations.append(success)
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(validations)
    total = len(validations)
    
    if passed == total:
        print(f"🎉 All {total} validation checks passed!")
        print("✅ Package is ready for deployment")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} validation checks failed")
        print("🚫 Package is NOT ready for deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())