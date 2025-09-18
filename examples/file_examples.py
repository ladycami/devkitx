#!/usr/bin/env python3
"""
File Utilities Examples

This module demonstrates practical usage of devkitx.file_utils
including file operations, path handling, and cross-platform compatibility.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Generator

from devkitx.file_utils import (
    read_file,
    write_file,
    append_file,
    copy_file,
    move_file,
    delete_file,
    create_directory,
    list_files,
    get_file_info,
    find_files,
    backup_file,
    safe_filename,
    get_file_hash,
    compress_file,
    decompress_file,
    watch_directory,
    batch_rename,
    sync_directories
)


def basic_file_operations():
    """Demonstrate basic file read/write operations."""
    print("=== Basic File Operations ===")
    
    # Create a temporary directory for examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Write text file
        sample_file = temp_path / "sample.txt"
        content = "Hello, World!\nThis is a sample file.\nLine 3 with some data."
        
        write_file(sample_file, content)
        print(f"✓ Created file: {sample_file}")
        
        # Read file back
        read_content = read_file(sample_file)
        print(f"✓ Read content: {len(read_content)} characters")
        
        # Append to file
        append_file(sample_file, "\nAppended line 4")
        updated_content = read_file(sample_file)
        print(f"✓ After append: {len(updated_content)} characters")
        
        # Binary file operations
        binary_file = temp_path / "binary.dat"
        binary_data = b'\x00\x01\x02\x03\xFF\xFE\xFD'
        
        write_file(binary_file, binary_data, mode='wb')
        read_binary = read_file(binary_file, mode='rb')
        print(f"✓ Binary file: wrote {len(binary_data)} bytes, read {len(read_binary)} bytes")
        
        # File info
        info = get_file_info(sample_file)
        print(f"✓ File info: size={info['size']} bytes, modified={info['modified']}")


def file_management_operations():
    """Demonstrate file management operations."""
    print("\n=== File Management Operations ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create source file
        source_file = temp_path / "source.txt"
        write_file(source_file, "Original content")
        
        # Copy file
        copy_dest = temp_path / "copied.txt"
        copy_file(source_file, copy_dest)
        print(f"✓ Copied {source_file.name} to {copy_dest.name}")
        
        # Move file
        move_dest = temp_path / "moved.txt"
        move_file(copy_dest, move_dest)
        print(f"✓ Moved {copy_dest.name} to {move_dest.name}")
        
        # Backup file
        backup_path = backup_file(source_file)
        print(f"✓ Created backup: {backup_path}")
        
        # Create directory structure
        nested_dir = temp_path / "nested" / "deep" / "structure"
        create_directory(nested_dir)
        print(f"✓ Created nested directory: {nested_dir}")
        
        # List files
        files = list_files(temp_path, recursive=True)
        print(f"✓ Found {len(files)} files in directory tree")
        for file_path in files:
            print(f"  - {file_path.relative_to(temp_path)}")


def file_search_and_filtering():
    """Demonstrate file search and filtering capabilities."""
    print("\n=== File Search and Filtering ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample file structure
        files_to_create = [
            "document.txt",
            "image.jpg", 
            "script.py",
            "data.json",
            "config.yaml",
            "backup.txt.bak",
            "logs/app.log",
            "logs/error.log",
            "src/main.py",
            "src/utils.py",
            "tests/test_main.py"
        ]
        
        for file_path in files_to_create:
            full_path = temp_path / file_path
            create_directory(full_path.parent)
            write_file(full_path, f"Content of {file_path}")
        
        print(f"✓ Created {len(files_to_create)} sample files")
        
        # Find files by extension
        python_files = find_files(temp_path, pattern="*.py", recursive=True)
        print(f"✓ Found {len(python_files)} Python files:")
        for py_file in python_files:
            print(f"  - {py_file.relative_to(temp_path)}")
        
        # Find files by name pattern
        log_files = find_files(temp_path, pattern="*.log", recursive=True)
        print(f"✓ Found {len(log_files)} log files:")
        for log_file in log_files:
            print(f"  - {log_file.relative_to(temp_path)}")
        
        # Find files by size (create files of different sizes)
        large_file = temp_path / "large.txt"
        write_file(large_file, "x" * 10000)  # 10KB file
        
        # Custom filter function
        def size_filter(file_path: Path) -> bool:
            return file_path.stat().st_size > 1000
        
        large_files = [f for f in list_files(temp_path, recursive=True) if size_filter(f)]
        print(f"✓ Found {len(large_files)} files larger than 1KB")


def file_hashing_and_integrity():
    """Demonstrate file hashing and integrity checking."""
    print("\n=== File Hashing and Integrity ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test files with different content
        files_content = {
            "file1.txt": "This is the first file content",
            "file2.txt": "This is the second file content", 
            "file3.txt": "This is the first file content"  # Same as file1
        }
        
        file_hashes = {}
        
        for filename, content in files_content.items():
            file_path = temp_path / filename
            write_file(file_path, content)
            
            # Calculate different hash types
            md5_hash = get_file_hash(file_path, algorithm='md5')
            sha256_hash = get_file_hash(file_path, algorithm='sha256')
            
            file_hashes[filename] = {
                'md5': md5_hash,
                'sha256': sha256_hash
            }
            
            print(f"✓ {filename}:")
            print(f"  MD5:    {md5_hash}")
            print(f"  SHA256: {sha256_hash}")
        
        # Check for duplicate files
        print("\n✓ Duplicate detection:")
        md5_groups = {}
        for filename, hashes in file_hashes.items():
            md5 = hashes['md5']
            if md5 not in md5_groups:
                md5_groups[md5] = []
            md5_groups[md5].append(filename)
        
        for md5, files in md5_groups.items():
            if len(files) > 1:
                print(f"  Duplicates found: {', '.join(files)} (MD5: {md5[:8]}...)")


def compression_examples():
    """Demonstrate file compression and decompression."""
    print("\n=== File Compression Examples ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a text file with repetitive content (compresses well)
        text_file = temp_path / "repetitive.txt"
        repetitive_content = "This line repeats many times.\n" * 1000
        write_file(text_file, repetitive_content)
        
        original_size = text_file.stat().st_size
        print(f"✓ Original file size: {original_size:,} bytes")
        
        # Compress file
        compressed_file = compress_file(text_file)
        compressed_size = compressed_file.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        print(f"✓ Compressed file: {compressed_file.name}")
        print(f"✓ Compressed size: {compressed_size:,} bytes")
        print(f"✓ Compression ratio: {compression_ratio:.1f}%")
        
        # Decompress file
        decompressed_file = decompress_file(compressed_file)
        decompressed_content = read_file(decompressed_file)
        
        print(f"✓ Decompressed file: {decompressed_file.name}")
        print(f"✓ Content matches original: {decompressed_content == repetitive_content}")


def batch_operations():
    """Demonstrate batch file operations."""
    print("\n=== Batch Operations ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create files with inconsistent naming
        original_files = [
            "Document 1.txt",
            "Document 2.txt", 
            "Image File.jpg",
            "Script File.py",
            "Data File.json"
        ]
        
        for filename in original_files:
            file_path = temp_path / filename
            write_file(file_path, f"Content of {filename}")
        
        print(f"✓ Created {len(original_files)} files with spaces in names")
        
        # Batch rename to remove spaces and lowercase
        def rename_function(old_name: str) -> str:
            # Replace spaces with underscores and convert to lowercase
            return old_name.replace(" ", "_").lower()
        
        renamed_files = batch_rename(temp_path, rename_function)
        print(f"✓ Renamed {len(renamed_files)} files:")
        for old_name, new_name in renamed_files.items():
            print(f"  '{old_name}' → '{new_name}'")
        
        # Batch file processing
        def process_text_files(directory: Path) -> Dict[str, int]:
            """Count lines in all text files."""
            results = {}
            
            for file_path in find_files(directory, pattern="*.txt"):
                content = read_file(file_path)
                line_count = len(content.splitlines())
                results[file_path.name] = line_count
            
            return results
        
        line_counts = process_text_files(temp_path)
        print(f"✓ Line counts for text files:")
        for filename, count in line_counts.items():
            print(f"  {filename}: {count} lines")


def directory_synchronization():
    """Demonstrate directory synchronization."""
    print("\n=== Directory Synchronization ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create source and destination directories
        source_dir = temp_path / "source"
        dest_dir = temp_path / "destination"
        
        create_directory(source_dir)
        create_directory(dest_dir)
        
        # Create files in source directory
        source_files = {
            "file1.txt": "Content 1",
            "file2.txt": "Content 2",
            "subdir/file3.txt": "Content 3"
        }
        
        for rel_path, content in source_files.items():
            file_path = source_dir / rel_path
            create_directory(file_path.parent)
            write_file(file_path, content)
        
        print(f"✓ Created source directory with {len(source_files)} files")
        
        # Sync directories
        sync_result = sync_directories(source_dir, dest_dir)
        print(f"✓ Synchronized directories:")
        print(f"  Copied: {sync_result['copied']} files")
        print(f"  Updated: {sync_result['updated']} files")
        print(f"  Deleted: {sync_result['deleted']} files")
        
        # Verify sync
        dest_files = list_files(dest_dir, recursive=True)
        print(f"✓ Destination now has {len(dest_files)} files")


def safe_filename_examples():
    """Demonstrate safe filename generation."""
    print("\n=== Safe Filename Examples ===")
    
    unsafe_names = [
        "file with spaces.txt",
        "file/with\\slashes.doc",
        "file:with*special?chars.pdf",
        "file<with>pipes|and\"quotes.csv",
        "CON.txt",  # Windows reserved name
        "aux.log",  # Windows reserved name
        "file" + "x" * 300 + ".txt",  # Very long name
        "файл.txt",  # Unicode characters
        ".hidden_file",
        "file..txt"  # Multiple dots
    ]
    
    print("Unsafe filename → Safe filename:")
    print("-" * 50)
    
    for unsafe in unsafe_names:
        safe = safe_filename(unsafe)
        print(f"'{unsafe[:30]}...' → '{safe}'")
    
    # Platform-specific considerations
    print("\n✓ Platform-specific considerations:")
    print("  - Windows: Reserved names (CON, AUX, PRN, etc.) are handled")
    print("  - All platforms: Special characters are replaced or removed")
    print("  - Length limits are enforced (usually 255 characters)")
    print("  - Unicode characters may be transliterated or removed")


def error_handling_examples():
    """Demonstrate error handling and edge cases."""
    print("\n=== Error Handling Examples ===")
    
    # Handle missing files
    try:
        content = read_file("nonexistent_file.txt")
    except FileNotFoundError as e:
        print(f"✓ Handled missing file: {type(e).__name__}")
    
    # Handle permission errors (simulate)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a file and try to write to read-only file
        readonly_file = temp_path / "readonly.txt"
        write_file(readonly_file, "Initial content")
        
        # Make file read-only (Unix-like systems)
        if hasattr(os, 'chmod'):
            try:
                os.chmod(readonly_file, 0o444)  # Read-only
                write_file(readonly_file, "New content")
            except PermissionError as e:
                print(f"✓ Handled permission error: {type(e).__name__}")
            finally:
                # Restore write permission for cleanup
                os.chmod(readonly_file, 0o644)
        
        # Handle disk space issues (can't easily simulate)
        print("✓ Disk space errors would be handled with OSError")
        
        # Handle invalid paths
        try:
            invalid_path = Path("invalid\x00path.txt")  # Null byte in path
            write_file(invalid_path, "content")
        except (ValueError, OSError) as e:
            print(f"✓ Handled invalid path: {type(e).__name__}")


def performance_considerations():
    """Demonstrate performance considerations."""
    print("\n=== Performance Considerations ===")
    
    print("Performance tips:")
    print("1. Use buffered I/O for large files")
    print("2. Process files in chunks for memory efficiency")
    print("3. Use generators for large directory listings")
    print("4. Consider async I/O for concurrent operations")
    print("5. Cache file metadata when processing many files")
    
    # Demonstrate efficient large file processing
    def process_large_file_efficiently(file_path: Path, chunk_size: int = 8192) -> int:
        """Process large file in chunks to avoid memory issues."""
        total_size = 0
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                total_size += len(chunk)
                # Process chunk here
        
        return total_size
    
    # Demonstrate efficient directory traversal
    def find_files_efficiently(directory: Path, pattern: str) -> Generator[Path, None, None]:
        """Memory-efficient file finding using generators."""
        for item in directory.rglob(pattern):
            if item.is_file():
                yield item
    
    print("✓ Use chunked reading for large files")
    print("✓ Use generators for memory-efficient directory traversal")
    print("✓ Consider pathlib.Path for cross-platform compatibility")


def limitations_and_gotchas():
    """Document known limitations and gotchas."""
    print("\n=== Limitations and Gotchas ===")
    
    print("Known limitations:")
    print("1. File operations are blocking - use async variants for concurrency")
    print("2. Large files may consume significant memory if read entirely")
    print("3. File watching may have platform-specific limitations")
    print("4. Atomic operations aren't guaranteed across all filesystems")
    print("5. Unicode filename support varies by filesystem")
    
    print("\nCross-platform gotchas:")
    print("- Path separators: Use pathlib.Path for cross-platform compatibility")
    print("- Case sensitivity: Windows is case-insensitive, Unix is case-sensitive")
    print("- Reserved filenames: Windows has reserved names (CON, AUX, etc.)")
    print("- Maximum path length: Windows has 260 character limit (can be extended)")
    print("- File locking behavior differs between platforms")
    
    print("\nBest practices:")
    print("- Always use context managers (with statements) for file operations")
    print("- Handle exceptions appropriately for your use case")
    print("- Use pathlib.Path instead of string concatenation")
    print("- Validate filenames before creating files")
    print("- Consider file permissions and ownership")
    print("- Use atomic operations when data integrity is critical")
    print("- Test file operations on target platforms")


if __name__ == "__main__":
    """Run all examples."""
    print("Dev QoL Toolkit - File Utilities Examples")
    print("=" * 50)
    
    basic_file_operations()
    file_management_operations()
    file_search_and_filtering()
    file_hashing_and_integrity()
    compression_examples()
    batch_operations()
    directory_synchronization()
    safe_filename_examples()
    error_handling_examples()
    performance_considerations()
    limitations_and_gotchas()
    
    print("\n" + "=" * 50)
    print("All file utilities examples completed!")