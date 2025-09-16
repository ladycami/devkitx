#!/usr/bin/env python3
"""
PyPI deployment script for devtools-py.

This script handles the deployment of the package to PyPI using twine.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def check_prerequisites():
    """Check that all prerequisites are met for deployment."""
    print("🔍 Checking deployment prerequisites...")
    
    # Check if twine is installed
    exit_code, stdout, stderr = run_command(["python", "-m", "twine", "--version"])
    if exit_code != 0:
        print("❌ twine is not installed. Install with: pip install twine")
        return False
    
    print(f"✅ twine is available: {stdout.strip()}")
    
    # Check if dist files exist
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory not found. Run 'python -m build' first.")
        return False
    
    wheel_files = list(dist_dir.glob("*.whl"))
    tar_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files or not tar_files:
        print("❌ Missing distribution files. Run 'python -m build' first.")
        return False
    
    print(f"✅ Found distribution files: {len(wheel_files)} wheel(s), {len(tar_files)} source dist(s)")
    
    # Check if .pypirc exists (optional)
    pypirc_path = Path.home() / ".pypirc"
    if pypirc_path.exists():
        print("✅ Found .pypirc configuration file")
    else:
        print("⚠️  No .pypirc found. You'll need to provide credentials manually.")
    
    return True


def validate_package():
    """Validate the package before upload."""
    print("\n🔍 Validating package...")
    
    # Check package with twine
    exit_code, stdout, stderr = run_command([
        "python", "-m", "twine", "check", "dist/*"
    ])
    
    if exit_code != 0:
        print(f"❌ Package validation failed: {stderr}")
        return False
    
    print("✅ Package validation passed")
    return True


def upload_to_testpypi():
    """Upload to TestPyPI first for testing."""
    print("\n🚀 Uploading to TestPyPI...")
    
    # Load environment variables
    test_pypi_token = os.getenv("TEST_PYPI_TOKEN")
    if not test_pypi_token:
        print("❌ TEST_PYPI_TOKEN not found in environment")
        return False
    
    exit_code, stdout, stderr = run_command([
        "python", "-m", "twine", "upload", 
        "--repository", "testpypi",
        "--username", "__token__",
        "--password", test_pypi_token,
        "dist/*"
    ])
    
    if exit_code != 0:
        print(f"❌ TestPyPI upload failed: {stderr}")
        return False
    
    print("✅ Successfully uploaded to TestPyPI")
    print("🔗 Check your package at: https://test.pypi.org/project/devtools-py/")
    return True


def upload_to_pypi():
    """Upload to production PyPI."""
    print("\n🚀 Uploading to PyPI...")
    
    # Confirm with user
    response = input("Are you sure you want to upload to production PyPI? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Deployment cancelled by user")
        return False
    
    # Load environment variables
    pypi_token = os.getenv("PYPI_TOKEN")
    if not pypi_token:
        print("❌ PYPI_TOKEN not found in environment")
        return False
    
    exit_code, stdout, stderr = run_command([
        "python", "-m", "twine", "upload",
        "--username", "__token__",
        "--password", pypi_token,
        "dist/*"
    ])
    
    if exit_code != 0:
        print(f"❌ PyPI upload failed: {stderr}")
        return False
    
    print("✅ Successfully uploaded to PyPI")
    print("🔗 Check your package at: https://pypi.org/project/devtools-py/")
    return True


def verify_deployment():
    """Verify that the package can be installed from PyPI."""
    print("\n🔍 Verifying deployment...")
    
    # Try to install from PyPI
    print("Testing installation from PyPI...")
    exit_code, stdout, stderr = run_command([
        "pip", "install", "--index-url", "https://pypi.org/simple/", 
        "--no-deps", "devtools-py==1.0.0"
    ])
    
    if exit_code != 0:
        print(f"⚠️  Could not verify installation: {stderr}")
        print("This might be normal if the package is still propagating.")
        return True  # Don't fail on this
    
    print("✅ Package can be installed from PyPI")
    return True


def main():
    """Main deployment function."""
    print("🚀 Starting PyPI deployment for devtools-py v1.0.0")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Validate package
    if not validate_package():
        return 1
    
    # Ask user which deployment method to use
    print("\nDeployment options:")
    print("1. Deploy to TestPyPI only (recommended for testing)")
    print("2. Deploy to TestPyPI then PyPI (full deployment)")
    print("3. Deploy directly to PyPI (production only)")
    
    choice = input("Choose deployment option (1-3): ").strip()
    
    if choice == "1":
        # TestPyPI only
        if not upload_to_testpypi():
            return 1
    elif choice == "2":
        # TestPyPI then PyPI
        if not upload_to_testpypi():
            return 1
        
        input("\nPress Enter to continue with PyPI deployment...")
        
        if not upload_to_pypi():
            return 1
        
        if not verify_deployment():
            return 1
    elif choice == "3":
        # PyPI only
        if not upload_to_pypi():
            return 1
        
        if not verify_deployment():
            return 1
    else:
        print("❌ Invalid choice")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Deployment completed successfully!")
    
    if choice in ["2", "3"]:
        print("\n📦 Your package is now available on PyPI:")
        print("   pip install devtools-py")
        print("\n📚 Package page: https://pypi.org/project/devtools-py/")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())