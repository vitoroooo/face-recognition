"""
Main Configuration

Central configuration module that combines all system configurations
and provides unified access to configuration settings.

Requirements: 8.5, 10.1, 10.2, 11.2
"""

import os
from typing import Dict, Any
from dataclasses import dataclass, asdict
from .ppe_detection_config import PPE_DETECTION_CONFIG, ZONE_CONFIGURATIONS, CONFIGURATION_VALIDATION
from .camera_config import CAMERA_SYSTEM_CONFIG, CAMERA_CONFIGURATIONS, NETWORK_CONFIG
from .logging_config import LOGGING_CONFIG, is_logging_always_enabled


@dataclass
class SystemConfig:
    """Main system configuration"""
    # System identification
    system_name: str = "PPE Compliance Monitoring System"
    version: str = "1.0.0"
    environment: str = "production"  # production, development, testing

    # Performance requirements
    uptime_target: float = 99.5  # 99.5% uptime requirement
    max_concurrent_cameras: int = 8
    auto_recovery_timeout: int = 60  # Recovery within 60 seconds

    # Data retention (731-735 days tolerance)
    data_retention_min_days: int = 731
    data_retention_max_days: int = 735

    # Security settings
    encryption_required: bool = True
    tls_version_preferred: str = "1.3"
    tls_fallback_allowed: bool = True  # Allow TLS 1.2 when 1.3 unavailable
    video_processing_auth_bypass: bool = True  # Process video regardless of auth status

    # Integration settings
    extend_existing_face_recognition: bool = True
    maintain_existing_functionality: bool = True

    # Configuration management
    allow_runtime_config_changes: bool = True
    restart_required_for_critical_changes: bool = True


# Global system configuration instance
SYSTEM_CONFIG = SystemConfig()

# Consolidated configuration dictionary
MAIN_CONFIG = {
    "system": asdict(SYSTEM_CONFIG),
    "ppe_detection": PPE_DETECTION_CONFIG,
    "cameras": CAMERA_SYSTEM_CONFIG,
    "camera_instances": {k: asdict(v) for k, v in CAMERA_CONFIGURATIONS.items()},
    "zones": {k: asdict(v) for k, v in ZONE_CONFIGURATIONS.items()},
    "network": NETWORK_CONFIG,
    "logging": asdict(LOGGING_CONFIG),
    "validation": CONFIGURATION_VALIDATION,
}

# Environment-specific overrides
ENVIRONMENT_OVERRIDES = {
    "development": {
        "system": {
            "uptime_target": 95.0,
            "max_concurrent_cameras": 4,
        },
        "ppe_detection": {
            "confidence_threshold": 0.6,  # Lower threshold for testing
        },
        "logging": {
            "log_level": "DEBUG",
        }
    },

    "testing": {
        "system": {
            "uptime_target": 90.0,
            "max_concurrent_cameras": 2,
            "data_retention_min_days": 1,  # Short retention for testing
            "data_retention_max_days": 7,
        },
        "cameras": {
            "connection_timeout_seconds": 5,  # Faster timeouts for tests
        }
    }
}


def load_config(environment: str = None) -> Dict[str, Any]:
    """
    Load configuration with environment-specific overrides

    Args:
        environment: Environment name (development, testing, production)

    Returns:
        Complete configuration dictionary
    """
    config = MAIN_CONFIG.copy()

    # Apply environment overrides if specified
    if environment and environment in ENVIRONMENT_OVERRIDES:
        overrides = ENVIRONMENT_OVERRIDES[environment]
        for section, settings in overrides.items():
            if section in config:
                config[section].update(settings)

    # Ensure logging is always enabled (requirement 8.5)
    config["logging"]["enabled"] = True
    config["logging"]["audit_enabled"] = True

    return config


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using dot notation

    Args:
        key_path: Path to configuration value (e.g., 'system.version')
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    config = load_config(os.getenv("PPE_ENVIRONMENT", "production"))

    keys = key_path.split('.')
    value = config

    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def update_config_value(key_path: str, new_value: Any) -> bool:
    """
    Update configuration value and check if restart is required

    Args:
        key_path: Path to configuration value
        new_value: New value to set

    Returns:
        True if restart is required, False otherwise
    """
    # Check if this is a critical configuration change
    critical_settings = CONFIGURATION_VALIDATION.get("critical_safety_settings", [])

    # Extract the setting name from the key path
    setting_name = key_path.split('.')[-1]

    # Update the configuration (in a real implementation, this would persist)
    # For now, we just check if restart is required

    if setting_name in critical_settings:
        return True  # Restart required for critical safety settings

    return False


def validate_configuration(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate system configuration and return validation results

    Args:
        config: Configuration to validate (uses current if None)

    Returns:
        Dictionary with validation results
    """
    if config is None:
        config = load_config()

    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "info": []
    }

    # Validate logging is always enabled (requirement 8.5)
    if not config.get("logging", {}).get("enabled", False):
        validation_results["errors"].append("Logging must always be enabled (requirement 8.5)")
        validation_results["valid"] = False

    # Validate audit logging is enabled
    if not config.get("logging", {}).get("audit_enabled", False):
        validation_results["errors"].append("Audit logging must always be enabled")
        validation_results["valid"] = False

    # Validate data retention period is within tolerance
    retention_min = config.get("system", {}).get("data_retention_min_days", 731)
    retention_max = config.get("system", {}).get("data_retention_max_days", 735)

    if retention_min < 731 or retention_max > 735:
        validation_results["errors"].append("Data retention must be within 731-735 days tolerance")
        validation_results["valid"] = False

    # Validate PPE detection confidence thresholds
    confidence = config.get("ppe_detection", {}).get("confidence_threshold", 0.7)
    if confidence < 0.5 or confidence > 1.0:
        validation_results["warnings"].append(f"PPE detection confidence {confidence} may affect accuracy")

    # Validate camera configuration
    max_cameras = config.get("system", {}).get("max_concurrent_cameras", 8)
    if max_cameras < 8:
        validation_results["warnings"].append("System supports fewer than required 8 concurrent cameras")

    # Add info about current configuration
    validation_results["info"].append(f"Logging always enabled: {is_logging_always_enabled()}")
    validation_results["info"].append(f"Environment: {config.get('system', {}).get('environment', 'production')}")
    validation_results["info"].append(f"TLS fallback allowed: {config.get('system', {}).get('tls_fallback_allowed', True)}")

    return validation_results


def get_environment_config() -> Dict[str, Any]:
    """Get configuration for current environment"""
    environment = os.getenv("PPE_ENVIRONMENT", "production")
    return load_config(environment)


def is_critical_change(setting_path: str) -> bool:
    """Check if a configuration change requires system restart"""
    critical_settings = [
        "system.encryption_required",
        "system.tls_version_preferred",
        "ppe_detection.confidence_threshold",
        "zones.*.required_ppe",
        "zones.*.is_critical_area",
        "cameras.max_cameras"
    ]

    # Check if the setting path matches any critical setting pattern
    for critical in critical_settings:
        if critical in setting_path or setting_path.endswith(critical.split('.')[-1]):
            return True

    return False


def export_config() -> Dict[str, Any]:
    """Export current configuration for backup or deployment"""
    config = get_environment_config()

    # Add metadata
    config["_metadata"] = {
        "exported_at": "timestamp_placeholder",
        "version": SYSTEM_CONFIG.version,
        "environment": config.get("system", {}).get("environment"),
        "logging_enabled": is_logging_always_enabled()
    }

    return config
