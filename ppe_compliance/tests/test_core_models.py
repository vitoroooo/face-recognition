"""
Unit tests for core data models

Tests the core data models to ensure they work correctly and validate
data according to requirements.

Requirements: 2.1, 3.1, 4.2, 10.2, 11.2
"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from typing import List

from ..models.core import (
    PPEDetection, PersonDetection, FaceDetection, ViolationEvent,
    EnhancedViolationEvent, ViolationType, ComplianceStatus
)
from ..config.ppe_detection_config import PPEItemType


class TestPPEDetection:
    """Test PPE detection data model"""
    
    def test_valid_ppe_detection_creation(self):
        """Test creating valid PPE detection"""
        detection = PPEDetection(
            item_type=PPEItemType.HELMET,
            confidence=0.85,
            bounding_box=(10, 20, 100, 200),
            is_compliant=True
        )
        
        assert detection.item_type == PPEItemType.HELMET
        assert detection.confidence == 0.85
        assert detection.bounding_box == (10, 20, 100, 200)
        assert detection.is_compliant is True
        assert detection.is_valid_detection(0.7) is True
    
    def test_invalid_confidence_raises_error(self):
        """Test that invalid confidence values raise errors"""
        with pytest.raises(ValueError, match="Confidence must be between 0.0 and 1.0"):
            PPEDetection(
                item_type=PPEItemType.HELMET,
                confidence=1.5,  # Invalid confidence
                bounding_box=(10, 20, 100, 200),
                is_compliant=True
            )
    
    def test_invalid_bounding_box_raises_error(self):
        """Test that invalid bounding box raises error"""
        with pytest.raises(ValueError, match="Invalid bounding box coordinates"):
            PPEDetection(
                item_type=PPEItemType.HELMET,
                confidence=0.8,
                bounding_box=(100, 20, 10, 200),  # x1 > x2
                is_compliant=True
            )
    
    def test_detection_area_calculation(self):
        """Test bounding box area calculation"""
        detection = PPEDetection(
            item_type=PPEItemType.HELMET,
            confidence=0.8,
            bounding_box=(10, 20, 60, 120),
            is_compliant=True
        )
        
        expected_area = (60 - 10) * (120 - 20)  # 50 * 100 = 5000
        assert detection.get_detection_area() == expected_area


class TestPersonDetection:
    """Test person detection data model"""
    
    def test_valid_person_detection_creation(self):
        """Test creating valid person detection"""
        ppe_items = [
            PPEDetection(PPEItemType.HELMET, 0.9, (10, 10, 50, 50), True),
            PPEDetection(PPEItemType.SAFETY_GLASSES, 0.8, (15, 15, 45, 35), True)
        ]
        
        person = PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=ppe_items,
            compliance_status=ComplianceStatus.COMPLIANT,
            confidence=0.95
        )
        
        assert person.person_id == 1
        assert len(person.ppe_items) == 2
        assert person.compliance_status == ComplianceStatus.COMPLIANT
        assert person.has_valid_ppe_detections() is True
    
    def test_get_detected_ppe_types(self):
        """Test getting detected PPE types"""
        ppe_items = [
            PPEDetection(PPEItemType.HELMET, 0.9, (10, 10, 50, 50), True),
            PPEDetection(PPEItemType.SAFETY_GLASSES, 0.6, (15, 15, 45, 35), True),  # Below threshold
            PPEDetection(PPEItemType.WORK_UNIFORM, 0.8, (20, 20, 80, 180), True)
        ]
        
        person = PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=ppe_items,
            compliance_status=ComplianceStatus.COMPLIANT
        )
        
        detected_types = person.get_detected_ppe_types(min_confidence=0.7)
        expected_types = [PPEItemType.HELMET, PPEItemType.WORK_UNIFORM]
        
        assert set(detected_types) == set(expected_types)
    
    def test_calculate_compliance_score(self):
        """Test compliance score calculation"""
        # Person with helmet and uniform detected
        ppe_items = [
            PPEDetection(PPEItemType.HELMET, 0.9, (10, 10, 50, 50), True),
            PPEDetection(PPEItemType.WORK_UNIFORM, 0.8, (20, 20, 80, 180), True)
        ]
        
        person = PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=ppe_items,
            compliance_status=ComplianceStatus.PARTIAL
        )
        
        # Required: helmet, uniform, safety_glasses
        required_ppe = [PPEItemType.HELMET, PPEItemType.WORK_UNIFORM, PPEItemType.SAFETY_GLASSES]
        
        score = person.calculate_compliance_score(required_ppe)
        assert score == 2/3  # 2 out of 3 required items detected
    
    def test_no_valid_detections_returns_false(self):
        """Test that person with no valid detections returns false for has_valid_ppe_detections"""
        ppe_items = [
            PPEDetection(PPEItemType.HELMET, 0.5, (10, 10, 50, 50), True),  # Below threshold
        ]
        
        person = PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=ppe_items,
            compliance_status=ComplianceStatus.INVALID_DETECTION
        )
        
        assert person.has_valid_ppe_detections(min_confidence=0.7) is False


class TestFaceDetection:
    """Test face detection data model"""
    
    def test_valid_face_detection_creation(self):
        """Test creating valid face detection"""
        face_encoding = np.random.rand(128)  # Typical face encoding size
        
        face = FaceDetection(
            employee_id="EMP001",
            employee_name="John Doe",
            confidence=0.85,
            bounding_box=(20, 30, 80, 100),
            face_encoding=face_encoding
        )
        
        assert face.employee_id == "EMP001"
        assert face.employee_name == "John Doe"
        assert face.is_identified is True
        assert face.is_valid_recognition(0.5) is True
        assert face.requires_manual_review() is False
    
    def test_unknown_face_requires_manual_review(self):
        """Test that unknown faces require manual review"""
        face_encoding = np.random.rand(128)
        
        face = FaceDetection(
            employee_id=None,
            employee_name=None,
            confidence=0.75,
            bounding_box=(20, 30, 80, 100),
            face_encoding=face_encoding
        )
        
        assert face.is_identified is False
        assert face.requires_manual_review() is True
        assert face.get_display_name() == "Unknown Person"
    
    def test_invalid_face_encoding_raises_error(self):
        """Test that non-numpy array face encoding raises error"""
        with pytest.raises(ValueError, match="Face encoding must be a numpy array"):
            FaceDetection(
                employee_id="EMP001",
                employee_name="John Doe",
                confidence=0.85,
                bounding_box=(20, 30, 80, 100),
                face_encoding=[1, 2, 3, 4]  # List instead of numpy array
            )


class TestViolationEvent:
    """Test violation event data model"""
    
    def create_sample_person_detection(self) -> PersonDetection:
        """Helper method to create sample person detection"""
        ppe_items = [
            PPEDetection(PPEItemType.WORK_UNIFORM, 0.8, (20, 20, 80, 180), True)
        ]
        
        return PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=ppe_items,
            compliance_status=ComplianceStatus.VIOLATION
        )
    
    def create_sample_face_detection(self) -> FaceDetection:
        """Helper method to create sample face detection"""
        return FaceDetection(
            employee_id="EMP001",
            employee_name="John Doe",
            confidence=0.85,
            bounding_box=(20, 30, 80, 100),
            face_encoding=np.random.rand(128)
        )
    
    def test_valid_violation_event_creation(self):
        """Test creating valid violation event"""
        person = self.create_sample_person_detection()
        face = self.create_sample_face_detection()
        
        violation = ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001",
            employee_name="John Doe",
            violation_types=[ViolationType.MISSING_HELMET],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_001.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=face
        )
        
        assert violation.camera_id == "CAM001"
        assert len(violation.violation_types) == 1
        assert violation.violation_types[0] == ViolationType.MISSING_HELMET
        assert violation.evidence_photo_path == "/evidence/violation_001.jpg"
        assert violation.get_severity_level() == "high"  # Missing helmet is critical PPE
    
    def test_violation_severity_levels(self):
        """Test violation severity level calculation"""
        person = self.create_sample_person_detection()
        
        # Multiple violations = critical
        violation_critical = ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001",
            employee_name="John Doe",
            violation_types=[ViolationType.MULTIPLE_VIOLATIONS],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_001.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=None
        )
        assert violation_critical.get_severity_level() == "critical"
        
        # Missing helmet = high
        violation_high = ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001", 
            employee_name="John Doe",
            violation_types=[ViolationType.MISSING_HELMET],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_002.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=None
        )
        assert violation_high.get_severity_level() == "high"
        
        # Single non-critical violation = low
        violation_low = ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001",
            employee_name="John Doe", 
            violation_types=[ViolationType.MISSING_GLOVES],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_003.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=None
        )
        assert violation_low.get_severity_level() == "low"
    
    def test_requires_escalation(self):
        """Test escalation requirement logic"""
        person = self.create_sample_person_detection()
        
        # High severity violation should require escalation
        violation = ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001",
            employee_name="John Doe",
            violation_types=[ViolationType.MISSING_HELMET],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_001.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=None
        )
        
        assert violation.requires_escalation() is True
    
    def test_empty_violation_types_raises_error(self):
        """Test that empty violation types list raises error"""
        person = self.create_sample_person_detection()
        
        with pytest.raises(ValueError, match="Violation event must have at least one violation type"):
            ViolationEvent(
                timestamp=datetime.now(),
                camera_id="CAM001",
                employee_id="EMP001",
                employee_name="John Doe",
                violation_types=[],  # Empty list
                confidence_score=0.9,
                evidence_photo_path="/evidence/violation_001.jpg",
                location_zone="manufacturing_floor",
                person_detection=person,
                face_detection=None
            )


class TestEnhancedViolationEvent:
    """Test enhanced violation event model"""
    
    def create_sample_violation_event(self) -> ViolationEvent:
        """Helper to create sample violation event"""
        person = PersonDetection(
            person_id=1,
            bounding_box=(5, 5, 100, 200),
            ppe_items=[],
            compliance_status=ComplianceStatus.VIOLATION
        )
        
        return ViolationEvent(
            timestamp=datetime.now(),
            camera_id="CAM001",
            employee_id="EMP001",
            employee_name="John Doe",
            violation_types=[ViolationType.MISSING_HELMET],
            confidence_score=0.9,
            evidence_photo_path="/evidence/violation_001.jpg",
            location_zone="manufacturing_floor",
            person_detection=person,
            face_detection=None
        )
    
    def test_valid_enhanced_violation_creation(self):
        """Test creating valid enhanced violation event"""
        base_violation = self.create_sample_violation_event()
        
        valid_ppe_detections = [
            PPEDetection(PPEItemType.WORK_UNIFORM, 0.8, (20, 20, 80, 180), True)
        ]
        
        associated_faces = [
            FaceDetection(
                employee_id="EMP001",
                employee_name="John Doe",
                confidence=0.85,
                bounding_box=(20, 30, 80, 100),
                face_encoding=np.random.rand(128)
            )
        ]
        
        enhanced_violation = EnhancedViolationEvent(
            base_violation=base_violation,
            valid_ppe_detections=valid_ppe_detections,
            associated_faces=associated_faces,
            evidence_captured=True,
            retention_expiry=base_violation.timestamp + timedelta(days=732),
            logging_metadata={"camera_fps": 30, "processing_time_ms": 150}
        )
        
        assert len(enhanced_violation.valid_ppe_detections) == 1
        assert len(enhanced_violation.associated_faces) == 1
        assert enhanced_violation.evidence_captured is True
        assert enhanced_violation.logging_metadata["camera_fps"] == 30
    
    def test_retention_period_validation(self):
        """Test that retention period must be within tolerance"""
        base_violation = self.create_sample_violation_event()
        
        # Too short retention period
        with pytest.raises(ValueError, match="Retention period .* not within 731-735 days tolerance"):
            EnhancedViolationEvent(
                base_violation=base_violation,
                valid_ppe_detections=[],
                associated_faces=[],
                evidence_captured=True,
                retention_expiry=base_violation.timestamp + timedelta(days=700),  # Too short
                logging_metadata={"test": "data"}
            )
    
    def test_logging_metadata_required(self):
        """Test that logging metadata is always required"""
        base_violation = self.create_sample_violation_event()
        
        with pytest.raises(ValueError, match="Logging metadata must always be captured"):
            EnhancedViolationEvent(
                base_violation=base_violation,
                valid_ppe_detections=[],
                associated_faces=[],
                evidence_captured=True,
                retention_expiry=base_violation.timestamp + timedelta(days=732),
                logging_metadata={}  # Empty metadata
            )