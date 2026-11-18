"""NIST 800-53 AU-compliant audit logging."""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import socket
import threading
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TextIO

__all__ = ["AuditEvent", "AuditLogger", "AuditChainError", "verify_chain", "GENESIS_HASH"]

#: Chain value used before the first event in a log.
GENESIS_HASH = "0" * 64
_CHAIN_FIELD = "_chain_hash"


def _utc_timestamp() -> str:
    """UTC time as ``YYYY-MM-DDTHH:MM:SS.ffffffZ`` (same format as devkitx 2.0)."""
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    return now.isoformat() + "Z"


@dataclass
class AuditEvent:
    """Structured audit event meeting NIST AU-3 requirements.

    NIST AU-3 requires: what, when, where, source, outcome, identity.
    """

    # What happened
    event_type: str
    action: str

    # When
    timestamp: str = field(default_factory=_utc_timestamp)

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
            content = f"{self.timestamp}{self.event_type}{self.action}{self.user_id}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_json(self) -> str:
        """Serialize to JSON for logging."""
        return json.dumps(asdict(self), separators=(",", ":"))


class AuditChainError(ValueError):
    """Raised when an audit log fails chain verification."""

    def __init__(self, line_number: int, reason: str) -> None:
        super().__init__(f"Audit log line {line_number}: {reason}")
        self.line_number = line_number
        self.reason = reason


def _canonical(record: dict[str, Any]) -> bytes:
    """Stable byte form of a record, excluding its own chain hash."""
    body = dict(record)
    metadata = dict(body.get("metadata") or {})
    metadata.pop(_CHAIN_FIELD, None)
    body["metadata"] = metadata
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _chain_hash(previous: str, record: dict[str, Any], key: bytes | None) -> str:
    message = previous.encode() + b"\n" + _canonical(record)
    if key:
        return hmac.new(key, message, hashlib.sha256).hexdigest()
    return hashlib.sha256(message).hexdigest()


def verify_chain(
    source: Path | str | Iterable[str],
    hmac_key: bytes | None = None,
    previous_hash: str = GENESIS_HASH,
) -> int:
    """Verify an audit log's hash chain.

    Every event's ``metadata._chain_hash`` covers the previous event's hash
    and the event's full content, so editing, deleting, inserting or
    reordering any line is detected from that point on.

    Without ``hmac_key`` the chain detects accidental or partial tampering,
    but someone able to rewrite the whole file can recompute it. Use an HMAC
    key stored outside the log (for example in a secrets manager) for
    protection against deliberate tampering (NIST AU-9).

    Args:
        source: Log file path, or an iterable of JSON lines.
        hmac_key: Key the log was written with, if any.
        previous_hash: Chain value before the first line (for rotated logs).

    Returns:
        Number of events verified.

    Raises:
        AuditChainError: On the first line that fails verification.
    """
    if isinstance(source, (str, Path)):
        with open(source, encoding="utf-8") as handle:
            return verify_chain(handle.readlines(), hmac_key, previous_hash)

    expected_previous = previous_hash
    count = 0
    for line_number, line in enumerate(source, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            recorded = record["metadata"][_CHAIN_FIELD]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise AuditChainError(line_number, f"not a chained audit event ({exc})") from None
        expected = _chain_hash(expected_previous, record, hmac_key)
        if not hmac.compare_digest(recorded, expected):
            raise AuditChainError(
                line_number, "chain hash mismatch (event altered, removed or reordered)"
            )
        expected_previous = recorded
        count += 1
    return count


def _last_chain_hash(path: Path) -> str | None:
    """Chain hash of the last event in an existing log file, if any."""
    if not path.exists():
        return None
    last = ""
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last = line
    if not last:
        return None
    try:
        return str(json.loads(last)["metadata"][_CHAIN_FIELD])
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


class AuditLogger:
    """NIST-compliant audit logger.

    Features:
    - Structured JSON output (AU-3)
    - Hash chain over every event's full content; keyed (HMAC-SHA256) when
      ``hmac_key`` is given (AU-9). Check a log with :func:`verify_chain`.
    - Continues an existing file's chain after a restart
    - Thread-safe
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
        *,
        hmac_key: bytes | None = None,
        previous_hash: str | None = None,
    ) -> None:
        """Create a logger.

        Args:
            service: Service name recorded on every event.
            output: Stream, file path (appended to), or None for stdout.
            hmac_key: Secret key for keyed chain hashes. Keep it out of the log.
            previous_hash: Chain value to continue from. Defaults to the last
                event in ``output`` when it is an existing file, otherwise
                :data:`GENESIS_HASH`.
        """
        self.service = service
        self._output = output
        self._key = hmac_key
        self._lock = threading.Lock()
        if previous_hash is None and isinstance(output, Path):
            previous_hash = _last_chain_hash(output)
        self._previous_hash: str = previous_hash or GENESIS_HASH

    def log(self, event: AuditEvent) -> None:
        """Log an audit event."""
        with self._lock:
            event.metadata.pop(_CHAIN_FIELD, None)
            # Hash exactly what a reader will parse back from the line.
            record = json.loads(event.to_json())
            event.metadata[_CHAIN_FIELD] = _chain_hash(self._previous_hash, record, self._key)

            line = event.to_json()

            if self._output is None:
                print(line)
            elif isinstance(self._output, Path):
                with open(self._output, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            else:
                self._output.write(line + "\n")
                self._output.flush()

            self._previous_hash = event.metadata[_CHAIN_FIELD]

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
