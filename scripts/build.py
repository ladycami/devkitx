#!/usr/bin/env python3
"""
Main build script for devtools-py package.

This script orchestrates the complete build process:
- Validates the codebase
- Builds the package
- Optionally bumps version and creates tags
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_name: str, args: list[str] = None) -> int:
    """Run a Python script and return its exit code."""
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)]
    
    if args:
        cmd.extend(args)
    
    print(f"🔧 Running {script_name}...")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(
        description="Build devtools-py package with validation"
    )
    
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation checks"
    )
    
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="Bump version before building"
    )
    
    parser.add_argument(
        "--tag",
        action="store_true",
        help="Create git tag (requires --bump)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building"
    )
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    
    print("🚀 Starting devtools-py build process")
    print("=" * 50)
    
    # Clean build artifacts if requested
    if args.clean:
        print("🧹 Cleaning build artifacts...")
        dist_dir = project_root / "dist"
        build_dir = project_root / "build"
        
        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
            print("✅ Removed dist/ directory")
        
        if build_dir.exists():
            import shutil
            shutil.rmtree(build_dir)
            print("✅ Removed build/ directory")
    
    # Bump version if requested
    if args.bump:
        print(f"📈 Bumping {args.bump} version...")
        version_args = ["bump", args.bump]
        if args.tag:
            version_args.append("--tag")
        
        exit_code = run_script("version_manager.py", version_args)
        if exit_code != 0:
            print("❌ Version bump failed")
            return exit_code
    
    # Run validation unless skipped
    if not args.skip_validation:
        print("🔍 Running validation checks...")
        exit_code = run_script("build_validate.py")
        if exit_code != 0:
            print("❌ Validation failed - build aborted")
            return exit_code
    else:
        print("⚠️  Skipping validation checks")
    
    # Build the package
    print("📦 Building package...")
    try:
        subprocess.run(
            [sys.executable, "-m", "build"],
            check=True,
            cwd=project_root
        )
        print("✅ Package built successfully")
        
        # Show build artifacts
        dist_dir = project_root / "dist"
        if dist_dir.exists():
            artifacts = list(dist_dir.glob("*"))
            if artifacts:
                print("\n📁 Build artifacts:")
                for artifact in artifacts:
                    print(f"  - {artifact.name}")
        
        print("\n🎉 Build completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Package build failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())