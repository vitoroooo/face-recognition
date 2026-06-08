"""
Configuration Models for PPE Compliance Monitoring System

This module defines configuration models with enhanced security settings,
TLS fallback capabilities, and restart requirement handling.

Requirements: 10.2, 11.2
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class TLSVersion(Enum):
    """Supported TLS versions"""
    TLS_1_2 = "1.2"
    TLS_1_3 = "1.3"


class EncryptionStandard(Enum):
    """Supported encryption standards"""
    AES_256 = "AES-256"
    AES_128 = "AES-128"


class AuthenticationMode(Enum):
    """Authentication modes for different operations"""
    REQUIRED = "required"
    OPTIONAL = "optional" 
    BYPASS_FOR_VIDEO = "bypass_for_video"  # Allow video processing regardless of auth


@dataclass
class SecurityConfig:
    """
    Enhanced security configuration with TLS fallback support
    
    Requirements:
    - TLS 1.3 preferred, TLS 1.2 fallback allowed when unavailable
    - AES-256 encryption required for data storage
    - Video processing allowed regardless of authentication status
    """
    # TLS Configuration
    tls_version_preferred: TLSVersion = TLSVersion.TLS_1_3
    tls_fallback_allowed: bool = True  # Allow TLS 1.2 when TLS 1.3 unavailable
    tls_fallback_version: TLSVersion = TLSVersion.TLS_1_2
    
    # Encryption Standards
    encryption_standard: EncryptionStandard = EncryptionStandard.AES_256
    encryption_required: bool = True  # Must not operate unless data is actually encrypted
    
    # Authentication Configuration
    video_processing_auth_mode: AuthenticationMode = AuthenticationMode.BYPASS_FOR_VIDEO
    system_access_auth_required: bool = True
    api_access_auth_required: bool = True
    
    # Certificate and Key Management
    certificate_path: Optional[str] = None
    private_key_path: Optional[str] = None
    ca_certificate_path: Optional[str] = None
    certificate_validation_strict: bool = True
    
    # Security Logging
    security_audit_enabled: bool = True
    failed_auth_logging: bool = True
    tls_handshake_logging: bool = False  # May be verbose
    
    def __post_init__(self):
        """Validate security configuration"""
        # Ensure encryption is properly configured when required
        if self.encryption_required and not self.encryption_standard:
            raise ValueError("Encryption standard must be specified when encryption is required")
        
        # Validate TLS fallback configuration
        if self.tls_fallback_allowed:
            if self.tls_fallback_version == self.tls_version_preferred:
                raise ValueError("TLS fallback version must be different from preferred version")
    
    def can_fallback_to_tls12(self) -> bool:
        """Check if TLS 1.2 fallback is allowed when TLS 1.3 unavailable"""
        return (self.tls_fallback_allowed and 
                self.tls_fallback_version == TLSVersion.TLS_1_2)
    
    def requires_encryption_validation(self) -> bool:
        """Check if system must validate actual encryption before operating"""
        return self.encryption_required
    
    def allows_video_processing_without_auth(self) -> bool:
        """Check if video processing can proceed regardless of authentication status"""
        return self.video_processing_auth_mode == AuthenticationMode.BYPASS_FOR_VIDEO


@dataclass
class ModelDeploymentConfig:
    """
    Configuration for model deployment with compatibility checking
    
    Requirements:
    - Block deployment when compatibility breaks
    - Validation required before updates
    - Backward compatibility maintenance
    """
    compatibility_check_enabled: bool = True
    block_incompatible_updates: bool = True  # Block deployment when compatibility breaks
    validation_required_before_deployment: bool = True
    backward_compatibility_required: bool = True
    
    # Model validation settings
    performance_validation_threshold: float = 0.85  # Minimum accuracy requirement
    validation_dataset_path: Optional[str] = None
    validation_sample_size: int = 1000
    
    # Deployment rollback settings
    rollback_enabled: bool = True
    previous_model_backup_count: int = 3
    automatic_rollback_on_failure: bool = True
    
    # Update restrictions
    allowed_accuracy_degradation: float = 0.05  # 5% maximum accuracy loss
    require_manual_approval_for_major_updates: bool = True
    
    def __post_init__(self):
        """Validate model deployment configuration"""
        if self.performance_validation_threshold < 0.0 or self.performance_validation_threshold > 1.0:
            raise ValueError("Performance validation threshold must be between 0.0 and 1.0")
        
        if self.allowed_accuracy_degradation < 0.0:
            raise ValueError("Allowed accuracy degradation cannot be negative")
    
    def should_block_deployment(self, compatibility_broken: bool, 
                               performance_degradation: float) -> bool:
        """Determine if deployment should be blocked"""
        if self.block_incompatible_updates and compatibility_broken:
            return True
        
        if performance_degradation > self.allowed_accuracy_degradation:
            return True
        
        return False
    
    def requires_manual_approval(self, is_major_update: bool) -> bool:
        """Check if update requires manual approval"""
        return self.require_manual_approval_for_major_updates and is_major_update


@dataclass 
class PPEComplianceConfig:
    """
    Enhanced PPE compliance configuration with restart requirements
    
    Requirements:
    - Zone-specific rules without safety conflicts
    - Restart required for critical safety settings
    - Configuration validation
    """
    required_ppe: List[str] = field(default_factory=list)
    zone_specific_rules: Dict[str, List[str]] = field(default_factory=dict)
    validation_threshold: float = 0.7
    
    # Critical settings that require restart when changed
    restart_required_changes: List[str] = field(default_factory=lambda: [
        "required_ppe",
        "validation_threshold", 
        "zone_specific_rules",
        "critical_area_settings"
    ])
    
    # Safety validation settings
    prevent_invalid_combinations: bool = True
    validate_zone_consistency: bool = True
    require_safety_approval_for_changes: bool = True
    
    # Configuration change tracking
    last_modified_timestamp: Optional[str] = None
    last_modified_by: Optional[str] = None
    change_requires_restart: bool = False
    
    def __post_init__(self):
        """Validate PPE compliance configuration"""
        self._validate_ppe_combinations()
        self._validate_zone_consistency()
    
    def _validate_ppe_combinations(self):
        """Validate PPE combinations to prevent invalid safety rule combinations"""
        if not self.prevent_invalid_combinations:
            return
        
        # Example safety validation rules
        for zone, ppe_list in self.zone_specific_rules.items():
            # If gloves are required, safety glasses should also be required for safety
            if "gloves" in ppe_list and "safety_glasses" not in ppe_list:
                raise ValueError(f"Zone {zone}: If gloves required, safety glasses must also be required")
            
            # Chemical processing areas must have comprehensive PPE
            if "chemical" in zone.lower():
                required_chemical_ppe = {"helmet", "safety_glasses", "gloves", "work_uniform"}
                if not required_chemical_ppe.issubset(set(ppe_list)):
                    raise ValueError(f"Chemical zone {zone} missing required PPE: {required_chemical_ppe - set(ppe_list)}")
    
    def _validate_zone_consistency(self):
        """Validate zone configuration consistency"""
        if not self.validate_zone_consistency:
            return
        
        # Ensure no empty zones with required PPE
        for zone, ppe_list in self.zone_specific_rules.items():
            if not ppe_list and zone not in ["office", "break_room", "lobby"]:
                raise ValueError(f"Non-office zone {zone} should have PPE requirements")
    
    def requires_restart_for_change(self, setting_name: str) -> bool:
        """Check if changing a specific setting requires system restart"""
        return setting_name in self.restart_required_changes
    
    def validate_change(self, setting_name: str, new_value: Any) -> Dict[str, Any]:
        """Validate a configuration change and return validation results"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "requires_restart": self.requires_restart_for_change(setting_name),
            "requires_approval": self.require_safety_approval_for_changes
        }
        
        # Validate specific setting changes
        if setting_name == "required_ppe":
            if not isinstance(new_value, list):
                validation_result["errors"].append("required_ppe must be a list")
                validation_result["valid"] = False
            elif not new_value:
                validation_result["warnings"].append("Empty PPE requirements may reduce safety")
        
        elif setting_name == "validation_threshold":
            if not (0.0 <= new_value <= 1.0):
                validation_result["errors"].append("validation_threshold must be between 0.0 and 1.0")
                validation_result["valid"] = False
            elif new_value < 0.5:
                validation_result["warnings"].append("Low validation threshold may increase false positives")
        
        elif setting_name == "zone_specific_rules":
            try:
                # Create temporary config to test validation
                temp_config = PPEComplianceConfig(zone_specific_rules=new_value)
                temp_config._validate_ppe_combinations()
            except ValueError as e:
                validation_result["errors"].append(str(e))
                validation_result["valid"] = False
        
        return validation_result


@dataclass
class SystemRestartConfig:
    """
    Configuration for system restart requirements and procedures
    
    Requirements:
    - Critical safety settings require restart when necessary
    - Graceful restart procedures for safety systems
    """
    restart_timeout_seconds: int = 60
    graceful_shutdown_enabled: bool = True
    save_state_before_restart: bool = True
    
    # Critical settings that always require restart
    always_restart_settings: List[str] = field(default_factory=lambda: [
        "encryption_standard",
        "tls_version_preferred",
        "security_audit_enabled"
    ])
    
    # Restart scheduling
    allow_immediate_restart: bool = False  # Require scheduled restart for safety
    maintenance_window_required: bool = True
    notify_users_before_restart: bool = True
    restart_notification_minutes: int = 10
    
    def requires_immediate_restart(self, setting_name: str) -> bool:
        """Check if setting change requires immediate restart"""
        return setting_name in self.always_restart_settings and self.allow_immediate_restart
    
    def requires_scheduled_restart(self, setting_name: str) -> bool:
        """Check if setting change requires scheduled restart"""
        return setting_name in self.always_restart_settings and not self.allow_immediate_restart
    
    def get_restart_procedure(self, setting_name: str) -> Dict[str, Any]:
        """Get recommended restart procedure for setting change"""
        return {
            "immediate": self.requires_immediate_restart(setting_name),
            "scheduled": self.requires_scheduled_restart(setting_name),
            "graceful_shutdown": self.graceful_shutdown_enabled,
            "save_state": self.save_state_before_restart,
            "notification_required": self.notify_users_before_restart,
            "notification_time_minutes": self.restart_notification_minutes
        }