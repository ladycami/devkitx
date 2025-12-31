"""Tests for DevKitX compliance module."""

import json
from io import StringIO
import pytest
from devkitx.compliance import AuditLogger, AuditEvent, PIIDetector, PIIMatch


class TestAuditLogger:
    """Test audit logging functionality."""
    
    def test_audit_event_creation(self):
        """Test creating audit events."""
        event = AuditEvent(
            event_type="authentication",
            action="login",
            service="test-service",
            user_id="user123",
            outcome="success"
        )
        
        assert event.event_type == "authentication"
        assert event.action == "login"
        assert event.user_id == "user123"
        assert event.outcome == "success"
        assert event.event_id  # Should be auto-generated
        assert event.timestamp  # Should be auto-generated
    
    def test_audit_event_json_serialization(self):
        """Test audit event JSON serialization."""
        event = AuditEvent(
            event_type="access",
            action="read",
            service="api",
            user_id="user456",
            resource_type="document",
            resource_id="doc123"
        )
        
        json_str = event.to_json()
        parsed = json.loads(json_str)
        
        assert parsed["event_type"] == "access"
        assert parsed["action"] == "read"
        assert parsed["user_id"] == "user456"
        assert parsed["resource_type"] == "document"
        assert parsed["resource_id"] == "doc123"
    
    def test_audit_logger_log_auth(self):
        """Test logging authentication events."""
        output = StringIO()
        logger = AuditLogger(service="test-service", output=output)
        
        logger.log_auth(
            action="login",
            user_id="user123",
            outcome="success",
            source_ip="192.168.1.100"
        )
        
        output.seek(0)
        log_line = output.read().strip()
        parsed = json.loads(log_line)
        
        assert parsed["event_type"] == "authentication"
        assert parsed["action"] == "login"
        assert parsed["user_id"] == "user123"
        assert parsed["outcome"] == "success"
        assert parsed["source_ip"] == "192.168.1.100"
        assert parsed["service"] == "test-service"
    
    def test_audit_logger_log_access(self):
        """Test logging access events."""
        output = StringIO()
        logger = AuditLogger(service="api", output=output)
        
        logger.log_access(
            action="read",
            resource_type="user_profile",
            resource_id="profile456",
            user_id="user123"
        )
        
        output.seek(0)
        log_line = output.read().strip()
        parsed = json.loads(log_line)
        
        assert parsed["event_type"] == "access"
        assert parsed["action"] == "read"
        assert parsed["resource_type"] == "user_profile"
        assert parsed["resource_id"] == "profile456"
        assert parsed["user_id"] == "user123"
    
    def test_audit_logger_log_change(self):
        """Test logging change events."""
        output = StringIO()
        logger = AuditLogger(service="api", output=output)
        
        changes = {"email": {"old": "old@example.com", "new": "new@example.com"}}
        logger.log_change(
            action="update",
            resource_type="user_profile",
            resource_id="profile456",
            user_id="user123",
            changes=changes
        )
        
        output.seek(0)
        log_line = output.read().strip()
        parsed = json.loads(log_line)
        
        assert parsed["event_type"] == "change"
        assert parsed["action"] == "update"
        assert parsed["metadata"]["changes"] == changes


class TestPIIDetector:
    """Test PII detection functionality."""
    
    def test_detect_email(self):
        """Test email detection."""
        detector = PIIDetector()
        text = "Contact us at support@example.com for help."
        
        matches = detector.scan_text(text)
        
        email_matches = [m for m in matches if m.pii_type == "email"]
        assert len(email_matches) == 1
        assert email_matches[0].value == "support@example.com"
        assert email_matches[0].line_number == 1
    
    def test_detect_phone(self):
        """Test phone number detection."""
        detector = PIIDetector()
        text = "Call us at 555-123-4567 or (555) 987-6543."
        
        matches = detector.scan_text(text)
        
        phone_matches = [m for m in matches if m.pii_type == "phone"]
        assert len(phone_matches) == 2
        assert "555-123-4567" in [m.value for m in phone_matches]
        assert "(555) 987-6543" in [m.value for m in phone_matches]
    
    def test_detect_ssn(self):
        """Test SSN detection."""
        detector = PIIDetector()
        text = "SSN: 123-45-6789"
        
        matches = detector.scan_text(text)
        
        ssn_matches = [m for m in matches if m.pii_type == "ssn"]
        assert len(ssn_matches) == 1
        assert ssn_matches[0].value == "123-45-6789"
        assert ssn_matches[0].confidence == 1.0
    
    def test_detect_credit_card(self):
        """Test credit card detection."""
        detector = PIIDetector()
        text = "Card number: 4532 1234 5678 9012"
        
        matches = detector.scan_text(text)
        
        cc_matches = [m for m in matches if m.pii_type == "credit_card"]
        assert len(cc_matches) == 1
        assert "4532 1234 5678 9012" in cc_matches[0].value
    
    def test_detect_ip_address(self):
        """Test IP address detection."""
        detector = PIIDetector()
        text = "Server IP: 192.168.1.100"
        
        matches = detector.scan_text(text)
        
        ip_matches = [m for m in matches if m.pii_type == "ipv4"]
        assert len(ip_matches) == 1
        assert ip_matches[0].value == "192.168.1.100"
    
    def test_pii_redaction(self):
        """Test PII value redaction."""
        match = PIIMatch(
            pii_type="email",
            value="john.doe@example.com",
            line_number=1,
            column=1,
            confidence=1.0
        )
        
        redacted = match.redacted
        assert redacted.startswith("jo")
        assert redacted.endswith("om")
        assert "****" in redacted or "***" in redacted
    
    def test_specific_pii_types(self):
        """Test detector with specific PII types."""
        detector = PIIDetector(types=["email"])
        text = "Email: john@example.com, Phone: 555-1234"
        
        matches = detector.scan_text(text)
        
        # Should only detect email, not phone
        assert len(matches) == 1
        assert matches[0].pii_type == "email"
    
    def test_multiline_detection(self):
        """Test PII detection across multiple lines."""
        detector = PIIDetector()
        text = """Line 1: Contact info
Line 2: Email: support@example.com
Line 3: Phone: 555-123-4567"""
        
        matches = detector.scan_text(text)
        
        # Check line numbers are correct
        email_match = next(m for m in matches if m.pii_type == "email")
        phone_match = next(m for m in matches if m.pii_type == "phone")
        
        assert email_match.line_number == 2
        assert phone_match.line_number == 3