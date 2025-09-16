#!/usr/bin/env python3
"""
CLI demonstration script for devkitx.

This script demonstrates the command-line interface functionality
by running various CLI commands programmatically.
"""

import subprocess
import sys
from pathlib import Path


def run_cli_command(args: list[str]) -> tuple[int, str, str]:
    """Run a CLI command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            ["devkitx"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def demo_cli_commands():
    """Demonstrate various CLI commands."""
    print("🖥️ DEVKITX CLI DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Test cases: [description, command_args, expected_in_output]
    test_cases = [
        # String utilities
        ("String case conversion (snake)", 
         ["string", "convert", "--to", "snake", "MyVariableName"], 
         "my_variable_name"),
        
        ("String case conversion (pascal)", 
         ["string", "convert", "--to", "pascal", "my_variable_name"], 
         "MyVariableName"),
        
        ("String case conversion (kebab)", 
         ["string", "convert", "--to", "kebab", "MyVariableName"], 
         "my-variable-name"),
        
        ("Email validation (valid)", 
         ["string", "validate", "--type", "email", "user@example.com"], 
         "Valid"),
        
        ("Email validation (invalid)", 
         ["string", "validate", "--type", "email", "invalid-email"], 
         "Invalid"),
        
        ("URL validation (valid)", 
         ["string", "validate", "--type", "url", "https://github.com"], 
         "Valid"),
        
        ("String sanitization", 
         ["string", "sanitize", "my/file:name?.txt"], 
         "my_file_name_.txt"),
        
        # Security utilities
        ("Data hashing", 
         ["security", "hash", "test_data"], 
         None),  # Just check it runs successfully
        
        ("Secret generation", 
         ["security", "generate-secret", "--length", "16"], 
         None),  # Just check it runs successfully
        
        ("UUID generation", 
         ["security", "generate-uuid"], 
         None),  # Just check it runs successfully
        
        # System utilities
        ("System information", 
         ["system", "info"], 
         "os_name"),
        
        ("Find executable", 
         ["system", "find-exec", "python"], 
         "python"),
        
        # Time utilities
        ("Date parsing", 
         ["time", "parse", "2024-01-15 14:30:00"], 
         "2024-01-15T14:30:00"),
        
        ("Duration formatting", 
         ["time", "duration", "3661"], 
         "1h 1m 1.0s"),
        
        ("Business day check", 
         ["time", "business-day", "2024-01-15"], 
         "Yes"),  # Monday
        
        # Validation utilities
        ("Range validation (valid)", 
         ["validate", "range", "25", "--min", "18", "--max", "65"], 
         "Valid"),
        
        ("Range validation (invalid)", 
         ["validate", "range", "10", "--min", "18", "--max", "65"], 
         "Invalid"),
        
        ("Length validation", 
         ["validate", "length", "hello", "--min", "3", "--max", "10"], 
         "Valid"),
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for description, args, expected in test_cases:
        print(f"Testing: {description}")
        print(f"Command: devkitx {' '.join(args)}")
        
        exit_code, stdout, stderr = run_cli_command(args)
        
        if exit_code == 0:
            if expected is None or expected in stdout:
                print(f"✅ SUCCESS")
                if stdout.strip():
                    print(f"   Output: {stdout.strip()}")
                successful_tests += 1
            else:
                print(f"❌ FAILED - Expected '{expected}' in output")
                print(f"   Got: {stdout.strip()}")
        else:
            print(f"❌ FAILED - Exit code: {exit_code}")
            if stderr:
                print(f"   Error: {stderr.strip()}")
        
        print()
    
    print("=" * 60)
    print(f"CLI TESTS SUMMARY: {successful_tests}/{total_tests} passed")
    
    if successful_tests == total_tests:
        print("🎉 ALL CLI TESTS PASSED!")
    else:
        print(f"⚠️  {total_tests - successful_tests} tests failed")
    
    return successful_tests == total_tests


def demo_help_commands():
    """Demonstrate help commands."""
    print("\n📚 HELP COMMANDS DEMONSTRATION")
    print("=" * 60)
    
    help_commands = [
        (["--help"], "Main help"),
        (["string", "--help"], "String utilities help"),
        (["security", "--help"], "Security utilities help"),
        (["system", "--help"], "System utilities help"),
        (["time", "--help"], "Time utilities help"),
        (["validate", "--help"], "Validation utilities help"),
    ]
    
    for args, description in help_commands:
        print(f"\n{description}:")
        print(f"Command: devkitx {' '.join(args)}")
        
        exit_code, stdout, stderr = run_cli_command(args)
        
        if exit_code == 0:
            # Show first few lines of help
            lines = stdout.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(stdout.split('\n')) > 5:
                print("   ...")
        else:
            print(f"   ❌ Failed to get help: {stderr}")


def main():
    """Main demonstration function."""
    print("Starting CLI demonstration...")
    print("Make sure devkitx is installed: pip install devkitx")
    print()
    
    # Check if devkitx is available
    exit_code, stdout, stderr = run_cli_command(["--version"])
    if exit_code != 0:
        # Try with --help instead
        exit_code, stdout, stderr = run_cli_command(["--help"])
        if exit_code != 0:
            print("❌ devkitx CLI not found. Please install with: pip install devkitx")
            return 1
    
    # Run demonstrations
    success = demo_cli_commands()
    demo_help_commands()
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 CLI DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("All devkitx CLI commands are working perfectly!")
    else:
        print("⚠️  Some CLI tests failed. Check the output above for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())