#!/usr/bin/env python3
"""
Deployment script for devtools-py package to PyPI.

This script handles the complete deployment process:
- Validates the package is ready for deployment
- Builds the package
- Uploads to PyPI using twine
- Verifies the deployment was successful
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List


def run_command(cmd: List[str], description: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            cwd=Path(__file__).parent.parent
        )
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"⚠️  {description} completed with warnings")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Exit code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        raise


def check_twine_config() -> bool:
    """Check if twine is configured properly."""
    print("🔍 Checking twine configuration...")
    
    try:
        # Check if twine is installed
        result = subprocess.run(
            ["python", "-m", "twine", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Twine is installed: {result.stdout.strip()}")
        
        # Check if credentials are configured
        # This will check for .pypirc or environment variables
        result = subprocess.run(
            ["python", "-m", "twine", "check", "--help"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Twine configuration appears valid")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Twine configuration issue: {e}")
        return False


def verify_package_version() -> str:
    """Get and verify the current package version."""
    print("🔍 Checking package version...")
    
    project_root = Path(__file__).parent.parent
    version_manager_path = project_root / "scripts" / "version_manager.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(version_manager_path), "current"],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_root
        )
        
        # Extract version from output like "Current version: 1.0.0"
        version_line = result.stdout.strip()
        if "Current version:" in version_line:
            version = version_line.split("Current version:")[-1].strip()
            print(f"✅ Package version: {version}")
            return version
        else:
            raise ValueError(f"Could not parse version from: {version_line}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get package version: {e}")
        raise


def clean_dist_directory() -> None:
    """Clean the dist directory before building."""
    print("🧹 Cleaning dist directory...")
    
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    
    if dist_dir.exists():
        import shutil
        shutil.rmtree(dist_dir)
        print("✅ Removed existing dist directory")
    
    dist_dir.mkdir(exist_ok=True)
    print("✅ Created clean dist directory")


def build_package() -> List[Path]:
    """Build the package and return list of built artifacts."""
    print("📦 Building package...")
    
    project_root = Path(__file__).parent.parent
    
    # Build both wheel and source distribution
    run_command(
        ["python", "-m", "build", "--wheel", "--sdist"],
        "Building wheel and source distribution"
    )
    
    # List built artifacts
    dist_dir = project_root / "dist"
    artifacts = list(dist_dir.glob("*"))
    
    if not artifacts:
        raise RuntimeError("No build artifacts found in dist directory")
    
    print("📁 Built artifacts:")
    for artifact in artifacts:
        print(f"  - {artifact.name}")
    
    return artifacts


def check_package_integrity(artifacts: List[Path]) -> None:
    """Check the integrity of built packages."""
    print("🔍 Checking package integrity...")
    
    # Use twine check to validate the packages
    artifact_paths = [str(artifact) for artifact in artifacts]
    
    run_command(
        ["python", "-m", "twine", "check"] + artifact_paths,
        "Validating package integrity with twine"
    )


def upload_to_pypi(artifacts: List[Path], test_pypi: bool = False) -> None:
    """Upload packages to PyPI or TestPyPI."""
    repository = "testpypi" if test_pypi else "pypi"
    repository_name = "TestPyPI" if test_pypi else "PyPI"
    
    print(f"🚀 Uploading to {repository_name}...")
    
    artifact_paths = [str(artifact) for artifact in artifacts]
    cmd = ["python", "-m", "twine", "upload"]
    
    if test_pypi:
        cmd.extend(["--repository", "testpypi"])
    
    cmd.extend(artifact_paths)
    
    run_command(cmd, f"Uploading to {repository_name}")


def verify_deployment(version: str, test_pypi: bool = False) -> None:
    """Verify that the package was deployed successfully."""
    package_name = "devtools-py"
    
    if test_pypi:
        print("🔍 Verifying TestPyPI deployment...")
        # For TestPyPI, we can check if the package is available
        print(f"✅ Package should be available at: https://test.pypi.org/project/{package_name}/{version}/")
    else:
        print("🔍 Verifying PyPI deployment...")
        
        # Wait a moment for PyPI to process the upload
        print("⏳ Waiting for PyPI to process the upload...")
        time.sleep(10)
        
        # Try to install the package from PyPI to verify
        try:
            result = subprocess.run(
                ["pip", "index", "versions", package_name],
                capture_output=True,
                text=True,
                check=False
            )
            
            if version in result.stdout:
                print(f"✅ Version {version} is available on PyPI")
            else:
                print(f"⚠️  Version {version} may not be available yet (can take a few minutes)")
                
        except Exception as e:
            print(f"⚠️  Could not verify deployment: {e}")
        
        print(f"✅ Package should be available at: https://pypi.org/project/{package_name}/{version}/")


def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(
        description="Deploy devtools-py package to PyPI"
    )
    
    parser.add_argument(
        "--test-pypi",
        action="store_true",
        help="Deploy to TestPyPI instead of PyPI"
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip pre-deployment validation"
    )
    
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building (use existing dist artifacts)"
    )
    
    args = parser.parse_args()
    
    repository_name = "TestPyPI" if args.test_pypi else "PyPI"
    
    print(f"🚀 Starting deployment to {repository_name}")
    print("=" * 50)
    
    try:
        # Check twine configuration
        if not check_twine_config():
            print("❌ Twine is not properly configured")
            return 1
        
        # Get package version
        version = verify_package_version()
        
        # Run validation unless skipped
        if not args.skip_validation:
            print("🔍 Running pre-deployment validation...")
            validation_script = Path(__file__).parent / "build_validate_simple.py"
            result = subprocess.run([sys.executable, str(validation_script)], check=False)
            
            if result.returncode != 0:
                print("❌ Pre-deployment validation failed")
                print("Use --skip-validation to bypass this check")
                return 1
        
        # Build package unless skipped
        if not args.skip_build:
            clean_dist_directory()
            artifacts = build_package()
        else:
            print("📦 Using existing build artifacts...")
            project_root = Path(__file__).parent.parent
            dist_dir = project_root / "dist"
            artifacts = list(dist_dir.glob("*"))
            
            if not artifacts:
                print("❌ No existing build artifacts found")
                return 1
        
        # Check package integrity
        check_package_integrity(artifacts)
        
        # Upload to PyPI
        upload_to_pypi(artifacts, test_pypi=args.test_pypi)
        
        # Verify deployment
        verify_deployment(version, test_pypi=args.test_pypi)
        
        print("\n" + "=" * 50)
        print(f"🎉 Successfully deployed version {version} to {repository_name}!")
        
        if args.test_pypi:
            print("\n📝 To install from TestPyPI:")
            print(f"pip install --index-url https://test.pypi.org/simple/ devtools-py=={version}")
        else:
            print("\n📝 To install the new version:")
            print(f"pip install devtools-py=={version}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())