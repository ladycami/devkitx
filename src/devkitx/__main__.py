from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import (
    json_utils,
    file_utils,
    string_utils,
    config_utils,
    system_utils,
    security_utils,
    time_utils,
    validation_utils,
)


def add_json_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add JSON-related CLI commands."""
    json_parser = subparsers.add_parser("json", help="JSON utilities")
    json_sub = json_parser.add_subparsers(dest="json_cmd", required=True)

    # Flatten JSON command
    flatten_parser = json_sub.add_parser("flatten", help="Flatten JSON file to stdout")
    flatten_parser.add_argument("path", type=Path, help="Path to JSON file")

    # Pretty print JSON command
    pretty_parser = json_sub.add_parser("pretty", help="Pretty print JSON file")
    pretty_parser.add_argument("path", type=Path, help="Path to JSON file")


def add_file_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add file-related CLI commands."""
    file_parser = subparsers.add_parser("file", help="File utilities")
    file_sub = file_parser.add_subparsers(dest="file_cmd", required=True)

    # Find file command
    find_parser = file_sub.add_parser("find", help="Find files by name under a root directory")
    find_parser.add_argument("name", help="Filename or glob pattern")
    find_parser.add_argument(
        "--root", type=Path, default=Path("."), help="Root directory to search"
    )


def add_string_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add string manipulation CLI commands."""
    string_parser = subparsers.add_parser("string", help="String manipulation utilities")
    string_sub = string_parser.add_subparsers(dest="string_cmd", required=True)

    # Case conversion command
    convert_parser = string_sub.add_parser("convert", help="Convert string case")
    convert_parser.add_argument("text", help="Text to convert")
    convert_parser.add_argument(
        "--to",
        choices=["snake", "camel", "pascal", "kebab"],
        required=True,
        help="Target case format",
    )

    # Validation command
    validate_parser = string_sub.add_parser("validate", help="Validate string format")
    validate_parser.add_argument("text", help="Text to validate")
    validate_parser.add_argument(
        "--type", choices=["email", "url"], required=True, help="Validation type"
    )

    # Sanitize command
    sanitize_parser = string_sub.add_parser("sanitize", help="Sanitize filename")
    sanitize_parser.add_argument("filename", help="Filename to sanitize")


def add_config_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add configuration management CLI commands."""
    config_parser = subparsers.add_parser("config", help="Configuration management utilities")
    config_sub = config_parser.add_subparsers(dest="config_cmd", required=True)

    # Load config command
    load_parser = config_sub.add_parser("load", help="Load and display configuration")
    load_parser.add_argument("path", type=Path, help="Path to configuration file")
    load_parser.add_argument(
        "--format",
        choices=["json", "yaml", "toml", "env"],
        help="Configuration format (auto-detected if not specified)",
    )

    # Merge configs command
    merge_parser = config_sub.add_parser("merge", help="Merge multiple configuration files")
    merge_parser.add_argument("files", nargs="+", type=Path, help="Configuration files to merge")
    merge_parser.add_argument("--output", type=Path, help="Output file (stdout if not specified)")


def add_system_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add system utilities CLI commands."""
    system_parser = subparsers.add_parser("system", help="System utilities")
    system_sub = system_parser.add_subparsers(dest="system_cmd", required=True)

    # System info command
    info_parser = system_sub.add_parser("info", help="Display system information")
    info_parser.add_argument(
        "--format", choices=["json", "table"], default="table", help="Output format"
    )

    # Run command
    run_parser = system_sub.add_parser("run", help="Run system command with timeout")
    run_parser.add_argument("cmd", nargs="+", help="Command to run")
    run_parser.add_argument("--timeout", type=float, help="Timeout in seconds")

    # Find executable command
    find_exec_parser = system_sub.add_parser("find-exec", help="Find executable in PATH")
    find_exec_parser.add_argument("name", help="Executable name")


def add_security_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add security utilities CLI commands."""
    security_parser = subparsers.add_parser("security", help="Security utilities")
    security_sub = security_parser.add_subparsers(dest="security_cmd", required=True)

    # Hash command
    hash_parser = security_sub.add_parser("hash", help="Hash data")
    hash_parser.add_argument("data", help="Data to hash")
    hash_parser.add_argument(
        "--algorithm", choices=["sha256", "sha512", "md5"], default="sha256", help="Hash algorithm"
    )

    # Generate secret command
    secret_parser = security_sub.add_parser("generate-secret", help="Generate secret key")
    secret_parser.add_argument("--length", type=int, default=32, help="Secret length")

    # Generate UUID command
    security_sub.add_parser("generate-uuid", help="Generate UUID")


def add_time_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add time utilities CLI commands."""
    time_parser = subparsers.add_parser("time", help="Time utilities")
    time_sub = time_parser.add_subparsers(dest="time_cmd", required=True)

    # Parse date command
    parse_parser = time_sub.add_parser("parse", help="Parse date string")
    parse_parser.add_argument("date_string", help="Date string to parse")
    parse_parser.add_argument("--format", help="Expected date format")

    # Format duration command
    duration_parser = time_sub.add_parser("duration", help="Format duration")
    duration_parser.add_argument("seconds", type=float, help="Duration in seconds")

    # Business day command
    business_parser = time_sub.add_parser("business-day", help="Check if date is business day")
    business_parser.add_argument("date", help="Date to check (YYYY-MM-DD)")


def add_validation_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add validation utilities CLI commands."""
    validation_parser = subparsers.add_parser("validate", help="Validation utilities")
    validation_sub = validation_parser.add_subparsers(dest="validation_cmd", required=True)

    # Range validation command
    range_parser = validation_sub.add_parser("range", help="Validate number range")
    range_parser.add_argument("value", type=float, help="Value to validate")
    range_parser.add_argument("--min", type=float, required=True, help="Minimum value")
    range_parser.add_argument("--max", type=float, required=True, help="Maximum value")

    # Length validation command
    length_parser = validation_sub.add_parser("length", help="Validate string length")
    length_parser.add_argument("text", help="Text to validate")
    length_parser.add_argument("--min", type=int, default=0, help="Minimum length")
    length_parser.add_argument("--max", type=int, help="Maximum length")


def execute_json_commands(args: argparse.Namespace) -> int:
    """Execute JSON-related commands."""
    if args.json_cmd == "flatten":
        data = json_utils.load_json(args.path)
        print(json_utils.pretty_json(json_utils.flatten_json(data)))
        return 0
    elif args.json_cmd == "pretty":
        data = json_utils.load_json(args.path)
        print(json_utils.pretty_json(data))
        return 0
    return 1


def execute_file_commands(args: argparse.Namespace) -> int:
    """Execute file-related commands."""
    if args.file_cmd == "find":
        for p in file_utils.find_file(args.name, args.root):
            print(p)
        return 0
    return 1


def execute_string_commands(args: argparse.Namespace) -> int:
    """Execute string manipulation commands."""
    if args.string_cmd == "convert":
        text = args.text
        if args.to == "snake":
            result = string_utils.to_snake_case(text)
        elif args.to == "camel":
            result = string_utils.to_camel_case(text)
        elif args.to == "pascal":
            result = string_utils.to_pascal_case(text)
        elif args.to == "kebab":
            result = string_utils.to_kebab_case(text)
        else:
            return 1
        print(result)
        return 0
    elif args.string_cmd == "validate":
        text = args.text
        if args.type == "email":
            result = string_utils.validate_email(text)
        elif args.type == "url":
            result = string_utils.validate_url(text)
        else:
            return 1
        print("Valid" if result else "Invalid")
        return 0
    elif args.string_cmd == "sanitize":
        result = string_utils.sanitize_filename(args.filename)
        print(result)
        return 0
    return 1


def execute_config_commands(args: argparse.Namespace) -> int:
    """Execute configuration management commands."""
    if args.config_cmd == "load":
        try:
            if args.format == "json" or (not args.format and args.path.suffix == ".json"):
                data = json_utils.load_json(args.path)
            elif args.format == "yaml" or (
                not args.format and args.path.suffix in [".yaml", ".yml"]
            ):
                data = config_utils.load_yaml_config(args.path)
            elif args.format == "toml" or (not args.format and args.path.suffix == ".toml"):
                data = config_utils.load_toml_config(args.path)
            elif args.format == "env" or (not args.format and args.path.suffix == ".env"):
                data = config_utils.load_dotenv(args.path)
            else:
                print(f"Unsupported format or file extension: {args.path.suffix}")
                return 1
            print(json_utils.pretty_json(data))
            return 0
        except Exception as e:
            print(f"Error loading config: {e}")
            return 1
    elif args.config_cmd == "merge":
        try:
            merged = {}
            for file_path in args.files:
                if file_path.suffix == ".json":
                    data = json_utils.load_json(file_path)
                elif file_path.suffix in [".yaml", ".yml"]:
                    data = config_utils.load_yaml_config(file_path)
                elif file_path.suffix == ".toml":
                    data = config_utils.load_toml_config(file_path)
                else:
                    print(f"Unsupported file format: {file_path}")
                    return 1

                # Import data_utils for deep_merge
                from . import data_utils

                merged = data_utils.deep_merge(merged, data)

            result = json_utils.pretty_json(merged)
            if args.output:
                args.output.write_text(result)
                print(f"Merged configuration saved to {args.output}")
            else:
                print(result)
            return 0
        except Exception as e:
            print(f"Error merging configs: {e}")
            return 1
    return 1


def execute_system_commands(args: argparse.Namespace) -> int:
    """Execute system utilities commands."""
    if args.system_cmd == "info":
        try:
            info = system_utils.get_system_info()
            python_info = system_utils.get_python_info()
            combined_info = {**info, **python_info}

            if args.format == "json":
                print(json_utils.pretty_json(combined_info))
            else:
                # Table format
                for key, value in combined_info.items():
                    print(f"{key:20}: {value}")
            return 0
        except Exception as e:
            print(f"Error getting system info: {e}")
            return 1
    elif args.system_cmd == "run":
        try:
            result = system_utils.run_command(args.cmd, timeout=args.timeout)
            print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}", file=sys.stderr)
            return result.returncode
        except Exception as e:
            print(f"Error running command: {e}")
            return 1
    elif args.system_cmd == "find-exec":
        try:
            path = system_utils.find_executable(args.name)
            if path:
                print(path)
                return 0
            else:
                print(f"Executable '{args.name}' not found")
                return 1
        except Exception as e:
            print(f"Error finding executable: {e}")
            return 1
    return 1


def execute_security_commands(args: argparse.Namespace) -> int:
    """Execute security utilities commands."""
    if args.security_cmd == "hash":
        try:
            result = security_utils.hash_data(args.data, args.algorithm)
            print(result)
            return 0
        except Exception as e:
            print(f"Error hashing data: {e}")
            return 1
    elif args.security_cmd == "generate-secret":
        try:
            secret = security_utils.generate_secret_key(args.length)
            print(secret)
            return 0
        except Exception as e:
            print(f"Error generating secret: {e}")
            return 1
    elif args.security_cmd == "generate-uuid":
        try:
            uuid = security_utils.generate_uuid()
            print(uuid)
            return 0
        except Exception as e:
            print(f"Error generating UUID: {e}")
            return 1
    return 1


def execute_time_commands(args: argparse.Namespace) -> int:
    """Execute time utilities commands."""
    if args.time_cmd == "parse":
        try:
            formats = [args.format] if args.format else None
            parsed_date = time_utils.parse_date(args.date_string, formats)
            print(parsed_date.isoformat())
            return 0
        except Exception as e:
            print(f"Error parsing date: {e}")
            return 1
    elif args.time_cmd == "duration":
        try:
            formatted = time_utils.format_duration(args.seconds)
            print(formatted)
            return 0
        except Exception as e:
            print(f"Error formatting duration: {e}")
            return 1
    elif args.time_cmd == "business-day":
        try:
            from datetime import datetime

            date = datetime.fromisoformat(args.date)
            is_business = time_utils.is_business_day(date)
            print("Yes" if is_business else "No")
            return 0
        except Exception as e:
            print(f"Error checking business day: {e}")
            return 1
    return 1


def execute_validation_commands(args: argparse.Namespace) -> int:
    """Execute validation utilities commands."""
    if args.validation_cmd == "range":
        try:
            is_valid = validation_utils.validate_range(args.value, args.min, args.max)
            print("Valid" if is_valid else "Invalid")
            return 0
        except Exception as e:
            print(f"Error validating range: {e}")
            return 1
    elif args.validation_cmd == "length":
        try:
            is_valid = validation_utils.validate_length(args.text, args.min, args.max)
            print("Valid" if is_valid else "Invalid")
            return 0
        except Exception as e:
            print(f"Error validating length: {e}")
            return 1
    return 1


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point with command categories."""
    parser = argparse.ArgumentParser(
        prog="devkitx", description="Comprehensive developer quality-of-life utilities"
    )
    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Available command categories"
    )

    # Register all command categories
    add_json_commands(subparsers)
    add_file_commands(subparsers)
    add_string_commands(subparsers)
    add_config_commands(subparsers)
    add_system_commands(subparsers)
    add_security_commands(subparsers)
    add_time_commands(subparsers)
    add_validation_commands(subparsers)

    args = parser.parse_args(argv)

    # Execute commands based on category
    try:
        if args.command == "json":
            return execute_json_commands(args)
        elif args.command == "file":
            return execute_file_commands(args)
        elif args.command == "string":
            return execute_string_commands(args)
        elif args.command == "config":
            return execute_config_commands(args)
        elif args.command == "system":
            return execute_system_commands(args)
        elif args.command == "security":
            return execute_security_commands(args)
        elif args.command == "time":
            return execute_time_commands(args)
        elif args.command == "validate":
            return execute_validation_commands(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
