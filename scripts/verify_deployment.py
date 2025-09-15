#!/usr/bin/env python3
"""
Deployment verification script for devtools-py package.

This script verifies that a deployed package works correctly:
- Installs the package in a clean environment
- Tests basic functionality
- Verifies all modules can be imported
- Runs basic CLI commands
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import List


def run_command_in_venv(venv_path: Path, cmd: List[str], description: str) -> subprocess.CompletedProcess:
    """Run a command in the virtual environment."""
    print(f"🔧 {description}...")
    
    # Determine the correct python executable path
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    # Replace 'python' with the venv python path
    if cmd[0] == "python":
        cmd[0] = str(python_exe)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise


def create_test_environment() -> Path:
    """Create a clean virtual environment for testing."""
    print("🏗️  Creating clean test environment...")
    
    temp_dir = Path(tempfile.mkdtemp(prefix="devtools_py_test_"))
    venv_path = temp_dir / "test_venv"
    
    # Create virtual environment
    venv.create(venv_path, with_pip=True)
    
    print(f"✅ Created test environment at {venv_path}")
    return venv_path


def install_package(venv_path: Path, version: str = None, test_pypi: bool = False) -> None:
    """Install the package in the test environment."""
    package_spec = "devtools-py"
    if version:
        package_spec += f"=={version}"
    
    cmd = ["python", "-m", "pip", "install"]
    
    if test_pypi:
        cmd.extend(["--index-url", "https://test.pypi.org/simple/"])
        cmd.extend(["--extra-index-url", "https://pypi.org/simple/"])  # For dependencies
    
    cmd.append(package_spec)
    
    repository = "TestPyPI" if test_pypi else "PyPI"
    run_command_in_venv(venv_path, cmd, f"Installing {package_spec} from {repository}")


def test_imports(venv_path: Path) -> None:
    """Test that all modules can be imported."""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        "devtools_py",
        "devtools_py.json_utils",
        "devtools_py.file_utils",
        "devtools_py.string_utils",
        "devtools_py.config_utils",
        "devtools_py.system_utils",
        "devtools_py.security_utils",
        "devtools_py.time_utils",
        "devtools_py.validation_utils",
        "devtools_py.data_utils",
        "devtools_py.async_utils",
        "devtools_py.dev_utils",
        "devtools_py.cli_utils",
        "devtools_py.http_utils",
        "devtools_py.log_utils",
    ]
    
    for module in modules_to_test:
        cmd = ["python", "-c", f"import {module}; print(f'✅ {module} imported successfully')"]
        run_command_in_venv(venv_path, cmd, f"Importing {module}")


def test_cli_commands(venv_path: Path) -> None:
    """Test basic CLI functionality."""
    print("🔍 Testing CLI commands...")
    
    # Test help command
    run_command_in_venv(
        venv_path,
        ["python", "-m", "devtools_py", "--help"],
        "Testing CLI help command"
    )
    
    # Test version command (if available)
    try:
        run_command_in_venv(
            venv_path,
            ["python", "-m", "devtools_py", "--version"],
            "Testing CLI version command"
        )
    except subprocess.CalledProcessError:
        print("ℹ️  Version command not available (this is okay)")
    
    # Test a simple string command
    run_command_in_venv(
        venv_path,
        ["python", "-m", "devtools_py", "string", "convert", "--to", "snake", "TestString"],
        "Testing string conversion CLI command"
    )
    
    # Test system info command
    run_command_in_venv(
        venv_path,
        ["python", "-m", "devtools_py", "system", "info"],
        "Testing system info CLI command"
    )


def test_basic_functionality(venv_path: Path) -> None:
    """Test basic package functionality."""
    print("🔍 Testing basic functionality...")
    
    test_script = '''
import devtools_py.json_utils as json_utils
import devtools_py.string_utils as string_utils
import devtools_py.security_utils as security_utils
import tempfile
import json
from pathlib import Path

# Test JSON utilities
test_data = {"name": "test", "value": 123}
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    temp_file = Path(f.name)

json_utils.save_json(test_data, temp_file)
loaded_data = json_utils.load_json(temp_file)
assert loaded_data == test_data
print("✅ JSON utilities working")

# Test string utilities
snake_case = string_utils.to_snake_case("TestString")
assert snake_case == "test_string"
print("✅ String utilities working")

# Test security utilities
secret = security_utils.generate_secret_key(16)
assert len(secret) > 0
print("✅ Security utilities working")

# Clean up
temp_file.unlink()

print("🎉 All basic functionality tests passed!")
'''
    
    cmd = ["python", "-c", test_script]
    run_command_in_venv(venv_path, cmd, "Running basic functionality tests")


def cleanup_test_environment(venv_path: Path) -> None:
    """Clean up the test environment."""
    print("🧹 Cleaning up test environment...")
    
    import shutil
    shutil.rmtree(venv_path.parent)
    
    print("✅ Test environment cleaned up")


def main():
    """Main verification function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify devtools-py package deployment"
    )
    
    parser.add_argument(
        "--version",
        help="Specific version to test (default: latest)"
    )
    
    parser.add_argument(
        "--test-pypi",
        action="store_true",
        help="Test installation from TestPyPI"
    )
    
    parser.add_argument(
        "--keep-env",
        action="store_true",
        help="Keep test environment after verification"
    )
    
    args = parser.parse_args()
    
    repository = "TestPyPI" if args.test_pypi else "PyPI"
    version_info = f" (version {args.version})" if args.version else ""
    
    print(f"🚀 Starting deployment verification for devtools-py{version_info}")
    print(f"📦 Testing installation from {repository}")
    print("=" * 60)
    
    venv_path = None
    
    try:
        # Create test environment
        venv_path = create_test_environment()
        
        # Install package
        install_package(venv_path, args.version, args.test_pypi)
        
        # Test imports
        test_imports(venv_path)
        
        # Test CLI commands
        test_cli_commands(venv_path)
        
        # Test basic functionality
        test_basic_functionality(venv_path)
        
        print("\n" + "=" * 60)
        print("🎉 All verification tests passed!")
        print("✅ Package deployment is working correctly")
        
        if args.keep_env:
            print(f"🏗️  Test environment preserved at: {venv_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return 1
        
    finally:
        if venv_path and not args.keep_env:
            try:
                cleanup_test_environment(venv_path)
            except Exception as e:
                print(f"⚠️  Failed to clean up test environment: {e}")


if __name__ == "__main__":
    sys.exit(main())