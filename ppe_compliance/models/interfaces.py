"""
Abstract Base Classes and Interfaces for PPE Compliance Monitoring System

This module defines the abstract base classes and interfaces that define
the contract for core system components.

Requirements: 2.1, 3.1, 4.2, 10.2, 11.2
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime

from .core import (
    PersonDetection, FaceDetection, ViolationEvent,
    ComplianceStatus, ViolationType
)
from .config import ModelDeploymentConfig


class VideoStreamProcessor(ABC):
    """
    Abstract base class for video stream processing and camera management

    Manages CCTV camera connections, video stream ingestion, and frame preprocessing
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
    """

    @abstractmethod
    def initialize_cameras(self, camera_configs: List[Dict[str, Any]]) -> bool:
        """
        Initialize multiple CCTV camera connections

        Args:
            camera_configs: List of camera configuration dictionaries

        Returns:
            bool: True if all cameras initialized successfully
        """
        pass

    @abstractmethod
    def get_next_frame(self, camera_id: str) -> Tuple[bool, np.ndarray, Dict[str, Any]]:
        """
        Get next frame from specified camera with metadata

        Args:
            camera_id: Identifier for the camera

        Returns:
            Tuple of (success, frame, metadata)
            - success: Whether frame was retrieved successfully
            - frame: Video frame as numpy array
            - metadata: Frame metadata (timestamp, camera info, etc.)
        """
        pass

    @abstractmethod
    def preprocess_frame(self, frame: np.ndarray, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        Preprocess frame for AI analysis (resize, normalize, etc.)
        Requirement: Complete preprocessing within 50 milliseconds

        Args:
            frame: Input video frame
            target_size: Optional target size for resizing

        Returns:
            Preprocessed frame optimized for AI analysis
        """
        pass

    @abstractmethod
    def get_camera_status(self, camera_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of cameras (connection, frame rate, etc.)

        Args:
            camera_id: Optional specific camera ID, if None returns all cameras

        Returns:
            Dictionary with camera status information
        """
        pass

    @abstractmethod
    def handle_connection_failure(self, camera_id: str) -> bool:
        """
        Handle camera connection failure and attempt reconnection
        Requirement: Attempt reconnection within 30 seconds

        Args:
            camera_id: ID of failed camera

        Returns:
            bool: True if reconnection successful
        """
        pass

    @abstractmethod
    def release_resources(self) -> None:
        """Clean up camera connections and resources"""
        pass

    @abstractmethod
    def supports_protocol(self, protocol: str) -> bool:
        """
        Check if processor supports specific camera protocol
        Required protocols: USB, IP, RTSP

        Args:
            protocol: Camera protocol name

        Returns:
            bool: True if protocol is supported
        """
        pass


class PPEDetector(ABC):
    """
    Abstract base class for PPE detection using computer vision models

    Detects personal protective equipment items and evaluates compliance
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
    """

    @abstractmethod
    def load_model(self, model_path: str, config: Dict[str, Any]) -> bool:
        """
        Load PPE detection model

        Args:
            model_path: Path to model file
            config: Model configuration parameters

        Returns:
            bool: True if model loaded successfully
        """
        pass

    @abstractmethod
    def detect_ppe_items(self, frame: np.ndarray) -> List[PersonDetection]:
        """
        Detect PPE items and persons in the frame
        Requirement: Process all individuals within 200 milliseconds

        Args:
            frame: Input video frame

        Returns:
            List of PersonDetection objects with associated PPE items
        """
        pass

    @abstractmethod
    def evaluate_compliance(self, person: PersonDetection,
                          required_ppe: List[str], zone_config: Dict[str, Any]) -> ComplianceStatus:
        """
        Evaluate if person meets PPE compliance requirements
        Requirement: Requires valid PPE detections before marking compliance as met

        Args:
            person: PersonDetection object to evaluate
            required_ppe: List of required PPE items for the zone
            zone_config: Zone-specific configuration

        Returns:
            ComplianceStatus enum value
        """
        pass

    @abstractmethod
    def has_valid_ppe_detections(self, person: PersonDetection,
                                min_confidence: float = 0.7) -> bool:
        """
        Check if person has valid PPE detections before marking compliance as met
        Requirement: Valid detections required for compliance evaluation

        Args:
            person: PersonDetection to validate
            min_confidence: Minimum confidence threshold

        Returns:
            bool: True if person has valid PPE detections
        """
        pass

    @abstractmethod
    def get_supported_ppe_types(self) -> List[str]:
        """
        Get list of PPE types supported by the model
        Required types: helmet, safety_glasses, work_uniform, gloves, safety_vest

        Returns:
            List of supported PPE type names
        """
        pass

    @abstractmethod
    def update_model(self, new_model_path: str,
                    deployment_config: ModelDeploymentConfig) -> bool:
        """
        Update PPE detection model with compatibility validation
        Requirement: Block deployment when compatibility breaks

        Args:
            new_model_path: Path to new model
            deployment_config: Deployment configuration and validation settings

        Returns:
            bool: True if update successful
        """
        pass


class FaceRecognizer(ABC):
    """
    Abstract base class for enhanced face recognition system

    Identifies employees even when wearing PPE, handling partial occlusion
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """

    @abstractmethod
    def load_employee_database(self, db_path: str) -> bool:
        """
        Load employee database with photos and metadata
        Requirement: Support database updates without system restart

        Args:
            db_path: Path to employee database

        Returns:
            bool: True if database loaded successfully
        """
        pass

    @abstractmethod
    def recognize_faces(self, frame: np.ndarray) -> List[FaceDetection]:
        """
        Recognize faces in frame and return employee information
        Requirement: Maintain recognition accuracy above 85% with PPE interference

        Args:
            frame: Input video frame

        Returns:
            List of FaceDetection objects (both recognized and unidentified)
        """
        pass

    @abstractmethod
    def associate_face_with_ppe(self, faces: List[FaceDetection],
                               persons: List[PersonDetection]) -> Dict[str, Any]:
        """
        Associate detected faces with PPE compliance status
        Requirement: Includes both recognized and unidentified faces

        Args:
            faces: List of detected faces
            persons: List of detected persons with PPE information

        Returns:
            Dictionary mapping faces to persons and compliance status
        """
        pass

    @abstractmethod
    def add_employee(self, employee_id: str, name: str,
                    photo_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Add new employee to recognition database

        Args:
            employee_id: Unique employee identifier
            name: Employee name
            photo_path: Path to employee photo
            metadata: Additional employee metadata

        Returns:
            bool: True if employee added successfully
        """
        pass

    @abstractmethod
    def handle_unknown_face(self, face_detection: FaceDetection) -> Dict[str, Any]:
        """
        Log unknown face for manual review
        Requirement: Log unknown faces for manual review processes

        Args:
            face_detection: FaceDetection object for unknown person

        Returns:
            Dictionary with logging and review information
        """
        pass

    @abstractmethod
    def update_employee_database(self, updates: List[Dict[str, Any]]) -> bool:
        """
        Update employee database without system restart
        Requirement: Load and process employee database updates without system restart

        Args:
            updates: List of employee updates (add, modify, delete)

        Returns:
            bool: True if updates applied successfully
        """
        pass


class ComplianceEngine(ABC):
    """
    Abstract base class for compliance evaluation and violation management

    Core logic engine that evaluates PPE compliance and triggers appropriate actions
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """

    @abstractmethod
    def evaluate_frame_compliance(self, faces: List[FaceDetection],
                                 persons: List[PersonDetection],
                                 camera_metadata: Dict[str, Any]) -> List[ViolationEvent]:
        """
        Evaluate compliance for all persons in frame

        Args:
            faces: Detected faces in frame
            persons: Detected persons with PPE information
            camera_metadata: Camera and frame metadata

        Returns:
            List of ViolationEvent objects for any violations found
        """
        pass

    @abstractmethod
    def apply_compliance_rules(self, person: PersonDetection,
                              face: Optional[FaceDetection],
                              zone_config: Dict[str, Any]) -> Optional[ViolationEvent]:
        """
        Apply configured compliance rules to individual

        Args:
            person: PersonDetection to evaluate
            face: Optional associated FaceDetection
            zone_config: Zone-specific compliance configuration

        Returns:
            ViolationEvent if violation found, None if compliant
        """
        pass

    @abstractmethod
    def capture_photo_evidence(self, frame: np.ndarray,
                              violation: ViolationEvent) -> str:
        """
        Capture photo evidence only when violations occur
        Requirement: Capture photo evidence with bounding boxes only when violations occur

        Args:
            frame: Video frame containing violation
            violation: ViolationEvent details

        Returns:
            Path to captured evidence photo
        """
        pass

    @abstractmethod
    def should_trigger_alert(self, violation: ViolationEvent,
                            violation_history: List[ViolationEvent]) -> bool:
        """
        Determine if alert should be triggered based on cooldown and history

        Args:
            violation: Current violation event
            violation_history: Previous violations for context

        Returns:
            bool: True if alert should be triggered
        """
        pass

    @abstractmethod
    def update_violation_history(self, violation: ViolationEvent) -> None:
        """
        Update employee violation history for trending analysis
        Requirement: Track violation history for trend analysis

        Args:
            violation: ViolationEvent to add to history
        """
        pass

    @abstractmethod
    def get_zone_requirements(self, zone_name: str) -> Dict[str, Any]:
        """
        Get PPE requirements for specific zone
        Requirement: Support different PPE requirements based on facility zones

        Args:
            zone_name: Name of the zone/area

        Returns:
            Dictionary with zone-specific PPE requirements
        """
        pass


class AlertSystem(ABC):
    """
    Abstract base class for alert and notification management

    Manages real-time notifications, dashboard updates, and alert routing
    Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
    """

    @abstractmethod
    def send_violation_alert(self, violation: ViolationEvent,
                           notification_channels: List[str]) -> bool:
        """
        Send immediate alert for violation event
        Requirement: Send notifications within 5 seconds through configured channels

        Args:
            violation: ViolationEvent to alert about
            notification_channels: List of channels (email, sms, dashboard)

        Returns:
            bool: True if alert sent successfully
        """
        pass

    @abstractmethod
    def generate_alert_content(self, violation: ViolationEvent) -> Dict[str, Any]:
        """
        Generate alert content with employee information and photo evidence
        Requirement: Include employee information, violation type, and photo evidence

        Args:
            violation: ViolationEvent to generate content for

        Returns:
            Dictionary with formatted alert content for different channels
        """
        pass

    @abstractmethod
    def escalate_to_management(self, violation: ViolationEvent,
                              escalation_level: str) -> bool:
        """
        Escalate critical violations to management with higher priority
        Requirement: Escalate to management with higher priority for critical violations

        Args:
            violation: ViolationEvent to escalate
            escalation_level: Level of escalation (medium, high, critical)

        Returns:
            bool: True if escalation successful
        """
        pass

    @abstractmethod
    def check_cooldown_period(self, employee_id: Optional[str],
                             violation_type: ViolationType) -> bool:
        """
        Check if alert is in cooldown period to prevent spam
        Requirement: Implement cooldown periods to prevent alert spam

        Args:
            employee_id: Employee ID (if known)
            violation_type: Type of violation

        Returns:
            bool: True if still in cooldown period (should not send alert)
        """
        pass

    @abstractmethod
    def update_dashboard(self, camera_status: Dict[str, Any],
                        violations: List[ViolationEvent]) -> None:
        """
        Update real-time compliance dashboard

        Args:
            camera_status: Current status of all cameras
            violations: Recent violations for dashboard display
        """
        pass


class DataStorageManager(ABC):
    """
    Abstract base class for data storage and management

    Manages violation data storage, retention, and access controls
    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """

    @abstractmethod
    def store_violation_event(self, violation: ViolationEvent) -> bool:
        """
        Store violation event with complete metadata
        Requirement: Store all Violation_Events with complete metadata in database

        Args:
            violation: ViolationEvent to store

        Returns:
            bool: True if stored successfully
        """
        pass

    @abstractmethod
    def store_photo_evidence(self, photo_data: bytes,
                           violation_id: str) -> str:
        """
        Store photo evidence with proper file management
        Requirement: Include photo evidence and maintain data integrity

        Args:
            photo_data: Photo data as bytes
            violation_id: ID of associated violation

        Returns:
            str: Path to stored photo file
        """
        pass

    @abstractmethod
    def apply_retention_policy(self, retention_days_min: int = 731,
                              retention_days_max: int = 735) -> Dict[str, int]:
        """
        Apply data retention policy with operational tolerance
        Requirement: Retain violation data for 731-735 days with tolerance

        Args:
            retention_days_min: Minimum retention period
            retention_days_max: Maximum retention period

        Returns:
            Dictionary with retention statistics (archived, deleted counts)
        """
        pass

    @abstractmethod
    def enforce_access_controls(self, user_id: str,
                               requested_data: str) -> bool:
        """
        Enforce role-based access controls for stored data
        Requirement: Enforce role-based access controls when accessing stored data

        Args:
            user_id: ID of user requesting access
            requested_data: Type or ID of requested data

        Returns:
            bool: True if access granted
        """
        pass

    @abstractmethod
    def backup_violation_data(self) -> bool:
        """
        Backup violation data to prevent data loss
        Requirement: Backup violation data daily to prevent data loss

        Returns:
            bool: True if backup successful
        """
        pass


class ReportingSystem(ABC):
    """
    Abstract base class for dashboard and reporting functionality

    Provides real-time dashboard and comprehensive reporting capabilities
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """

    @abstractmethod
    def update_realtime_dashboard(self, compliance_status: Dict[str, Any],
                                 violations: List[ViolationEvent]) -> None:
        """
        Update real-time dashboard showing current compliance status
        Requirement: Update dashboard immediately with visual indicators

        Args:
            compliance_status: Current compliance status across all cameras
            violations: Recent violations for display
        """
        pass

    @abstractmethod
    def generate_compliance_report(self, start_date: datetime,
                                  end_date: datetime,
                                  report_type: str) -> Dict[str, Any]:
        """
        Generate comprehensive compliance reports
        Requirement: Generate daily, weekly, and monthly compliance reports

        Args:
            start_date: Report start date
            end_date: Report end date
            report_type: Type of report (daily, weekly, monthly)

        Returns:
            Dictionary with complete report data
        """
        pass

    @abstractmethod
    def mark_missing_sections(self, report_data: Dict[str, Any],
                             missing_components: List[str]) -> Dict[str, Any]:
        """
        Mark missing sections clearly when partial reports are generated
        Requirement: Clearly mark missing sections when components unavailable

        Args:
            report_data: Report data to modify
            missing_components: List of missing component names

        Returns:
            Report data with missing sections clearly marked
        """
        pass

    @abstractmethod
    def export_report(self, report_data: Dict[str, Any],
                     format_type: str, output_path: str) -> str:
        """
        Export reports in PDF and Excel formats for external sharing
        Requirement: Export reports in PDF and Excel formats

        Args:
            report_data: Report data to export
            format_type: Export format (pdf, excel)
            output_path: Path for exported file

        Returns:
            Path to exported report file
        """
        pass
