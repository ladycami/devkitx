"""Scan code for hardcoded secrets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class SecretMatch:
    """A detected secret."""
    secret_type: str
    value: str
    line_number: int
    file_path: str
    severity: str = "high"  # low, medium, high, critical
    
    @property
    def redacted(self) -> str:
        """Return redacted version."""
        if len(self.value) <= 8:
            return "*" * len(self.value)
        return self.value[:4] + "*" * (len(self.value) - 8) + self.value[-4:]


class SecretsScanner:
    """Scan source code for hardcoded secrets.
    
    Detects:
    - AWS access keys and secrets
    - API keys and tokens
    - Database connection strings
    - Private keys
    - JWT tokens
    - Generic high-entropy strings
    
    Example:
        >>> scanner = SecretsScanner()
        >>> for match in scanner.scan_directory("./src"):
        ...     print(f"{match.file_path}:{match.line_number} - {match.secret_type}")
    """
    
    PATTERNS = [
        # AWS
        ("aws_access_key", r"AKIA[0-9A-Z]{16}", "critical"),
        ("aws_secret_key", r"(?i)aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]", "critical"),
        
        # Generic API keys
        ("api_key", r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]", "high"),
        ("bearer_token", r"(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}", "high"),
        
        # Database
        ("db_connection", r"(?i)(postgres|mysql|mongodb)://[^\s'\"]+", "critical"),
        ("password_assign", r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"][^'\"]{8,}['\"]", "high"),
        
        # Private keys
        ("private_key", r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----", "critical"),
        
        # JWT
        ("jwt_token", r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "high"),
        
        # GitHub
        ("github_token", r"gh[pousr]_[A-Za-z0-9_]{36,}", "critical"),
        
        # Slack
        ("slack_token", r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*", "critical"),
        
        # Generic secrets
        ("secret_assign", r"(?i)(secret|token|auth)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]", "medium"),
    ]
    
    IGNORE_EXTENSIONS = {".pyc", ".so", ".o", ".a", ".dll", ".exe", ".bin", ".jpg", ".png", ".gif"}
    IGNORE_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", ".tox", ".eggs"}
    
    def scan_text(self, text: str, file_path: str = "") -> list[SecretMatch]:
        """Scan text for secrets."""
        matches = []
        lines = text.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            
            for secret_type, pattern, severity in self.PATTERNS:
                for match in re.finditer(pattern, line):
                    matches.append(SecretMatch(
                        secret_type=secret_type,
                        value=match.group(),
                        line_number=line_num,
                        file_path=file_path,
                        severity=severity,
                    ))
        
        return matches
    
    def scan_file(self, path: Path) -> list[SecretMatch]:
        """Scan a single file for secrets."""
        if path.suffix in self.IGNORE_EXTENSIONS:
            return []
        
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return self.scan_text(content, str(path))
        except Exception:
            return []
    
    def scan_directory(self, path: Path | str) -> Iterator[SecretMatch]:
        """Recursively scan directory for secrets."""
        path = Path(path)
        
        for file_path in path.rglob("*"):
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                continue
            
            if file_path.is_file():
                yield from self.scan_file(file_path)