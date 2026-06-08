"""
PPE Detection Configuration

This module contains configuration settings for PPE detection rules,
required PPE items per zone, and detection thresholds.

Requirements: 8.5, 10.1
"""

from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class PPEItemType(Enum):
    """Types of PPE items that can be detected"""
    HELMET = "helmet"
    SAFETY_GLASSES = "safety_glasses" 
    WORK_UNIFORM = "work_uniform"
    GLOVES = "gloves"
    SAFETY_VEST = "safety_vest"
    SAFETY_SHOES = "safety_shoes"


@dataclass
class PPEZoneConfig:
    """Configuration for PPE requirements in specific zones"""
    zone_name: str
    required_ppe: List[PPEItemType]
    minimum_confidence: float = 0.7
    is_critical_area: bool = False


# Default PPE detection configuration
PPE_DETECTION_CONFIG = {
    # Model configuration
    "model_path": "models/ppe_detection_model.pt",
    "model_type": "yolo",
    "device": "auto",  # auto, cpu, cuda:0, etc.
    
    # Detection thresholds
    "confidence_threshold": 0.7,
    "nms_threshold": 0.4,
    "max_detections": 50,
    
    # Performance settings
    "input_size": (640, 640),
    "batch_size": 1,
    "max_processing_time_ms": 200,  # For multiple persons requirement
    
    # PPE item classes mapping
    "class_names": {
        0: PPEItemType.HELMET,
        1: PPEItemType.SAFETY_GLASSES,
        2: PPEItemType.WORK_UNIFORM,
        3: PPEItemType.GLOVES,
        4: PPEItemType.SAFETY_VEST,
        5: PPEItemType.SAFETY_SHOES,
    },
    
    # Validation settings
    "require_valid_detections": True,  # Must have valid detections before marking compliance
    "person_detection_threshold": 0.5,
}

# Zone-specific PPE requirements
ZONE_CONFIGURATIONS = {
    "manufacturing_floor": PPEZoneConfig(
        zone_name="Manufacturing Floor",
        required_ppe=[
            PPEItemType.HELMET,
            PPEItemType.SAFETY_GLASSES,
            PPEItemType.WORK_UNIFORM,
            PPEItemType.SAFETY_SHOES
        ],
        minimum_confidence=0.7,
        is_critical_area=True
    ),
    
    "warehouse": PPEZoneConfig(
        zone_name="Warehouse",
        required_ppe=[
            PPEItemType.HELMET,
            PPEItemType.SAFETY_VEST,
            PPEItemType.SAFETY_SHOES
        ],
        minimum_confidence=0.7,
        is_critical_area=False
    ),
    
    "chemical_processing": PPEZoneConfig(
        zone_name="Chemical Processing",
        required_ppe=[
            PPEItemType.HELMET,
            PPEItemType.SAFETY_GLASSES,
            PPEItemType.WORK_UNIFORM,
            PPEItemType.GLOVES,
            PPEItemType.SAFETY_SHOES
        ],
        minimum_confidence=0.8,
        is_critical_area=True
    ),
    
    "office_area": PPEZoneConfig(
        zone_name="Office Area",
        required_ppe=[],  # No PPE required in office areas
        minimum_confidence=0.7,
        is_critical_area=False
    ),
}

# Configuration validation settings
CONFIGURATION_VALIDATION = {
    "prevent_invalid_combinations": True,
    "restart_required_for_critical_changes": True,
    "critical_safety_settings": [
        "required_ppe",
        "minimum_confidence",
        "is_critical_area"
    ],
    "validate_zone_consistency": True,
}


def get_zone_config(zone_name: str) -> PPEZoneConfig:
    """Get PPE configuration for a specific zone"""
    return ZONE_CONFIGURATIONS.get(zone_name, ZONE_CONFIGURATIONS["office_area"])


def validate_ppe_combination(required_ppe: List[PPEItemType]) -> bool:
    """Validate PPE combination to prevent invalid safety rule combinations"""
    # Basic validation - can be extended with more complex safety rules
    if not required_ppe:
        return True  # Empty list is valid (office areas)
    
    # Check for conflicting combinations
    # Example: If chemical processing, must have gloves AND safety glasses
    if PPEItemType.GLOVES in required_ppe:
        # If gloves required, safety glasses should also be required for safety
        if PPEItemType.SAFETY_GLASSES not in required_ppe:
            return False
    
    return True


def is_critical_configuration_change(setting_name: str) -> bool:
    """Check if a configuration change requires system restart"""
    return setting_name in CONFIGURATION_VALIDATION["critical_safety_settings"]