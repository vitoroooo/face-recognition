"""
Camera Configuration

This module contains configuration settings for CCTV camera management,
connection settings, and zone mapping.

Requirements: 1.1, 1.2, 1.3, 1.4
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CameraProtocol(Enum):
    """Supported camera protocols"""
    USB = "usb"
    IP = "ip"
    RTSP = "rtsp"


@dataclass
class CameraConfig:
    """Configuration for individual camera"""
    camera_id: str
    protocol: CameraProtocol
    connection_string: str
    zone_name: str
    position_description: str
    is_primary: bool = False
    retry_interval_seconds: int = 30
    target_fps: int = 15
    resolution: Tuple[int, int] = (1920, 1080)
    preprocessing_enabled: bool = True


# Global camera system configuration
CAMERA_SYSTEM_CONFIG = {
    # Connection management
    "max_cameras": 8,  # Support at least 8 concurrent camera feeds
    "connection_timeout_seconds": 10,
    "retry_interval_seconds": 30,
    "max_retry_attempts": 5,
    "health_check_interval_seconds": 60,

    # Performance settings
    "target_fps_per_camera": 15,  # Maintain at least 15 FPS per camera
    "frame_processing_timeout_ms": 50,  # Preprocess frames within 50ms
    "buffer_size": 10,
    "enable_frame_skipping": True,

    # Video preprocessing
    "resize_for_ai": True,
    "resize_dimensions": (640, 640),
    "normalize_pixels": True,
    "enable_denoising": False,  # Can be enabled for low-quality cameras

    # Resource management
    "prioritize_critical_cameras": True,
    "enable_resource_monitoring": True,
    "cpu_usage_threshold": 80.0,
    "memory_usage_threshold": 85.0,
}

# Camera configurations for different zones
CAMERA_CONFIGURATIONS = {
    "cam_manufacturing_01": CameraConfig(
        camera_id="cam_manufacturing_01",
        protocol=CameraProtocol.IP,
        connection_string="rtsp://192.168.1.100:554/stream1",
        zone_name="manufacturing_floor",
        position_description="Manufacturing Floor - Assembly Line 1",
        is_primary=True,
        resolution=(1920, 1080)
    ),

    "cam_manufacturing_02": CameraConfig(
        camera_id="cam_manufacturing_02",
        protocol=CameraProtocol.IP,
        connection_string="rtsp://192.168.1.101:554/stream1",
        zone_name="manufacturing_floor",
        position_description="Manufacturing Floor - Assembly Line 2",
        is_primary=False,
        resolution=(1920, 1080)
    ),

    "cam_warehouse_01": CameraConfig(
        camera_id="cam_warehouse_01",
        protocol=CameraProtocol.RTSP,
        connection_string="rtsp://192.168.1.102:554/live",
        zone_name="warehouse",
        position_description="Warehouse - Main Entrance",
        is_primary=True,
        resolution=(1280, 720)
    ),

    "cam_chemical_01": CameraConfig(
        camera_id="cam_chemical_01",
        protocol=CameraProtocol.IP,
        connection_string="http://192.168.1.103:8080/video",
        zone_name="chemical_processing",
        position_description="Chemical Processing - Reactor Area",
        is_primary=True,
        resolution=(1920, 1080),
        target_fps=20  # Higher FPS for critical area
    ),

    "cam_office_01": CameraConfig(
        camera_id="cam_office_01",
        protocol=CameraProtocol.USB,
        connection_string="0",  # USB camera index
        zone_name="office_area",
        position_description="Office Area - Main Hall",
        is_primary=False,
        resolution=(1280, 720),
        target_fps=10  # Lower FPS for office area
    ),
}

# Critical camera prioritization
CRITICAL_CAMERAS = [
    "cam_manufacturing_01",
    "cam_manufacturing_02",
    "cam_chemical_01"
]

# Network and security settings
NETWORK_CONFIG = {
    "connection_timeout": 10,
    "read_timeout": 5,
    "user_agent": "PPE-Compliance-System/1.0",
    "enable_authentication": True,
    "default_username": "admin",
    "default_password": "admin123",  # Should be changed in production

    # TLS/SSL settings
    "verify_ssl": True,
    "tls_version": "1.3",  # Prefer TLS 1.3
    "allow_tls_fallback": True,  # Allow TLS 1.2 fallback when TLS 1.3 unavailable
    "ssl_ciphers": "HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA",
}


def get_camera_config(camera_id: str) -> Optional[CameraConfig]:
    """Get configuration for specific camera"""
    return CAMERA_CONFIGURATIONS.get(camera_id)


def get_cameras_by_zone(zone_name: str) -> List[CameraConfig]:
    """Get all cameras assigned to a specific zone"""
    return [
        config for config in CAMERA_CONFIGURATIONS.values()
        if config.zone_name == zone_name
    ]


def get_critical_cameras() -> List[CameraConfig]:
    """Get configurations for critical cameras"""
    return [
        config for camera_id, config in CAMERA_CONFIGURATIONS.items()
        if camera_id in CRITICAL_CAMERAS
    ]


def validate_camera_config(config: CameraConfig) -> bool:
    """Validate camera configuration"""
    if not config.camera_id or not config.connection_string:
        return False

    if config.target_fps < 5 or config.target_fps > 60:
        return False

    if config.retry_interval_seconds < 10:
        return False

    return True


def get_zone_from_camera(camera_id: str) -> Optional[str]:
    """Get zone name for a specific camera"""
    config = get_camera_config(camera_id)
    return config.zone_name if config else None
