"""NIST 800-53 control mapping utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class NISTControl:
    """NIST 800-53 security control."""
    control_id: str
    title: str
    description: str
    family: str
    priority: str  # low, moderate, high
    
    
# NIST 800-53 controls relevant to DevKitX features
NIST_CONTROLS = {
    "AU-2": NISTControl(
        control_id="AU-2",
        title="Audit Events",
        description="Identify the types of events that the system is capable of auditing",
        family="Audit and Accountability",
        priority="moderate"
    ),
    "AU-3": NISTControl(
        control_id="AU-3", 
        title="Content of Audit Records",
        description="Ensure audit records contain information that establishes what, when, where, source, outcome, and identity",
        family="Audit and Accountability",
        priority="moderate"
    ),
    "AU-9": NISTControl(
        control_id="AU-9",
        title="Protection of Audit Information", 
        description="Protect audit information and audit logging tools from unauthorized access, modification, and deletion",
        family="Audit and Accountability",
        priority="moderate"
    ),
    "SA-3": NISTControl(
        control_id="SA-3",
        title="System Development Life Cycle",
        description="Manage the system using a system development life cycle methodology that includes information security considerations",
        family="System and Services Acquisition", 
        priority="moderate"
    ),
    "SC-8": NISTControl(
        control_id="SC-8",
        title="Transmission Confidentiality and Integrity",
        description="Protect the confidentiality and integrity of transmitted information",
        family="System and Communications Protection",
        priority="moderate"
    ),
    "SC-13": NISTControl(
        control_id="SC-13",
        title="Cryptographic Protection",
        description="Implement cryptographic mechanisms to prevent unauthorized disclosure of information",
        family="System and Communications Protection",
        priority="moderate"
    ),
    "SC-28": NISTControl(
        control_id="SC-28",
        title="Protection of Information at Rest",
        description="Protect the confidentiality and integrity of information at rest",
        family="System and Communications Protection",
        priority="moderate"
    ),
    "SI-12": NISTControl(
        control_id="SI-12",
        title="Information Handling and Retention",
        description="Handle and retain information within the system and information output from the system",
        family="System and Information Integrity",
        priority="moderate"
    ),
    "PM-25": NISTControl(
        control_id="PM-25",
        title="Minimization of Personally Identifiable Information",
        description="Implement policies and procedures to minimize the use of personally identifiable information",
        family="Program Management",
        priority="moderate"
    ),
}


def get_controls_for(feature: str) -> List[NISTControl]:
    """Get NIST controls relevant to a DevKitX feature.
    
    Args:
        feature: DevKitX feature name
        
    Returns:
        List of relevant NIST controls
        
    Example:
        >>> controls = get_controls_for("audit_logger")
        >>> for control in controls:
        ...     print(f"{control.control_id}: {control.title}")
        AU-2: Audit Events
        AU-3: Content of Audit Records
        AU-9: Protection of Audit Information
    """
    feature_mapping = {
        "audit_logger": ["AU-2", "AU-3", "AU-9"],
        "secrets_scanner": ["SA-3", "SC-28"],
        "pii_detector": ["SI-12", "PM-25"],
        "secure_client": ["SC-8", "SC-13"],
        "http_defaults": ["SC-8", "SC-13"],
    }
    
    control_ids = feature_mapping.get(feature, [])
    return [NIST_CONTROLS[control_id] for control_id in control_ids if control_id in NIST_CONTROLS]