"""System and process utilities for DevKitX.

This module provides utilities for system information, process execution,
and cross-platform system operations.
"""

import asyncio
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

__all__ = [
    "run_command",
    "run_command_async",
    "get_system_info",
    "get_python_info",
    "find_executable",
    "get_env_vars",
    "is_admin",
    "get_free_port",
]


def run_command(
    cmd: list[str], timeout: float | None = None, cwd: str | Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a command with timeout and error handling.

    Args:
        cmd: Command and arguments as list
        timeout: Optional timeout in seconds
        cwd: Optional working directory

    Returns:
        CompletedProcess result with stdout and stderr as strings

    Raises:
        subprocess.TimeoutExpired: If command times out
        subprocess.CalledProcessError: If command returns non-zero exit code
        FileNotFoundError: If command executable is not found
    """
    if not cmd:
        raise ValueError("Command list cannot be empty")

    # Convert Path to string if needed
    if cwd is not None:
        cwd = str(cwd)

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, check=True
        )
        return result
    except subprocess.TimeoutExpired as e:
        # Re-raise with more context
        raise subprocess.TimeoutExpired(
            cmd=e.cmd, timeout=e.timeout, output=e.output, stderr=e.stderr
        ) from e
    except subprocess.CalledProcessError as e:
        # Re-raise with more context
        raise subprocess.CalledProcessError(
            returncode=e.returncode, cmd=e.cmd, output=e.output, stderr=e.stderr
        ) from e
    except FileNotFoundError as e:
        # Provide more helpful error message
        raise FileNotFoundError(f"Command '{cmd[0]}' not found in PATH") from e


async def run_command_async(
    cmd: list[str], timeout: float | None = None
) -> subprocess.CompletedProcess[str]:
    """Run a command asynchronously with timeout.

    Args:
        cmd: Command and arguments as list
        timeout: Optional timeout in seconds

    Returns:
        CompletedProcess result with stdout and stderr as strings

    Raises:
        asyncio.TimeoutError: If command times out
        subprocess.CalledProcessError: If command returns non-zero exit code
        FileNotFoundError: If command executable is not found
    """
    if not cmd:
        raise ValueError("Command list cannot be empty")

    try:
        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for completion with timeout
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)

        # Decode output
        stdout_str = stdout.decode("utf-8") if stdout else ""
        stderr_str = stderr.decode("utf-8") if stderr else ""

        # Create CompletedProcess-like result
        result = subprocess.CompletedProcess(
            args=cmd, returncode=process.returncode or 0, stdout=stdout_str, stderr=stderr_str
        )

        # Check return code
        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                returncode=result.returncode, cmd=cmd, output=stdout_str, stderr=stderr_str
            )

        return result

    except asyncio.TimeoutError as e:
        # Kill the process if it's still running
        if process and process.returncode is None:
            process.kill()
            await process.wait()
        raise asyncio.TimeoutError(
            f"Command '{' '.join(cmd)}' timed out after {timeout} seconds"
        ) from e
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Command '{cmd[0]}' not found in PATH") from e


def get_system_info() -> dict[str, str]:
    """Get system information.

    Returns:
        Dictionary containing system information including OS name, version,
        architecture, hostname, username, and CPU count
    """
    try:
        import getpass

        username = getpass.getuser()
    except Exception:
        username = os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

    try:
        hostname = platform.node()
    except Exception:
        hostname = "unknown"

    try:
        cpu_count = os.cpu_count() or 0
    except Exception:
        cpu_count = 0

    return {
        "os_name": platform.system(),
        "os_version": platform.release(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "processor": platform.processor() or "unknown",
        "hostname": hostname,
        "username": username,
        "cpu_count": str(cpu_count),
    }


def get_python_info() -> dict[str, str]:
    """Get Python runtime information.

    Returns:
        Dictionary containing Python version, implementation, executable path,
        and other runtime details
    """
    return {
        "version": sys.version,
        "version_info": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "implementation": platform.python_implementation(),
        "compiler": platform.python_compiler(),
        "executable": sys.executable,
        "prefix": sys.prefix,
        "path": str(Path(sys.executable).parent),
        "build": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }


def find_executable(name: str) -> str | None:
    """Find executable in system PATH.

    Args:
        name: Name of executable to find

    Returns:
        Path to executable or None if not found
    """
    if not name:
        return None

    # Use shutil.which which handles cross-platform executable finding
    return shutil.which(name)


def get_env_vars(prefix: str = "") -> dict[str, str]:
    """Get environment variables with optional prefix filter.

    Args:
        prefix: Optional prefix to filter variables

    Returns:
        Dictionary of environment variables matching the prefix
    """
    if not prefix:
        return dict(os.environ)

    return {key: value for key, value in os.environ.items() if key.startswith(prefix)}


def is_admin() -> bool:
    """Check if running with administrator/root privileges.

    Returns:
        True if running as admin/root, False otherwise
    """
    try:
        if platform.system() == "Windows":
            import ctypes

            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            # Unix-like systems (Linux, macOS)
            return os.geteuid() == 0
    except Exception:
        # If we can't determine, assume not admin for safety
        return False


def get_free_port(start: int = 8000) -> int:
    """Find a free port starting from the given port number.

    Args:
        start: Starting port number to check

    Returns:
        Available port number

    Raises:
        OSError: If no free port is found in reasonable range
    """
    if start < 1 or start > 65535:
        raise ValueError("Port must be between 1 and 65535")

    # Try ports starting from the given number
    for port in range(start, 65536):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("localhost", port))
                return port
        except OSError:
            # Port is in use, try next one
            continue

    # If we get here, no free port was found
    raise OSError(f"No free port found starting from {start}")
