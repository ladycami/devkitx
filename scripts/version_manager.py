#!/usr/bin/env python3
"""
Version management script for devtools-py package.

This script handles semantic versioning operations:
- Bump major, minor, or patch versions
- Update version in pyproject.toml
- Create git tags for releases
- Validate version format
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Tuple


class VersionManager:
    """Manages semantic versioning for the package."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.version_pattern = re.compile(r'^version = "(\d+)\.(\d+)\.(\d+)"$')
    
    def get_current_version(self) -> Tuple[int, int, int]:
        """Get current version from pyproject.toml."""
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.pyproject_path}")
        
        content = self.pyproject_path.read_text()
        
        for line in content.splitlines():
            match = self.version_pattern.match(line.strip())
            if match:
                major, minor, patch = map(int, match.groups())
                return major, minor, patch
        
        raise ValueError("Version not found in pyproject.toml")
    
    def set_version(self, major: int, minor: int, patch: int) -> None:
        """Update version in pyproject.toml."""
        content = self.pyproject_path.read_text()
        new_version = f'version = "{major}.{minor}.{patch}"'
        
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if self.version_pattern.match(line.strip()):
                lines[i] = new_version
                break
        else:
            raise ValueError("Version line not found in pyproject.toml")
        
        self.pyproject_path.write_text('\n'.join(lines) + '\n')
        print(f"✅ Updated version to {major}.{minor}.{patch}")
    
    def bump_version(self, bump_type: str) -> Tuple[int, int, int]:
        """Bump version according to semantic versioning rules."""
        major, minor, patch = self.get_current_version()
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")
        
        self.set_version(major, minor, patch)
        return major, minor, patch
    
    def create_git_tag(self, version: str, message: str = None) -> bool:
        """Create a git tag for the version."""
        tag_name = f"v{version}"
        
        if message is None:
            message = f"Release version {version}"
        
        try:
            # Check if tag already exists
            result = subprocess.run(
                ["git", "tag", "-l", tag_name],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.stdout.strip():
                print(f"⚠️  Tag {tag_name} already exists")
                return False
            
            # Create the tag
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", message],
                check=True,
                cwd=self.project_root
            )
            
            print(f"✅ Created git tag {tag_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create git tag: {e}")
            return False
    
    def validate_version_format(self, version: str) -> bool:
        """Validate semantic version format."""
        pattern = re.compile(r'^\d+\.\d+\.\d+$')
        return bool(pattern.match(version))


def main():
    """Main function for version management CLI."""
    parser = argparse.ArgumentParser(
        description="Manage semantic versioning for devtools-py package"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Current version command
    subparsers.add_parser("current", help="Show current version")
    
    # Bump version command
    bump_parser = subparsers.add_parser("bump", help="Bump version")
    bump_parser.add_argument(
        "type",
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    bump_parser.add_argument(
        "--tag",
        action="store_true",
        help="Create git tag after bumping"
    )
    bump_parser.add_argument(
        "--message",
        help="Custom tag message"
    )
    
    # Set version command
    set_parser = subparsers.add_parser("set", help="Set specific version")
    set_parser.add_argument("version", help="Version to set (e.g., 1.2.3)")
    set_parser.add_argument(
        "--tag",
        action="store_true",
        help="Create git tag after setting"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize version manager
    project_root = Path(__file__).parent.parent
    vm = VersionManager(project_root)
    
    try:
        if args.command == "current":
            major, minor, patch = vm.get_current_version()
            print(f"Current version: {major}.{minor}.{patch}")
            
        elif args.command == "bump":
            major, minor, patch = vm.bump_version(args.type)
            version_str = f"{major}.{minor}.{patch}"
            
            if args.tag:
                vm.create_git_tag(version_str, args.message)
                
        elif args.command == "set":
            if not vm.validate_version_format(args.version):
                print(f"❌ Invalid version format: {args.version}")
                print("Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)")
                return 1
            
            major, minor, patch = map(int, args.version.split('.'))
            vm.set_version(major, minor, patch)
            
            if args.tag:
                vm.create_git_tag(args.version)
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())