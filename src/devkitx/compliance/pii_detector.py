"""PII detection utilities for compliance scanning."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator
from pathlib import Path


@dataclass
class PIIMatch:
    """A detected PII instance."""
    pii_type: str
    value: str
    line_number: int
    column: int
    file_path: str = ""
    confidence: float = 1.0
    
    @property
    def redacted(self) -> str:
        """Return redacted version of the value."""
        if len(self.value) <= 4:
            return "*" * len(self.value)
        return self.value[:2] + "*" * (len(self.value) - 4) + self.value[-2:]


class PIIDetector:
    """Detect personally identifiable information in text and files.
    
    Detects:
    - Social Security Numbers (SSN)
    - Credit card numbers
    - Email addresses
    - Phone numbers
    - IP addresses
    
    Example:
        >>> detector = PIIDetector()
        >>> matches = detector.scan_text("Contact john@example.com or 555-123-4567")
        >>> for match in matches:
        ...     print(f"{match.pii_type}: {match.redacted}")
        email: jo**************om
        phone: 55*********67
    """
    
    PATTERNS = {
        "ssn": (
            r"\b\d{3}-\d{2}-\d{4}\b",
            1.0,
        ),
        "credit_card": (
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            0.9,
        ),
        "email": (
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            1.0,
        ),
        "phone": (
            r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            0.8,
        ),
        "ipv4": (
            r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
            0.7,
        ),
    }
    
    def __init__(self, types: list[str] | None = None) -> None:
        """Initialize detector with specific PII types.
        
        Args:
            types: List of PII types to detect (default: all)
        """
        if types:
            self.patterns = {k: v for k, v in self.PATTERNS.items() if k in types}
        else:
            self.patterns = self.PATTERNS.copy()
    
    def scan_text(self, text: str, file_path: str = "") -> list[PIIMatch]:
        """Scan text for PII.
        
        Args:
            text: Text to scan
            file_path: Optional file path for context
            
        Returns:
            List of PII matches
        """
        matches = []
        lines = text.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for pii_type, (pattern, confidence) in self.patterns.items():
                for match in re.finditer(pattern, line, re.IGNORECASE):
                    matches.append(PIIMatch(
                        pii_type=pii_type,
                        value=match.group(),
                        line_number=line_num,
                        column=match.start() + 1,
                        file_path=file_path,
                        confidence=confidence,
                    ))
        
        return matches
    
    def scan_file(self, path: Path | str) -> list[PIIMatch]:
        """Scan a file for PII."""
        path = Path(path)
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return self.scan_text(content, str(path))
        except Exception:
            return []
    
    def scan_directory(
        self,
        path: Path | str,
        extensions: list[str] | None = None,
    ) -> Iterator[PIIMatch]:
        """Scan all files in directory for PII.
        
        Args:
            path: Directory to scan
            extensions: File extensions to include (default: common text files)
            
        Yields:
            PII matches found
        """
        path = Path(path)
        extensions = extensions or [".py", ".js", ".ts", ".json", ".yaml", ".yml", ".txt", ".md", ".csv"]
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in extensions:
                yield from self.scan_file(file_path)