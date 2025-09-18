#!/usr/bin/env python3
"""
Release verification script for devtools-py.

This script verifies that the built package is ready for deployment.
"""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def verify_package_build():
    """Verify that the package builds correctly."""
    print("🔍 Verifying package build...")
    
    # Check if dist files exist
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory not found")
        return False
    
    wheel_files = list(dist_dir.glob("*.whl"))
    tar_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files:
        print("❌ No wheel files found in dist/")
        return False
    
    if not tar_files:
        print("❌ No source distribution files found in dist/")
        return False
    
    print(f"✅ Found wheel: {wheel_files[0].name}")
    print(f"✅ Found source dist: {tar_files[0].name}")
    return True


def verify_package_installation():
    """Verify that the package can be installed and imported."""
    print("\n🔍 Verifying package installation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        venv_path = temp_path / "test_venv"
        
        # Create virtual environment
        print("Creating test virtual environment...")
        venv.create(venv_path, with_pip=True)
        
        # Get paths
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"
        
        # Install the package
        wheel_file = next(Path("dist").glob("*.whl"))
        print(f"Installing {wheel_file.name}...")
        
        exit_code, stdout, stderr = run_command([
            str(pip_exe), "install", str(wheel_file)
        ])
        
        if exit_code != 0:
            print(f"❌ Installation failed: {stderr}")
            return False
        
        # Test import
        print("Testing package import...")
        exit_code, stdout, stderr = run_command([
            str(python_exe), "-c", "import devkitx; print('Import successful')"
        ])
        
        if exit_code != 0:
            print(f"❌ Import failed: {stderr}")
            return False
        
        print("✅ Package imports successfully")
        
        # Test CLI
        print("Testing CLI functionality...")
        exit_code, stdout, stderr = run_command([
            str(python_exe), "-m", "devkitx", "--help"
        ])
        
        if exit_code != 0:
            print(f"❌ CLI test failed: {stderr}")
            return False
        
        if "devtools-py" not in stdout:
            print("❌ CLI help output doesn't contain expected content")
            return False
        
        print("✅ CLI works correctly")
        
        # Test a simple command
        print("Testing CLI command...")
        exit_code, stdout, stderr = run_command([
            str(python_exe), "-m", "devkitx", "string", "convert", "--to", "snake", "TestString"
        ])
        
        if exit_code != 0:
            print(f"❌ CLI command failed: {stderr}")
            return False
        
        if "test_string" not in stdout:
            print(f"❌ CLI command output unexpected: {stdout}")
            return False
        
        print("✅ CLI commands work correctly")
        
    return True


def verify_metadata():
    """Verify package metadata."""
    print("\n🔍 Verifying package metadata...")
    
    # Check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return False
    
    content = pyproject_path.read_text()
    
    # Check required fields
    required_fields = [
        'name = "devtools-py"',
        'version = "1.0.0"',
        'description =',
        'readme = "README.md"',
        'license =',
        'authors =',
        'requires-python = ">=3.10"'
    ]
    
    for field in required_fields:
        if field not in content:
            print(f"❌ Missing required field in pyproject.toml: {field}")
            return False
    
    print("✅ Package metadata is complete")
    
    # Check README exists
    if not Path("README.md").exists():
        print("❌ README.md not found")
        return False
    
    print("✅ README.md exists")
    
    # Check LICENSE exists
    if not Path("LICENSE").exists():
        print("❌ LICENSE file not found")
        return False
    
    print("✅ LICENSE file exists")
    
    return True


def main():
    """Main verification function."""
    print("🚀 Starting release verification for devtools-py v1.0.0")
    print("=" * 60)
    
    success = True
    
    # Run all verification steps
    if not verify_metadata():
        success = False
    
    if not verify_package_build():
        success = False
    
    if not verify_package_installation():
        success = False
    
    print("\n" + "=" * 60)
    
    if success:
        print("🎉 All verification checks passed!")
        print("📦 Package is ready for deployment to PyPI")
        return 0
    else:
        print("❌ Some verification checks failed")
        print("🔧 Please fix the issues before deploying")
        return 1


if __name__ == "__main__":
    sys.exit(main())