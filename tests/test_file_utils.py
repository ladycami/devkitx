"""Tests for file_utils module."""

from __future__ import annotations
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st

from devtools_py import file_utils


class TestFindFile:
    """Test find_file function."""

    def test_find_exact_name(self, tmp_path: Path):
        """Test finding files by exact name."""
        # Create test files
        (tmp_path / "test.txt").write_text("content")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "test.txt").write_text("content")
        (tmp_path / "other.txt").write_text("content")

        results = file_utils.find_file("test.txt", tmp_path)

        assert len(results) == 2
        assert all(p.name == "test.txt" for p in results)
        assert all(p.is_file() for p in results)

    def test_find_glob_pattern(self, tmp_path: Path):
        """Test finding files by glob pattern."""
        # Create test files
        (tmp_path / "file1.json").write_text("{}")
        (tmp_path / "file2.json").write_text("{}")
        (tmp_path / "file.txt").write_text("text")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.json").write_text("{}")

        results = file_utils.find_file("*.json", tmp_path)

        assert len(results) == 3
        assert all(p.suffix == ".json" for p in results)

    def test_find_case_insensitive_fallback(self, tmp_path: Path):
        """Test case-insensitive fallback when exact match not found."""
        (tmp_path / "Test.TXT").write_text("content")

        results = file_utils.find_file("test.txt", tmp_path)

        assert len(results) == 1
        assert results[0].name == "Test.TXT"

    def test_find_nonexistent_file(self, tmp_path: Path):
        """Test finding nonexistent file returns empty list."""
        results = file_utils.find_file("nonexistent.txt", tmp_path)
        assert results == []

    def test_find_in_nonexistent_directory(self):
        """Test finding in nonexistent directory."""
        results = file_utils.find_file("test.txt", "/nonexistent/path")
        assert results == []

    @given(
        pattern=st.text(min_size=1, max_size=20).filter(lambda x: not any(c in x for c in "*?[]"))
    )
    def test_find_various_names(self, pattern):
        """Test finding files with various names."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # Create a file with the pattern name
            test_file = tmp_path / pattern
            test_file.write_text("content")

            results = file_utils.find_file(pattern, tmp_path)

            assert len(results) == 1
            assert results[0].name == pattern


class TestEnsureDir:
    """Test ensure_dir function."""

    def test_create_new_directory(self, tmp_path: Path):
        """Test creating a new directory."""
        new_dir = tmp_path / "new_directory"

        result = file_utils.ensure_dir(new_dir)

        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_nested_directories(self, tmp_path: Path):
        """Test creating nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"

        result = file_utils.ensure_dir(nested_dir)

        assert result == nested_dir
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_existing_directory(self, tmp_path: Path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = file_utils.ensure_dir(existing_dir)

        assert result == existing_dir
        assert existing_dir.exists()

    def test_string_path(self, tmp_path: Path):
        """Test with string path."""
        new_dir_str = str(tmp_path / "string_dir")

        result = file_utils.ensure_dir(new_dir_str)

        assert result == Path(new_dir_str)
        assert result.exists()


class TestIsReadable:
    """Test is_readable function."""

    def test_readable_file(self, tmp_path: Path):
        """Test with readable file."""
        test_file = tmp_path / "readable.txt"
        test_file.write_text("content")

        assert file_utils.is_readable(test_file) is True

    def test_nonexistent_file(self, tmp_path: Path):
        """Test with nonexistent file."""
        nonexistent = tmp_path / "nonexistent.txt"

        assert file_utils.is_readable(nonexistent) is False

    def test_directory(self, tmp_path: Path):
        """Test with directory."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        assert file_utils.is_readable(test_dir) is True

    def test_permission_error(self, tmp_path: Path):
        """Test handling permission errors."""
        with patch("os.access", side_effect=PermissionError):
            assert file_utils.is_readable(tmp_path) is False

    def test_string_path(self, tmp_path: Path):
        """Test with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert file_utils.is_readable(str(test_file)) is True


class TestIsWritable:
    """Test is_writable function."""

    def test_writable_file(self, tmp_path: Path):
        """Test with writable file."""
        test_file = tmp_path / "writable.txt"
        test_file.write_text("content")

        assert file_utils.is_writable(test_file) is True

    def test_nonexistent_file_writable_parent(self, tmp_path: Path):
        """Test with nonexistent file in writable directory."""
        nonexistent = tmp_path / "new_file.txt"

        assert file_utils.is_writable(nonexistent) is True

    def test_permission_error(self, tmp_path: Path):
        """Test handling permission errors."""
        with patch("os.access", side_effect=PermissionError):
            assert file_utils.is_writable(tmp_path) is False

    def test_string_path(self, tmp_path: Path):
        """Test with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        assert file_utils.is_writable(str(test_file)) is True


class TestAtomicWrite:
    """Test atomic_write function."""

    def test_atomic_write_text(self, tmp_path: Path):
        """Test atomic write with text data."""
        target = tmp_path / "test.txt"

        result = file_utils.atomic_write(target, "hello world")

        assert result == target
        assert target.read_text() == "hello world"

    def test_atomic_write_bytes(self, tmp_path: Path):
        """Test atomic write with bytes data."""
        target = tmp_path / "test.bin"
        data = b"binary data"

        result = file_utils.atomic_write(target, data)

        assert result == target
        assert target.read_bytes() == data

    def test_atomic_write_creates_parent_dirs(self, tmp_path: Path):
        """Test that atomic write creates parent directories."""
        target = tmp_path / "nested" / "dirs" / "file.txt"

        result = file_utils.atomic_write(target, "content")

        assert result == target
        assert target.exists()
        assert target.read_text() == "content"

    def test_atomic_write_overwrites_existing(self, tmp_path: Path):
        """Test that atomic write overwrites existing files."""
        target = tmp_path / "existing.txt"
        target.write_text("old content")

        result = file_utils.atomic_write(target, "new content")

        assert result == target
        assert target.read_text() == "new content"

    def test_string_path(self, tmp_path: Path):
        """Test atomic write with string path."""
        target_str = str(tmp_path / "string_path.txt")

        result = file_utils.atomic_write(target_str, "content")

        assert result == Path(target_str)
        assert result.read_text() == "content"


class TestGlobExt:
    """Test glob_ext function."""

    def test_glob_with_dot_extension(self, tmp_path: Path):
        """Test glob with extension including dot."""
        # Create test files
        (tmp_path / "file1.json").write_text("{}")
        (tmp_path / "file2.json").write_text("{}")
        (tmp_path / "file.txt").write_text("text")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "nested.json").write_text("{}")

        results = file_utils.glob_ext(tmp_path, ".json")

        assert len(results) == 3
        assert all(p.suffix == ".json" for p in results)

    def test_glob_without_dot_extension(self, tmp_path: Path):
        """Test glob with extension without dot."""
        # Create test files
        (tmp_path / "file1.py").write_text("code")
        (tmp_path / "file2.py").write_text("code")
        (tmp_path / "file.txt").write_text("text")

        results = file_utils.glob_ext(tmp_path, "py")

        assert len(results) == 2
        assert all(p.suffix == ".py" for p in results)

    def test_glob_no_matches(self, tmp_path: Path):
        """Test glob with no matching files."""
        (tmp_path / "file.txt").write_text("text")

        results = file_utils.glob_ext(tmp_path, ".json")

        assert results == []

    def test_string_path(self, tmp_path: Path):
        """Test glob with string path."""
        (tmp_path / "test.xml").write_text("<xml/>")

        results = file_utils.glob_ext(str(tmp_path), "xml")

        assert len(results) == 1
        assert results[0].suffix == ".xml"


class TestCopyFile:
    """Test copy_file function."""

    def test_copy_file_basic(self, tmp_path: Path):
        """Test basic file copying."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("test content")

        result = file_utils.copy_file(src, dst)

        assert result == dst
        assert dst.exists()
        assert dst.read_text() == "test content"
        assert src.exists()  # Source should still exist

    def test_copy_file_creates_parent_dirs(self, tmp_path: Path):
        """Test that copy creates parent directories."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "nested" / "dirs" / "destination.txt"
        src.write_text("content")

        result = file_utils.copy_file(src, dst)

        assert result == dst
        assert dst.exists()
        assert dst.read_text() == "content"

    def test_copy_file_overwrite_default(self, tmp_path: Path):
        """Test that copy overwrites by default."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("new content")
        dst.write_text("old content")

        result = file_utils.copy_file(src, dst)

        assert result == dst
        assert dst.read_text() == "new content"

    def test_copy_file_no_overwrite(self, tmp_path: Path):
        """Test copy with overwrite=False raises error if destination exists."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("new content")
        dst.write_text("old content")

        with pytest.raises(FileExistsError):
            file_utils.copy_file(src, dst, overwrite=False)

        # Destination should be unchanged
        assert dst.read_text() == "old content"

    def test_copy_file_string_paths(self, tmp_path: Path):
        """Test copy with string paths."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("content")

        result = file_utils.copy_file(str(src), str(dst))

        assert result == dst
        assert dst.read_text() == "content"

    def test_copy_preserves_metadata(self, tmp_path: Path):
        """Test that copy preserves file metadata."""
        src = tmp_path / "source.txt"
        dst = tmp_path / "destination.txt"
        src.write_text("content")

        # Get original modification time
        original_mtime = src.stat().st_mtime

        file_utils.copy_file(src, dst)

        # Destination should have same modification time
        assert abs(dst.stat().st_mtime - original_mtime) < 1.0  # Allow small difference


class TestFileUtilsIntegration:
    """Integration tests for file_utils module."""

    def test_workflow_integration(self, tmp_path: Path):
        """Test a complete workflow using multiple functions."""
        # Create directory structure
        work_dir = tmp_path / "project"
        file_utils.ensure_dir(work_dir / "src")
        file_utils.ensure_dir(work_dir / "tests")

        # Create some files
        src_file = work_dir / "src" / "main.py"
        file_utils.atomic_write(src_file, "print('hello')")

        test_file = work_dir / "tests" / "test_main.py"
        file_utils.atomic_write(test_file, "def test_main(): pass")

        # Find Python files
        py_files = file_utils.glob_ext(work_dir, "py")
        assert len(py_files) == 2

        # Check readability
        assert all(file_utils.is_readable(f) for f in py_files)
        assert all(file_utils.is_writable(f) for f in py_files)

        # Copy a file
        backup_file = work_dir / "main_backup.py"
        file_utils.copy_file(src_file, backup_file)

        # Verify the copy
        assert backup_file.read_text() == src_file.read_text()

    @given(
        filename=st.text(min_size=1, max_size=20).filter(lambda x: x.isalnum()),
        content=st.text(min_size=0, max_size=100),
    )
    def test_atomic_write_find_roundtrip(self, filename, content):
        """Test atomic write and find roundtrip with various inputs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            target = tmp_path / f"{filename}.txt"

            # Write file
            file_utils.atomic_write(target, content)

            # Find file
            found = file_utils.find_file(f"{filename}.txt", tmp_path)

            assert len(found) == 1
            assert found[0].read_text() == content
