"""
Core Data Models for PPE Compliance Monitoring System

This module defines the core data models used throughout the PPE compliance system:
- PPEDetection: Individual PPE item detections
- PersonDetection: Person detection with associated PPE items
- FaceDetection: Face recognition results with employee information
- ViolationEvent: Complete violation record with evidence

Requirements: 2.1, 3.1, 4.2, 10.2, 11.2
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from enum import Enum
import numpy as np

from ..config.ppe_detection_config import PPEItemType


class ViolationType(Enum):
    """Types of PPE compliance violations"""
    MISSING_HELMET = "missing_helmet"
    MISSING_GLASSES = "missing_glasses" 
    MISSING_UNIFORM = "missing_uniform"
    MISSING_GLOVES = "missing_gloves"
    MISSING_VEST = "missing_vest"
    MISSING_SHOES = "missing_shoes"
    MULTIPLE_VIOLATIONS = "multiple_violations"
    UNKNOWN_PERSON = "unknown_person"


class ComplianceStatus(Enum):
    """PPE compliance status for individuals"""
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    INVALID_DETECTION = "invalid_detection"


@dataclass
class PPEDetection:
    """
    Individual PPE item detection result
    
    Represents a detected PPE item with confidence score and location.
    Requirement: Valid detections must meet minimum confidence threshold.
    """
    item_type: PPEItemType
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    is_compliant: bool
    detection_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate PPE detection data"""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if len(self.bounding_box) != 4:
            raise ValueError(f"Bounding box must have 4 coordinates, got {len(self.bounding_box)}")
        
        x1, y1, x2, y2 = self.bounding_box
        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Invalid bounding box coordinates: {self.bounding_box}")
    
    def is_valid_detection(self, min_confidence: float = 0.7) -> bool:
        """Check if detection meets minimum confidence threshold"""
        return self.confidence >= min_confidence
    
    def get_detection_area(self) -> float:
        """Calculate bounding box area"""
        x1, y1, x2, y2 = self.bounding_box
        return (x2 - x1) * (y2 - y1)


@dataclass
class PersonDetection:
    """
    Person detection with associated PPE items
    
    Represents a detected person and their PPE compliance status.
    Requirement: Valid PPE detections required before marking compliance as met.
    """
    person_id: int
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    ppe_items: List[PPEDetection]
    compliance_status: ComplianceStatus
    confidence: float = 0.0
    detection_timestamp: datetime = field(default_factory=datetime.now)
    zone_name: Optional[str] = None
    
    def __post_init__(self):
        """Validate person detection data"""
        if len(self.bounding_box) != 4:
            raise ValueError(f"Bounding box must have 4 coordinates, got {len(self.bounding_box)}")
        
        x1, y1, x2, y2 = self.bounding_box
        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Invalid bounding box coordinates: {self.bounding_box}")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    def has_valid_ppe_detections(self, min_confidence: float = 0.7) -> bool:
        """
        Check if person has valid PPE detections
        Requirement: Valid detections required before marking compliance as met
        """
        if not self.ppe_items:
            return False
        
        return any(item.is_valid_detection(min_confidence) for item in self.ppe_items)
    
    def get_detected_ppe_types(self, min_confidence: float = 0.7) -> List[PPEItemType]:
        """Get list of validly detected PPE types"""
        return [
            item.item_type 
            for item in self.ppe_items 
            if item.is_valid_detection(min_confidence)
        ]
    
    def get_missing_ppe_types(self, required_ppe: List[PPEItemType], 
                            min_confidence: float = 0.7) -> List[PPEItemType]:
        """Get list of missing PPE types based on requirements"""
        detected_types = set(self.get_detected_ppe_types(min_confidence))
        required_types = set(required_ppe)
        return list(required_types - detected_types)
    
    def calculate_compliance_score(self, required_ppe: List[PPEItemType], 
                                 min_confidence: float = 0.7) -> float:
        """Calculate compliance score (0.0 to 1.0) based on detected PPE"""
        if not required_ppe:
            return 1.0  # No PPE required = fully compliant
        
        if not self.has_valid_ppe_detections(min_confidence):
            return 0.0  # No valid detections = not compliant
        
        detected_types = set(self.get_detected_ppe_types(min_confidence))
        required_types = set(required_ppe)
        
        if not required_types:
            return 1.0
        
        return len(detected_types.intersection(required_types)) / len(required_types)


@dataclass
class FaceDetection:
    """
    Face recognition result with employee information
    
    Represents face detection and recognition results, including both
    recognized employees and unidentified faces.
    Requirement: Associate both recognized and unidentified faces with PPE results.
    """
    employee_id: Optional[str]
    employee_name: Optional[str] 
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    face_encoding: np.ndarray
    detection_timestamp: datetime = field(default_factory=datetime.now)
    is_identified: bool = field(init=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate face detection data and set identification status"""
        if len(self.bounding_box) != 4:
            raise ValueError(f"Bounding box must have 4 coordinates, got {len(self.bounding_box)}")
        
        x1, y1, x2, y2 = self.bounding_box
        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Invalid bounding box coordinates: {self.bounding_box}")
        
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        
        if not isinstance(self.face_encoding, np.ndarray):
            raise ValueError("Face encoding must be a numpy array")
        
        # Set identification status
        self.is_identified = bool(self.employee_id)
    
    def is_valid_recognition(self, min_confidence: float = 0.5) -> bool:
        """Check if face recognition meets minimum confidence threshold"""
        return self.confidence >= min_confidence
    
    def requires_manual_review(self) -> bool:
        """Check if unknown face should be flagged for manual review"""
        return not self.is_identified and self.is_valid_recognition()
    
    def get_display_name(self) -> str:
        """Get display name for UI purposes"""
        if self.employee_name:
            return self.employee_name
        elif self.employee_id:
            return f"Employee {self.employee_id}"
        else:
            return "Unknown Person"


@dataclass
class ViolationEvent:
    """
    Complete violation record with evidence and metadata
    
    Represents a PPE compliance violation with all associated information.
    Requirement: Capture photo evidence only when violations occur.
    """
    timestamp: datetime
    camera_id: str
    employee_id: Optional[str]
    employee_name: Optional[str]
    violation_types: List[ViolationType]
    confidence_score: float
    evidence_photo_path: str  # Only captured when violations occur
    location_zone: str
    person_detection: PersonDetection
    face_detection: Optional[FaceDetection]
    event_id: str = field(default_factory=lambda: f"violation_{datetime.now().timestamp()}")
    
    # Additional metadata
    detection_metadata: Dict[str, Any] = field(default_factory=dict)
    alert_sent: bool = False
    reviewed: bool = False
    reviewer_id: Optional[str] = None
    review_timestamp: Optional[datetime] = None
    severity: str = "medium"  # low, medium, high, critical
    
    def __post_init__(self):
        """Validate violation event data"""
        if not self.violation_types:
            raise ValueError("Violation event must have at least one violation type")
        
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"Confidence score must be between 0.0 and 1.0, got {self.confidence_score}")
        
        if not self.evidence_photo_path:
            raise ValueError("Evidence photo path is required for violation events")
        
        if not self.camera_id:
            raise ValueError("Camera ID is required")
        
        if not self.location_zone:
            raise ValueError("Location zone is required")
    
    def is_repeat_violation(self, previous_violations: List['ViolationEvent'], 
                          time_window_hours: int = 24) -> bool:
        """Check if this is a repeat violation within time window"""
        if not self.employee_id:
            return False
        
        current_time = self.timestamp
        for prev_violation in previous_violations:
            if (prev_violation.employee_id == self.employee_id and
                (current_time - prev_violation.timestamp).total_seconds() < time_window_hours * 3600):
                return True
        
        return False
    
    def get_severity_level(self) -> str:
        """Determine violation severity based on types and context"""
        if ViolationType.MULTIPLE_VIOLATIONS in self.violation_types:
            return "critical"
        
        critical_ppe = {ViolationType.MISSING_HELMET, ViolationType.MISSING_GLASSES}
        violation_types_set = set(self.violation_types)
        
        if violation_types_set.intersection(critical_ppe):
            return "high"
        
        if len(self.violation_types) > 1:
            return "medium"
        
        return "low"
    
    def requires_escalation(self) -> bool:
        """Check if violation requires management escalation"""
        return (self.get_severity_level() in ["high", "critical"] or 
                ViolationType.UNKNOWN_PERSON in self.violation_types)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation event to dictionary for storage/transmission"""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "camera_id": self.camera_id,
            "employee_id": self.employee_id,
            "employee_name": self.employee_name,
            "violation_types": [vt.value for vt in self.violation_types],
            "confidence_score": self.confidence_score,
            "evidence_photo_path": self.evidence_photo_path,
            "location_zone": self.location_zone,
            "severity": self.get_severity_level(),
            "alert_sent": self.alert_sent,
            "reviewed": self.reviewed,
            "detection_metadata": self.detection_metadata
        }


@dataclass 
class EnhancedViolationEvent:
    """
    Enhanced violation event with extended metadata
    
    Extended version of ViolationEvent with additional validation and metadata.
    Requirements: Valid PPE detections, face associations, evidence capture, retention.
    """
    base_violation: ViolationEvent
    valid_ppe_detections: List[PPEDetection]  # Only valid detections used for compliance
    associated_faces: List[FaceDetection]  # Both recognized and unidentified
    evidence_captured: bool  # Only true when violation occurs
    retention_expiry: datetime  # Based on 731-735 days retention
    logging_metadata: Dict[str, Any]  # Always captured logging information
    
    def __post_init__(self):
        """Validate enhanced violation event"""
        # Evidence should only be captured for actual violations
        if not self.base_violation.violation_types and self.evidence_captured:
            raise ValueError("Evidence should only be captured when violations occur")
        
        # Verify valid PPE detections requirement
        if self.base_violation.person_detection.compliance_status == ComplianceStatus.COMPLIANT:
            if not any(det.is_valid_detection() for det in self.valid_ppe_detections):
                raise ValueError("Compliant status requires valid PPE detections")
        
        # Verify retention period within tolerance (731-735 days)
        days_diff = (self.retention_expiry - self.base_violation.timestamp).days
        if not (731 <= days_diff <= 735):
            raise ValueError(f"Retention period {days_diff} days not within 731-735 days tolerance")
        
        # Ensure logging metadata is always present
        if not self.logging_metadata:
            raise ValueError("Logging metadata must always be captured")
    
    def get_all_associated_data(self) -> Dict[str, Any]:
        """Get complete violation data including all associations"""
        return {
            "violation": self.base_violation.to_dict(),
            "valid_ppe_detections": [
                {
                    "item_type": det.item_type.value,
                    "confidence": det.confidence,
                    "bounding_box": det.bounding_box,
                    "is_compliant": det.is_compliant
                }
                for det in self.valid_ppe_detections
            ],
            "associated_faces": [
                {
                    "employee_id": face.employee_id,
                    "employee_name": face.employee_name,
                    "confidence": face.confidence,
                    "is_identified": face.is_identified
                }
                for face in self.associated_faces
            ],
            "evidence_captured": self.evidence_captured,
            "retention_expiry": self.retention_expiry.isoformat(),
            "logging_metadata": self.logging_metadata
        }