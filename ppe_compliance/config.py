"""
PPE Compliance System Configuration

Main configuration module that provides unified access to all system configurations.
This module integrates PPE detection rules, camera settings, logging configuration,
and system-wide settings with always-enabled audit trail.

Requirements: 8.5, 10.1
"""

from .config.main_config import (
    SYSTEM_CONFIG,
    MAIN_CONFIG,
    load_config,
    get_config_value,
    update_config_value,
    validate_configuration,
    get_environment_config,
    is_critical_change,
    export_config
)

from .config.ppe_detection_config import (
    PPE_DETECTION_CONFIG,
    ZONE_CONFIGURATIONS,
    PPEItemType,
    PPEZoneConfig,
    get_zone_config,
    validate_ppe_combination,
    is_critical_configuration_change
)

from .config.camera_config import (
    CAMERA_SYSTEM_CONFIG,
    CAMERA_CONFIGURATIONS,
    NETWORK_CONFIG,
    CameraProtocol,
    CameraConfig,
    get_camera_config,
    get_cameras_by_zone,
    get_critical_cameras,
    validate_camera_config,
    get_zone_from_camera
)

from .config.logging_config import (
    LOGGING_CONFIG,
    LogLevel,
    LogCategory,
    setup_logging,
    get_logger,
    log_audit_event,
    log_performance_metric,
    log_system_event,
    is_logging_always_enabled,
    cleanup_old_logs
)

# Initialize logging when this module is imported
# This ensures logging is always enabled from system start
setup_logging()

# Log system initialization
log_audit_event("system_startup", "PPE Compliance configuration module initialized")

__all__ = [
    # Main configuration
    'SYSTEM_CONFIG',
    'MAIN_CONFIG',
    'load_config',
    'get_config_value',
    'update_config_value',
    'validate_configuration',
    'get_environment_config',
    'is_critical_change',
    'export_config',
    
    # PPE detection configuration
    'PPE_DETECTION_CONFIG',
    'ZONE_CONFIGURATIONS',
    'PPEItemType',
    'PPEZoneConfig',
    'get_zone_config',
    'validate_ppe_combination',
    'is_critical_configuration_change',
    
    # Camera configuration
    'CAMERA_SYSTEM_CONFIG',
    'CAMERA_CONFIGURATIONS',
    'NETWORK_CONFIG',
    'CameraProtocol',
    'CameraConfig',
    'get_camera_config',
    'get_cameras_by_zone',
    'get_critical_cameras',
    'validate_camera_config',
    'get_zone_from_camera',
    
    # Logging configuration
    'LOGGING_CONFIG',
    'LogLevel',
    'LogCategory',
    'setup_logging',
    'get_logger',
    'log_audit_event',
    'log_performance_metric',
    'log_system_event',
    'is_logging_always_enabled',
    'cleanup_old_logs',
]