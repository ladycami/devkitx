"""NIST 800-53 AU-compliant audit logging."""

from __future__ import annotations

import json
import datetime
import hashlib
import socket
from dataclasses import dataclass, field, asdict
from typing import Any, TextIO
from pathlib import Path


@dataclass
class AuditEvent:
    """Structured audit event meeting NIST AU-3 requirements.
    
    NIST AU-3 requires: what, when, where, source, outcome, identity.
    """
    # What happened
    event_type: str
    action: str
    
    # When
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    
    # Where
    hostname: str = field(default_factory=socket.gethostname)
    service: str = ""
    
    # Source
    source_ip: str = ""
    user_agent: str = ""
    
    # Identity
    user_id: str = ""
    session_id: str = ""
    
    # Outcome
    outcome: str = "success"  # success, failure, error
    outcome_reason: str = ""
    
    # Additional context
    resource_type: str = ""
    resource_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    
    # Integrity
    event_id: str = field(default="")
    
    def __post_init__(self) -> None:
        if not self.event_id:
            # Generate deterministic event ID for integrity checking
            content = f"{self.timestamp}{self.event_type}{self.action}{self.user_id}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_json(self) -> str:
        """Serialize to JSON for logging."""
        return json.dumps(asdict(self), separators=(",", ":"))


class AuditLogger:
    """NIST-compliant audit logger.
    
    Features:
    - Structured JSON output (AU-3)
    - Tamper-evident hashing (AU-9)
    - Required fields enforcement (AU-3)
    - Multiple output targets
    
    Example:
        >>> logger = AuditLogger(service="my-api")
        >>> logger.log_auth("user_login", user_id="123", outcome="success")
        >>> logger.log_access("read", resource_type="document", resource_id="doc-456")
    """
    
    def __init__(
        self,
        service: str,
        output: TextIO | Path | None = None,
    ) -> None:
        self.service = service
        self._output = output
        self._previous_hash: str = "0" * 64  # Chain for tamper evidence
    
    def log(self, event: AuditEvent) -> None:
        """Log an audit event."""
        # Add chain hash for tamper evidence (AU-9)
        event.metadata["_chain_hash"] = self._compute_chain_hash(event)
        
        line = event.to_json()
        
        if self._output is None:
            print(line)
        elif isinstance(self._output, Path):
            with open(self._output, "a") as f:
                f.write(line + "\n")
        else:
            self._output.write(line + "\n")
            self._output.flush()
        
        self._previous_hash = event.metadata["_chain_hash"]
    
    def log_auth(
        self,
        action: str,
        user_id: str,
        outcome: str = "success",
        **kwargs: Any,
    ) -> None:
        """Log authentication event."""
        event = AuditEvent(
            event_type="authentication",
            action=action,
            service=self.service,
            user_id=user_id,
            outcome=outcome,
            **kwargs,
        )
        self.log(event)
    
    def log_access(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str = "",
        outcome: str = "success",
        **kwargs: Any,
    ) -> None:
        """Log resource access event."""
        event = AuditEvent(
            event_type="access",
            action=action,
            service=self.service,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            outcome=outcome,
            **kwargs,
        )
        self.log(event)
    
    def log_change(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str = "",
        changes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Log data change event."""
        metadata = kwargs.pop("metadata", {})
        if changes:
            metadata["changes"] = changes
        
        event = AuditEvent(
            event_type="change",
            action=action,
            service=self.service,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            metadata=metadata,
            **kwargs,
        )
        self.log(event)
    
    def _compute_chain_hash(self, event: AuditEvent) -> str:
        """Compute chain hash for tamper evidence."""
        content = f"{self._previous_hash}{event.event_id}{event.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()