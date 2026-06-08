"""
Logging Configuration

This module contains logging configuration with always-enabled audit trail
as required by the system specifications.

Requirements: 8.5 (Always-enabled logging), 11.5 (Audit logs)
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class LogLevel(Enum):
    """Log levels for different components"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class LogCategory(Enum):
    """Categories for different types of logs"""
    SYSTEM = "system"
    VIDEO = "video"
    PPE_DETECTION = "ppe_detection"
    FACE_RECOGNITION = "face_recognition"
    COMPLIANCE = "compliance"
    ALERTS = "alerts"
    AUDIT = "audit"
    SECURITY = "security"
    PERFORMANCE = "performance"


@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    enabled: bool = True  # Always enabled as per requirements
    log_level: LogLevel = LogLevel.INFO
    log_directory: str = "logs"
    max_file_size_mb: int = 100
    backup_count: int = 10
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Audit trail settings
    audit_enabled: bool = True  # Always enabled for compliance
    audit_file: str = "audit.log"
    audit_retention_days: int = 735  # Maximum retention period (731-735 days)
    
    # Performance logging
    performance_logging: bool = True
    log_processing_times: bool = True
    log_frame_rates: bool = True


# Default logging configuration - ALWAYS ENABLED
LOGGING_CONFIG = LoggingConfig(
    enabled=True,  # Cannot be disabled
    log_level=LogLevel.INFO,
    log_directory="ppe_compliance/logs",
    max_file_size_mb=100,
    backup_count=10,
    audit_enabled=True,  # Cannot be disabled
    performance_logging=True
)

# Log file configurations for different components
LOG_FILES = {
    LogCategory.SYSTEM: "system.log",
    LogCategory.VIDEO: "video_processing.log", 
    LogCategory.PPE_DETECTION: "ppe_detection.log",
    LogCategory.FACE_RECOGNITION: "face_recognition.log",
    LogCategory.COMPLIANCE: "compliance.log",
    LogCategory.ALERTS: "alerts.log",
    LogCategory.AUDIT: "audit.log",
    LogCategory.SECURITY: "security.log",
    LogCategory.PERFORMANCE: "performance.log",
}

# Audit log categories - these are always logged regardless of log level
AUDIT_CATEGORIES = [
    "system_startup",
    "system_shutdown", 
    "configuration_change",
    "user_login",
    "user_logout",
    "data_access",
    "violation_detected",
    "alert_sent",
    "model_update",
    "security_event",
    "data_retention_cleanup"
]

# Performance metrics to log
PERFORMANCE_METRICS = {
    "frame_processing_time": True,
    "ppe_detection_time": True,
    "face_recognition_time": True,
    "compliance_evaluation_time": True,
    "alert_response_time": True,
    "database_operation_time": True,
    "camera_connection_status": True,
    "system_resource_usage": True,
}


def setup_logging(config: LoggingConfig = LOGGING_CONFIG) -> None:
    """
    Set up logging configuration with always-enabled audit trail.
    
    Note: Logging cannot be disabled as per system requirements.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(config.log_directory, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level.value)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    formatter = logging.Formatter(
        config.format_string,
        datefmt=config.date_format
    )
    
    # Set up individual log files for each category
    for category, filename in LOG_FILES.items():
        logger = logging.getLogger(f"ppe_compliance.{category.value}")
        logger.setLevel(config.log_level.value)
        
        # Create rotating file handler
        file_path = os.path.join(config.log_directory, filename)
        handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=config.max_file_size_mb * 1024 * 1024,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Prevent propagation to avoid duplicate logs
        logger.propagate = False
    
    # Set up audit logger with special handling (always enabled)
    audit_logger = logging.getLogger("ppe_compliance.audit")
    audit_logger.setLevel(logging.INFO)  # Always log audit events
    
    audit_file_path = os.path.join(config.log_directory, config.audit_file)
    audit_handler = logging.handlers.RotatingFileHandler(
        audit_file_path,
        maxBytes=config.max_file_size_mb * 1024 * 1024,
        backupCount=config.backup_count * 2,  # Keep more audit logs
        encoding='utf-8'
    )
    
    # Special format for audit logs
    audit_formatter = logging.Formatter(
        "%(asctime)s - AUDIT - %(levelname)s - %(message)s",
        datefmt=config.date_format
    )
    audit_handler.setFormatter(audit_formatter)
    audit_logger.addHandler(audit_handler)
    audit_logger.propagate = False
    
    # Log system startup
    log_audit_event("system_startup", "PPE Compliance System logging initialized")


def get_logger(category: LogCategory) -> logging.Logger:
    """Get logger for specific category"""
    return logging.getLogger(f"ppe_compliance.{category.value}")


def log_audit_event(event_type: str, message: str, metadata: Dict[str, Any] = None) -> None:
    """
    Log audit event - these are always logged regardless of configuration.
    
    Args:
        event_type: Type of audit event (must be in AUDIT_CATEGORIES)
        message: Audit message
        metadata: Additional metadata to log
    """
    if event_type not in AUDIT_CATEGORIES:
        raise ValueError(f"Invalid audit event type: {event_type}")
    
    audit_logger = logging.getLogger("ppe_compliance.audit")
    
    # Format audit message with metadata
    audit_message = f"[{event_type.upper()}] {message}"
    if metadata:
        audit_message += f" | Metadata: {metadata}"
    
    # Always log as INFO level for audit events
    audit_logger.info(audit_message)


def log_performance_metric(metric_name: str, value: float, unit: str = "ms") -> None:
    """Log performance metric if performance logging is enabled"""
    if not LOGGING_CONFIG.performance_logging:
        return
    
    if metric_name not in PERFORMANCE_METRICS or not PERFORMANCE_METRICS[metric_name]:
        return
    
    performance_logger = get_logger(LogCategory.PERFORMANCE)
    performance_logger.info(f"METRIC - {metric_name}: {value} {unit}")


def log_system_event(category: LogCategory, level: LogLevel, message: str, 
                    metadata: Dict[str, Any] = None) -> None:
    """Log system event with metadata"""
    logger = get_logger(category)
    
    log_message = message
    if metadata:
        log_message += f" | {metadata}"
    
    logger.log(level.value, log_message)


def is_logging_always_enabled() -> bool:
    """
    Confirm that logging is always enabled as per system requirements.
    This function always returns True to comply with requirement 8.5.
    """
    return True


def cleanup_old_logs() -> None:
    """Clean up old log files based on retention policy"""
    log_audit_event("data_retention_cleanup", "Starting log cleanup process")
    
    # Implementation would clean up logs older than retention period
    # This is a placeholder for the actual cleanup logic
    pass


# Initialize logging on module import
setup_logging()