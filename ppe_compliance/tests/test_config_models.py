"""
Unit tests for configuration models

Tests the configuration models to ensure TLS fallback, restart requirements,
and other configuration features work correctly.

Requirements: 10.2, 11.2
"""

import pytest

from ..models.config import (
    SecurityConfig, ModelDeploymentConfig, PPEComplianceConfig,
    SystemRestartConfig, TLSVersion, EncryptionStandard, AuthenticationMode
)


class TestSecurityConfig:
    """Test security configuration model"""

    def test_default_security_config(self):
        """Test default security configuration"""
        config = SecurityConfig()

        assert config.tls_version_preferred == TLSVersion.TLS_1_3
        assert config.tls_fallback_allowed is True
        assert config.tls_fallback_version == TLSVersion.TLS_1_2
        assert config.encryption_standard == EncryptionStandard.AES_256
        assert config.encryption_required is True
        assert config.video_processing_auth_mode == AuthenticationMode.BYPASS_FOR_VIDEO

    def test_can_fallback_to_tls12(self):
        """Test TLS 1.2 fallback capability"""
        config = SecurityConfig(tls_fallback_allowed=True)
        assert config.can_fallback_to_tls12() is True

        config_no_fallback = SecurityConfig(tls_fallback_allowed=False)
        assert config_no_fallback.can_fallback_to_tls12() is False

    def test_requires_encryption_validation(self):
        """Test encryption validation requirement"""
        config = SecurityConfig(encryption_required=True)
        assert config.requires_encryption_validation() is True

        config_no_encryption = SecurityConfig(encryption_required=False)
        assert config_no_encryption.requires_encryption_validation() is False

    def test_allows_video_processing_without_auth(self):
        """Test video processing authentication bypass"""
        config = SecurityConfig()
        assert config.allows_video_processing_without_auth() is True

        config_auth_required = SecurityConfig(
            video_processing_auth_mode=AuthenticationMode.REQUIRED
        )
        assert config_auth_required.allows_video_processing_without_auth() is False

    def test_invalid_tls_fallback_configuration(self):
        """Test that invalid TLS fallback configuration raises error"""
        with pytest.raises(ValueError, match="TLS fallback version must be different from preferred version"):
            SecurityConfig(
                tls_version_preferred=TLSVersion.TLS_1_2,
                tls_fallback_allowed=True,
                tls_fallback_version=TLSVersion.TLS_1_2  # Same as preferred
            )

    def test_encryption_required_without_standard_raises_error(self):
        """Test that requiring encryption without standard raises error"""
        with pytest.raises(ValueError, match="Encryption standard must be specified when encryption is required"):
            SecurityConfig(
                encryption_required=True,
                encryption_standard=None
            )


class TestModelDeploymentConfig:
    """Test model deployment configuration model"""

    def test_default_model_deployment_config(self):
        """Test default model deployment configuration"""
        config = ModelDeploymentConfig()

        assert config.compatibility_check_enabled is True
        assert config.block_incompatible_updates is True
        assert config.validation_required_before_deployment is True
        assert config.backward_compatibility_required is True
        assert config.rollback_enabled is True

    def test_should_block_deployment_with_compatibility_break(self):
        """Test deployment blocking when compatibility breaks"""
        config = ModelDeploymentConfig(block_incompatible_updates=True)

        # Should block when compatibility is broken
        assert config.should_block_deployment(compatibility_broken=True, performance_degradation=0.02) is True

        # Should not block when compatibility is maintained
        assert config.should_block_deployment(compatibility_broken=False, performance_degradation=0.02) is False

    def test_should_block_deployment_with_performance_degradation(self):
        """Test deployment blocking due to performance degradation"""
        config = ModelDeploymentConfig(allowed_accuracy_degradation=0.05)

        # Should block when degradation exceeds threshold
        assert config.should_block_deployment(compatibility_broken=False, performance_degradation=0.10) is True

        # Should not block when degradation is within threshold
        assert config.should_block_deployment(compatibility_broken=False, performance_degradation=0.03) is False

    def test_requires_manual_approval(self):
        """Test manual approval requirement for major updates"""
        config = ModelDeploymentConfig(require_manual_approval_for_major_updates=True)

        assert config.requires_manual_approval(is_major_update=True) is True
        assert config.requires_manual_approval(is_major_update=False) is False

    def test_invalid_performance_threshold_raises_error(self):
        """Test that invalid performance threshold raises error"""
        with pytest.raises(ValueError, match="Performance validation threshold must be between 0.0 and 1.0"):
            ModelDeploymentConfig(performance_validation_threshold=1.5)

    def test_negative_accuracy_degradation_raises_error(self):
        """Test that negative accuracy degradation raises error"""
        with pytest.raises(ValueError, match="Allowed accuracy degradation cannot be negative"):
            ModelDeploymentConfig(allowed_accuracy_degradation=-0.1)


class TestPPEComplianceConfig:
    """Test PPE compliance configuration model"""

    def test_default_ppe_compliance_config(self):
        """Test default PPE compliance configuration"""
        config = PPEComplianceConfig()

        assert config.validation_threshold == 0.7
        assert config.prevent_invalid_combinations is True
        assert config.validate_zone_consistency is True
        assert config.require_safety_approval_for_changes is True
        assert "required_ppe" in config.restart_required_changes

    def test_requires_restart_for_change(self):
        """Test restart requirement for critical changes"""
        config = PPEComplianceConfig()

        assert config.requires_restart_for_change("required_ppe") is True
        assert config.requires_restart_for_change("validation_threshold") is True
        assert config.requires_restart_for_change("non_critical_setting") is False

    def test_validate_change_with_valid_data(self):
        """Test configuration change validation with valid data"""
        config = PPEComplianceConfig()

        # Valid required_ppe change
        result = config.validate_change("required_ppe", ["helmet", "safety_glasses"])
        assert result["valid"] is True
        assert result["requires_restart"] is True
        assert result["requires_approval"] is True

    def test_validate_change_with_invalid_threshold(self):
        """Test configuration change validation with invalid threshold"""
        config = PPEComplianceConfig()

        result = config.validate_change("validation_threshold", 1.5)
        assert result["valid"] is False
        assert "validation_threshold must be between 0.0 and 1.0" in result["errors"]

    def test_validate_change_with_low_threshold_warning(self):
        """Test configuration change validation with low threshold warning"""
        config = PPEComplianceConfig()

        result = config.validate_change("validation_threshold", 0.3)
        assert result["valid"] is True
        assert any("Low validation threshold" in warning for warning in result["warnings"])

    def test_ppe_combination_validation_with_gloves_but_no_glasses(self):
        """Test PPE combination validation fails when gloves required but no glasses"""
        with pytest.raises(ValueError, match="If gloves required, safety glasses must also be required"):
            PPEComplianceConfig(
                zone_specific_rules={
                    "test_zone": ["helmet", "gloves"]  # Missing safety_glasses
                }
            )

    def test_chemical_zone_validation(self):
        """Test chemical zone requires comprehensive PPE"""
        with pytest.raises(ValueError, match="Chemical zone .* missing required PPE"):
            PPEComplianceConfig(
                zone_specific_rules={
                    "chemical_processing": ["helmet"]  # Missing other required PPE
                }
            )

    def test_valid_ppe_combinations_pass_validation(self):
        """Test that valid PPE combinations pass validation"""
        config = PPEComplianceConfig(
            zone_specific_rules={
                "manufacturing": ["helmet", "safety_glasses", "gloves", "work_uniform"],
                "office": [],  # Office areas can have no PPE
                "chemical_processing": ["helmet", "safety_glasses", "gloves", "work_uniform"]
            }
        )

        # Should not raise any exceptions
        assert config.prevent_invalid_combinations is True


class TestSystemRestartConfig:
    """Test system restart configuration model"""

    def test_default_system_restart_config(self):
        """Test default system restart configuration"""
        config = SystemRestartConfig()

        assert config.restart_timeout_seconds == 60
        assert config.graceful_shutdown_enabled is True
        assert config.save_state_before_restart is True
        assert config.allow_immediate_restart is False  # Safety first
        assert config.maintenance_window_required is True

    def test_requires_immediate_restart(self):
        """Test immediate restart requirement logic"""
        config = SystemRestartConfig(allow_immediate_restart=True)

        assert config.requires_immediate_restart("encryption_standard") is True
        assert config.requires_immediate_restart("non_critical_setting") is False

    def test_requires_scheduled_restart(self):
        """Test scheduled restart requirement logic"""
        config = SystemRestartConfig(allow_immediate_restart=False)

        assert config.requires_scheduled_restart("encryption_standard") is True
        assert config.requires_scheduled_restart("tls_version_preferred") is True
        assert config.requires_scheduled_restart("non_critical_setting") is False

    def test_get_restart_procedure(self):
        """Test restart procedure configuration"""
        config = SystemRestartConfig(
            allow_immediate_restart=False,
            graceful_shutdown_enabled=True,
            save_state_before_restart=True,
            notify_users_before_restart=True,
            restart_notification_minutes=10
        )

        procedure = config.get_restart_procedure("encryption_standard")

        assert procedure["immediate"] is False
        assert procedure["scheduled"] is True
        assert procedure["graceful_shutdown"] is True
        assert procedure["save_state"] is True
        assert procedure["notification_required"] is True
        assert procedure["notification_time_minutes"] == 10

    def test_immediate_restart_when_allowed(self):
        """Test immediate restart when explicitly allowed"""
        config = SystemRestartConfig(allow_immediate_restart=True)

        procedure = config.get_restart_procedure("security_audit_enabled")

        assert procedure["immediate"] is True
        assert procedure["scheduled"] is False


class TestConfigurationIntegration:
    """Test integration between different configuration models"""

    def test_security_and_restart_config_integration(self):
        """Test that security config changes properly integrate with restart requirements"""
        restart_config = SystemRestartConfig()

        # TLS version changes should require restart
        assert restart_config.requires_scheduled_restart("tls_version_preferred") is True

        # Encryption changes should require restart
        assert restart_config.requires_scheduled_restart("encryption_standard") is True

    def test_model_deployment_with_security_requirements(self):
        """Test model deployment configuration with security requirements"""
        deployment_config = ModelDeploymentConfig(
            block_incompatible_updates=True,
            validation_required_before_deployment=True
        )

        security_config = SecurityConfig(encryption_required=True)

        # Both configs should enforce strict requirements
        assert deployment_config.block_incompatible_updates is True
        assert security_config.requires_encryption_validation() is True

    def test_ppe_config_with_restart_requirements(self):
        """Test PPE configuration changes with restart requirements"""
        ppe_config = PPEComplianceConfig()
        restart_config = SystemRestartConfig()

        # PPE requirement changes should require restart
        assert ppe_config.requires_restart_for_change("required_ppe") is True

        # Should use scheduled restart for safety
        assert restart_config.requires_scheduled_restart("required_ppe") is False  # Not in always_restart_settings

        # But PPE validation changes should still require restart
        validation_result = ppe_config.validate_change("validation_threshold", 0.8)
        assert validation_result["requires_restart"] is True
