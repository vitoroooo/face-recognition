"""
Data models and interfaces for PPE Compliance System

This module provides core data models, configuration models, and abstract interfaces
for the PPE compliance monitoring system.

Requirements: 2.1, 3.1, 4.2, 10.2, 11.2
"""

# Core data models
from .core import (
    PPEDetection,
    PersonDetection, 
    FaceDetection,
    ViolationEvent,
    EnhancedViolationEvent,
    ViolationType,
    ComplianceStatus
)

# Configuration models
from .config import (
    SecurityConfig,
    ModelDeploymentConfig,
    PPEComplianceConfig,
    SystemRestartConfig,
    TLSVersion,
    EncryptionStandard,
    AuthenticationMode
)

# Abstract interfaces
from .interfaces import (
    VideoStreamProcessor,
    PPEDetector,
    FaceRecognizer,
    ComplianceEngine,
    AlertSystem,
    DataStorageManager,
    ReportingSystem
)

__all__ = [
    # Core data models
    'PPEDetection',
    'PersonDetection',
    'FaceDetection', 
    'ViolationEvent',
    'EnhancedViolationEvent',
    'ViolationType',
    'ComplianceStatus',
    
    # Configuration models
    'SecurityConfig',
    'ModelDeploymentConfig',
    'PPEComplianceConfig',
    'SystemRestartConfig',
    'TLSVersion',
    'EncryptionStandard',
    'AuthenticationMode',
    
    # Abstract interfaces
    'VideoStreamProcessor',
    'PPEDetector',
    'FaceRecognizer',
    'ComplianceEngine',
    'AlertSystem',
    'DataStorageManager',
    'ReportingSystem',
]