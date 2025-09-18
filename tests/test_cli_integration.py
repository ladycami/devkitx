"""Integration tests for CLI commands."""

import subprocess
import sys
from pathlib import Path


def run_cli_command(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a CLI command and return the result."""
    cmd = [sys.executable, "-m", "devkitx"] + list(args)
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent / "src"
    )


class TestStringCommands:
    """Test string manipulation CLI commands."""

    def test_string_convert_to_snake(self):
        """Test string conversion to snake_case."""
        result = run_cli_command("string", "convert", "MyVariableName", "--to", "snake")
        assert result.returncode == 0
        assert result.stdout.strip() == "my_variable_name"

    def test_string_convert_to_camel(self):
        """Test string conversion to camelCase."""
        result = run_cli_command("string", "convert", "hello_world", "--to", "camel")
        assert result.returncode == 0
        assert result.stdout.strip() == "helloWorld"

    def test_string_convert_to_pascal(self):
        """Test string conversion to PascalCase."""
        result = run_cli_command("string", "convert", "hello_world", "--to", "pascal")
        assert result.returncode == 0
        assert result.stdout.strip() == "HelloWorld"

    def test_string_convert_to_kebab(self):
        """Test string conversion to kebab-case."""
        result = run_cli_command("string", "convert", "HelloWorld", "--to", "kebab")
        assert result.returncode == 0
        assert result.stdout.strip() == "hello-world"

    def test_string_validate_email_valid(self):
        """Test email validation with valid email."""
        result = run_cli_command("string", "validate", "test@example.com", "--type", "email")
        assert result.returncode == 0
        assert result.stdout.strip() == "Valid"

    def test_string_validate_email_invalid(self):
        """Test email validation with invalid email."""
        result = run_cli_command("string", "validate", "invalid-email", "--type", "email")
        assert result.returncode == 0
        assert result.stdout.strip() == "Invalid"

    def test_string_validate_url_valid(self):
        """Test URL validation with valid URL."""
        result = run_cli_command("string", "validate", "https://example.com", "--type", "url")
        assert result.returncode == 0
        assert result.stdout.strip() == "Valid"

    def test_string_validate_url_invalid(self):
        """Test URL validation with invalid URL."""
        result = run_cli_command("string", "validate", "not-a-url", "--type", "url")
        assert result.returncode == 0
        assert result.stdout.strip() == "Invalid"

    def test_string_sanitize_filename(self):
        """Test filename sanitization."""
        result = run_cli_command("string", "sanitize", "file<name>.txt")
        assert result.returncode == 0
        assert result.stdout.strip() == "file_name_.txt"


class TestJSONCommands:
    """Test JSON CLI commands."""

    def test_json_help(self):
        """Test JSON command help."""
        result = run_cli_command("json", "--help")
        assert result.returncode == 0
        assert "flatten" in result.stdout and "pretty" in result.stdout


class TestFileCommands:
    """Test file CLI commands."""

    def test_file_help(self):
        """Test file command help."""
        result = run_cli_command("file", "--help")
        assert result.returncode == 0
        assert "find" in result.stdout


class TestConfigCommands:
    """Test configuration CLI commands."""

    def test_config_help(self):
        """Test config command help."""
        result = run_cli_command("config", "--help")
        assert result.returncode == 0
        assert "load" in result.stdout and "merge" in result.stdout


class TestSystemCommands:
    """Test system CLI commands."""

    def test_system_info(self):
        """Test system info command."""
        result = run_cli_command("system", "info")
        assert result.returncode == 0
        assert "os_name" in result.stdout or "OS Name" in result.stdout

    def test_system_info_json(self):
        """Test system info command with JSON output."""
        result = run_cli_command("system", "info", "--format", "json")
        assert result.returncode == 0
        assert "{" in result.stdout  # JSON output

    def test_system_find_exec_python(self):
        """Test finding Python executable."""
        result = run_cli_command("system", "find-exec", "python")
        assert result.returncode == 0
        assert "python" in result.stdout.lower()


class TestSecurityCommands:
    """Test security CLI commands."""

    def test_security_hash_sha256(self):
        """Test SHA256 hashing."""
        result = run_cli_command("security", "hash", "test-data", "--algorithm", "sha256")
        assert result.returncode == 0
        assert len(result.stdout.strip()) == 64  # SHA256 hex length

    def test_security_generate_secret(self):
        """Test secret generation."""
        result = run_cli_command("security", "generate-secret", "--length", "16")
        assert result.returncode == 0
        # 16 bytes base64 encoded should be 24 characters (with padding)
        secret = result.stdout.strip()
        assert len(secret) == 24
        # Should be valid base64
        import base64

        try:
            decoded = base64.b64decode(secret)
            assert len(decoded) == 16
        except Exception:
            assert False, "Generated secret is not valid base64"

    def test_security_generate_uuid(self):
        """Test UUID generation."""
        result = run_cli_command("security", "generate-uuid")
        assert result.returncode == 0
        # UUID format: 8-4-4-4-12 characters
        uuid_output = result.stdout.strip()
        assert len(uuid_output) == 36
        assert uuid_output.count("-") == 4


class TestTimeCommands:
    """Test time CLI commands."""

    def test_time_duration(self):
        """Test duration formatting."""
        result = run_cli_command("time", "duration", "3661")  # 1 hour, 1 minute, 1 second
        assert result.returncode == 0
        output = result.stdout.strip()
        assert "1h" in output and "1m" in output and "s" in output

    def test_time_business_day(self):
        """Test business day check."""
        result = run_cli_command("time", "business-day", "2024-01-15")  # Monday
        assert result.returncode == 0
        assert result.stdout.strip() in ["Yes", "No"]


class TestValidationCommands:
    """Test validation CLI commands."""

    def test_validation_range_valid(self):
        """Test range validation with valid value."""
        result = run_cli_command("validate", "range", "5", "--min", "1", "--max", "10")
        assert result.returncode == 0
        assert result.stdout.strip() == "Valid"

    def test_validation_range_invalid(self):
        """Test range validation with invalid value."""
        result = run_cli_command("validate", "range", "15", "--min", "1", "--max", "10")
        assert result.returncode == 0
        assert result.stdout.strip() == "Invalid"

    def test_validation_length_valid(self):
        """Test length validation with valid text."""
        result = run_cli_command("validate", "length", "hello", "--min", "3", "--max", "10")
        assert result.returncode == 0
        assert result.stdout.strip() == "Valid"

    def test_validation_length_invalid(self):
        """Test length validation with invalid text."""
        result = run_cli_command("validate", "length", "hi", "--min", "3", "--max", "10")
        assert result.returncode == 0
        assert result.stdout.strip() == "Invalid"


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_invalid_command(self):
        """Test handling of invalid command."""
        result = run_cli_command("invalid-command")
        assert result.returncode != 0

    def test_missing_required_args(self):
        """Test handling of missing required arguments."""
        result = run_cli_command("string", "convert")
        assert result.returncode != 0

    def test_help_command(self):
        """Test main help command."""
        result = run_cli_command("--help")
        assert result.returncode == 0
        assert "devtools-py" in result.stdout
        assert "Available command categories" in result.stdout
