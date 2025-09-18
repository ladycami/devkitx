#!/usr/bin/env python3
"""
CLI Utilities Examples

This module demonstrates practical usage of devkitx.cli_utils
including interactive prompts, progress indicators, colored output,
and argument parsing enhancements.
"""

import time
import sys
from typing import List, Dict, Any, Optional

from devkitx.cli_utils import (
    password_prompt,
    multi_select,
    progress_bar,
    spinner,
    colored_text,
    table_format,
    confirm_prompt,
    input_with_validation,
    menu_select,
    print_banner,
    print_box,
    format_columns,
    animate_text,
    create_progress_tracker
)


def interactive_prompts_examples():
    """Demonstrate interactive prompt utilities."""
    print("=== Interactive Prompts Examples ===")
    
    # Note: These examples show the API but won't actually prompt in automated runs
    print("Interactive prompt examples (API demonstration):")
    
    # Password prompt
    print("\n1. Password Prompt:")
    print("   password = password_prompt('Enter password: ')")
    print("   confirm_password = password_prompt('Confirm password: ', confirm=True)")
    
    # Confirmation prompt
    print("\n2. Confirmation Prompt:")
    print("   confirmed = confirm_prompt('Are you sure?', default=False)")
    print("   # Returns True/False based on user input")
    
    # Multi-select
    print("\n3. Multi-select:")
    options = ["Python", "JavaScript", "Go", "Rust", "Java"]
    print(f"   options = {options}")
    print("   selected = multi_select(options, 'Select languages:')")
    print("   # Returns list of selected options")
    
    # Menu select
    print("\n4. Menu Select:")
    menu_options = {
        "1": "Create new project",
        "2": "Open existing project", 
        "3": "Settings",
        "q": "Quit"
    }
    print(f"   menu_options = {menu_options}")
    print("   choice = menu_select(menu_options, 'Choose an option:')")
    
    # Input with validation
    print("\n5. Input with Validation:")
    print("   def validate_email(email):")
    print("       return '@' in email and '.' in email")
    print("   email = input_with_validation('Email: ', validate_email)")


def progress_indicators_examples():
    """Demonstrate progress indicators and animations."""
    print("\n=== Progress Indicators Examples ===")
    
    # Simple progress bar
    print("1. Simple Progress Bar:")
    items = list(range(20))
    
    print("   Processing items...")
    for item in progress_bar(items, desc="Processing"):
        time.sleep(0.05)  # Simulate work
    print("   ✓ Complete!")
    
    # Progress bar with custom format
    print("\n2. Custom Progress Bar:")
    large_items = list(range(50))
    
    for i, item in enumerate(progress_bar(large_items, desc="Downloading")):
        time.sleep(0.02)  # Simulate download
        if i % 10 == 0:  # Update every 10 items
            print(f"   Downloaded {i+1}/{len(large_items)} files")
    
    # Spinner for indeterminate progress
    print("\n3. Spinner for Indeterminate Tasks:")
    print("   Starting long-running task...")
    
    with spinner("Processing data..."):
        time.sleep(2)  # Simulate long task
    
    print("   ✓ Task completed!")
    
    # Progress tracker for multiple steps
    print("\n4. Multi-step Progress Tracker:")
    tracker = create_progress_tracker([
        "Initialize system",
        "Load configuration", 
        "Connect to database",
        "Start services",
        "Ready"
    ])
    
    for step in tracker:
        print(f"   {step}")
        time.sleep(0.5)  # Simulate step execution


def colored_output_examples():
    """Demonstrate colored text and formatting."""
    print("\n=== Colored Output Examples ===")
    
    # Basic colors
    colors = ["red", "green", "blue", "yellow", "magenta", "cyan", "white"]
    
    print("1. Basic Colors:")
    for color in colors:
        colored = colored_text(f"This is {color} text", color)
        print(f"   {colored}")
    
    # Text styles
    print("\n2. Text Styles:")
    styles = [
        ("bold", True, False, False),
        ("italic", False, True, False),
        ("underline", False, False, True),
        ("bold + italic", True, True, False),
        ("all styles", True, True, True)
    ]
    
    for name, bold, italic, underline in styles:
        styled = colored_text(f"This is {name}", "blue", bold=bold, italic=italic, underline=underline)
        print(f"   {styled}")
    
    # Status messages
    print("\n3. Status Messages:")
    statuses = [
        ("✓ Success", "green", True),
        ("⚠ Warning", "yellow", True),
        ("✗ Error", "red", True),
        ("ℹ Info", "blue", False),
        ("⏳ Processing", "cyan", False)
    ]
    
    for message, color, bold in statuses:
        status = colored_text(message, color, bold=bold)
        print(f"   {status}")


def table_formatting_examples():
    """Demonstrate table formatting utilities."""
    print("\n=== Table Formatting Examples ===")
    
    # Simple table data
    users_data = [
        {"name": "Alice", "age": 30, "department": "Engineering", "salary": 75000},
        {"name": "Bob", "age": 25, "department": "Marketing", "salary": 65000},
        {"name": "Charlie", "age": 35, "department": "Engineering", "salary": 80000},
        {"name": "Diana", "age": 28, "department": "Design", "salary": 70000}
    ]
    
    print("1. Basic Table:")
    table = table_format(users_data)
    print(table)
    
    # Custom headers
    print("\n2. Table with Custom Headers:")
    custom_headers = ["Full Name", "Age", "Dept", "Annual Salary"]
    table_custom = table_format(users_data, headers=custom_headers)
    print(table_custom)
    
    # Column formatting
    print("\n3. Formatted Columns:")
    
    # Format salary as currency
    formatted_data = []
    for user in users_data:
        formatted_user = user.copy()
        formatted_user["salary"] = f"${user['salary']:,}"
        formatted_data.append(formatted_user)
    
    table_formatted = table_format(formatted_data)
    print(table_formatted)
    
    # Column alignment
    print("\n4. Column Alignment:")
    alignment_data = [
        {"left": "Left aligned", "center": "Center", "right": "Right"},
        {"left": "Short", "center": "Medium text", "right": "Very long text here"},
        {"left": "A", "center": "B", "right": "C"}
    ]
    
    aligned_table = format_columns(alignment_data, alignments={"left": "left", "center": "center", "right": "right"})
    print(aligned_table)


def banner_and_box_examples():
    """Demonstrate banner and box formatting."""
    print("\n=== Banner and Box Examples ===")
    
    # Simple banner
    print("1. Simple Banner:")
    print_banner("Welcome to MyApp", style="simple")
    
    # Fancy banner
    print("\n2. Fancy Banner:")
    print_banner("System Status", style="fancy", color="green")
    
    # Information box
    print("\n3. Information Box:")
    info_text = """
    System Information:
    - CPU Usage: 45%
    - Memory Usage: 2.1GB / 8GB
    - Disk Space: 120GB / 500GB
    - Network: Connected
    """
    print_box(info_text.strip(), title="System Status", color="blue")
    
    # Warning box
    print("\n4. Warning Box:")
    warning_text = "Disk space is running low. Please clean up unnecessary files."
    print_box(warning_text, title="Warning", color="yellow", style="warning")
    
    # Error box
    print("\n5. Error Box:")
    error_text = "Failed to connect to database. Check connection settings."
    print_box(error_text, title="Error", color="red", style="error")


def animation_examples():
    """Demonstrate text animations and effects."""
    print("\n=== Animation Examples ===")
    
    # Typewriter effect
    print("1. Typewriter Effect:")
    animate_text("This text appears character by character...", effect="typewriter", delay=0.05)
    
    # Fade in effect
    print("\n2. Fade In Effect:")
    animate_text("This text fades in gradually", effect="fade", delay=0.1)
    
    # Loading dots animation
    print("\n3. Loading Animation:")
    loading_messages = [
        "Initializing",
        "Loading modules", 
        "Connecting to services",
        "Ready!"
    ]
    
    for message in loading_messages:
        animate_text(f"{message}...", effect="dots", delay=0.5)
        time.sleep(1)


def real_world_cli_examples():
    """Demonstrate real-world CLI application patterns."""
    print("\n=== Real-World CLI Examples ===")
    
    # Application setup wizard
    print("1. Application Setup Wizard:")
    print_banner("Application Setup", style="fancy", color="blue")
    
    setup_steps = [
        "Checking system requirements",
        "Creating configuration directory",
        "Installing dependencies", 
        "Setting up database",
        "Configuring services",
        "Setup complete!"
    ]
    
    print("   Running setup wizard...")
    for step in progress_bar(setup_steps, desc="Setup"):
        time.sleep(0.3)
    
    print_box("Setup completed successfully!", title="Success", color="green")
    
    # System monitoring dashboard
    print("\n2. System Monitoring Dashboard:")
    
    # Simulate system metrics
    metrics_data = [
        {"service": "Web Server", "status": "Running", "cpu": "12%", "memory": "256MB"},
        {"service": "Database", "status": "Running", "cpu": "8%", "memory": "512MB"},
        {"service": "Cache", "status": "Running", "cpu": "3%", "memory": "128MB"},
        {"service": "Queue", "status": "Stopped", "cpu": "0%", "memory": "0MB"}
    ]
    
    print("   System Services Status:")
    
    # Color-code status
    formatted_metrics = []
    for metric in metrics_data:
        formatted_metric = metric.copy()
        status = metric["status"]
        if status == "Running":
            formatted_metric["status"] = colored_text("Running", "green", bold=True)
        else:
            formatted_metric["status"] = colored_text("Stopped", "red", bold=True)
        formatted_metrics.append(formatted_metric)
    
    table = table_format(formatted_metrics)
    print(table)
    
    # File processing utility
    print("\n3. File Processing Utility:")
    
    # Simulate file processing
    files = [f"file_{i:03d}.txt" for i in range(1, 26)]
    
    print("   Processing files...")
    processed_count = 0
    error_count = 0
    
    for filename in progress_bar(files, desc="Processing files"):
        # Simulate processing with occasional errors
        if filename.endswith("013.txt") or filename.endswith("019.txt"):
            error_count += 1
            print(f"   {colored_text('✗', 'red')} Error processing {filename}")
        else:
            processed_count += 1
        
        time.sleep(0.1)
    
    # Summary
    summary_text = f"""
    Processing Summary:
    - Total files: {len(files)}
    - Successfully processed: {processed_count}
    - Errors: {error_count}
    - Success rate: {(processed_count/len(files)*100):.1f}%
    """
    
    if error_count > 0:
        print_box(summary_text.strip(), title="Processing Complete (with errors)", color="yellow")
    else:
        print_box(summary_text.strip(), title="Processing Complete", color="green")


def argument_parsing_examples():
    """Demonstrate enhanced argument parsing patterns."""
    print("\n=== Argument Parsing Examples ===")
    
    print("Enhanced argument parsing patterns:")
    
    # Example CLI structure
    cli_structure = """
    myapp command [options] [arguments]
    
    Commands:
      init        Initialize new project
      build       Build the project
      test        Run tests
      deploy      Deploy to production
      status      Show system status
    
    Global Options:
      --verbose, -v    Verbose output
      --config, -c     Configuration file
      --help, -h       Show help
    """
    
    print(cli_structure)
    
    # Validation examples
    print("\nInput validation examples:")
    
    validation_examples = [
        ("Email validation", "user@example.com", "✓ Valid"),
        ("URL validation", "https://example.com", "✓ Valid"),
        ("Port validation", "8080", "✓ Valid (1-65535)"),
        ("File path validation", "/path/to/file.txt", "✓ Valid path"),
        ("JSON validation", '{"key": "value"}', "✓ Valid JSON")
    ]
    
    for desc, example, result in validation_examples:
        print(f"   {desc}: {example} → {result}")


def error_handling_examples():
    """Demonstrate CLI error handling patterns."""
    print("\n=== Error Handling Examples ===")
    
    # Different types of CLI errors
    error_scenarios = [
        ("User interruption (Ctrl+C)", "KeyboardInterrupt", "Graceful shutdown"),
        ("Invalid input", "ValueError", "Show error and retry"),
        ("File not found", "FileNotFoundError", "Clear error message"),
        ("Permission denied", "PermissionError", "Suggest solution"),
        ("Network timeout", "TimeoutError", "Retry with backoff")
    ]
    
    print("Error handling patterns:")
    for scenario, exception, handling in error_scenarios:
        print(f"   {scenario}:")
        print(f"     Exception: {exception}")
        print(f"     Handling: {handling}")
    
    # Example error handling
    print("\nExample error handling implementation:")
    
    def handle_cli_errors():
        """Example of comprehensive CLI error handling."""
        try:
            # Simulate various operations
            pass
        except KeyboardInterrupt:
            print(colored_text("\n✗ Operation cancelled by user", "yellow"))
            sys.exit(1)
        except FileNotFoundError as e:
            print(colored_text(f"✗ File not found: {e.filename}", "red"))
            print("   Please check the file path and try again.")
            sys.exit(1)
        except PermissionError as e:
            print(colored_text(f"✗ Permission denied: {e}", "red"))
            print("   Try running with elevated privileges or check file permissions.")
            sys.exit(1)
        except Exception as e:
            print(colored_text(f"✗ Unexpected error: {e}", "red"))
            print("   Please report this issue with the error details above.")
            sys.exit(1)
    
    print("   ✓ Comprehensive error handling implemented")


def performance_considerations():
    """Demonstrate performance considerations for CLI utilities."""
    print("\n=== Performance Considerations ===")
    
    print("Performance tips for CLI applications:")
    print("1. Use generators for large datasets to avoid memory issues")
    print("2. Implement lazy loading for expensive operations")
    print("3. Cache frequently accessed data")
    print("4. Use async operations for I/O-bound tasks")
    print("5. Provide progress feedback for long-running operations")
    
    # Example of efficient large data processing
    def process_large_dataset_efficiently():
        """Example of memory-efficient large dataset processing."""
        
        def data_generator(size):
            """Generate data on-demand instead of loading all at once."""
            for i in range(size):
                yield f"item_{i}"
        
        # Process 10,000 items efficiently
        large_dataset = data_generator(10000)
        
        print("\n   Processing large dataset efficiently:")
        processed = 0
        
        # Use progress bar with generator
        for item in progress_bar(large_dataset, desc="Processing", total=10000):
            # Simulate processing
            processed += 1
            if processed % 1000 == 0:
                time.sleep(0.1)  # Simulate work
        
        print(f"   ✓ Processed {processed:,} items efficiently")
    
    process_large_dataset_efficiently()


def limitations_and_gotchas():
    """Document known limitations and gotchas."""
    print("\n=== Limitations and Gotchas ===")
    
    print("Known limitations:")
    print("1. Color support varies by terminal (use color detection)")
    print("2. Interactive prompts don't work in non-TTY environments")
    print("3. Progress bars may not display correctly in all terminals")
    print("4. Unicode characters may not render on all systems")
    print("5. Terminal width detection may fail in some environments")
    
    print("\nCommon gotchas:")
    print("- Always check if stdout is a TTY before using colors/progress bars")
    print("- Handle terminal resize events for responsive layouts")
    print("- Provide fallbacks for non-interactive environments")
    print("- Test CLI tools in different terminal emulators")
    print("- Consider accessibility (screen readers, color blindness)")
    
    print("\nBest practices:")
    print("- Provide both interactive and non-interactive modes")
    print("- Use consistent color schemes and symbols")
    print("- Implement proper signal handling (SIGINT, SIGTERM)")
    print("- Validate user input thoroughly")
    print("- Provide clear help and usage information")
    print("- Support common CLI conventions (--help, --version)")
    print("- Use exit codes consistently")
    print("- Log important operations for debugging")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - CLI Utilities Examples")
    print("=" * 50)
    
    interactive_prompts_examples()
    progress_indicators_examples()
    colored_output_examples()
    table_formatting_examples()
    banner_and_box_examples()
    animation_examples()
    real_world_cli_examples()
    argument_parsing_examples()
    error_handling_examples()
    performance_considerations()
    limitations_and_gotchas()
    
    print("\n" + "=" * 50)
    print("All CLI utilities examples completed!")