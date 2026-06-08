# PPE Compliance Monitoring System

A comprehensive real-time computer vision solution that integrates with existing CCTV infrastructure to automatically detect Personal Protective Equipment (PPE) compliance violations and identify violating employees through face recognition.

## Directory Structure

```
ppe_compliance/
│
├── __init__.py                 # Main package initialization
├── config.py                   # Unified configuration access
├── README.md                   # This documentation
│
├── config/                     # Configuration management
│   ├── __init__.py
│   ├── main_config.py         # Central configuration controller
│   ├── ppe_detection_config.py # PPE detection rules and zone settings
│   ├── camera_config.py       # Camera management and network settings
│   └── logging_config.py      # Always-enabled logging configuration
│
├── models/                     # Data models and interfaces  
│   ├── __init__.py
│   └── ppe_detection/         # PPE detection model files
│       └── .gitkeep
│
├── detection/                  # PPE detection and computer vision
│   └── __init__.py
│
├── recognition/               # Enhanced face recognition system
│   └── __init__.py
│
├── compliance/                # Compliance engine and violation management
│   └── __init__.py
│
├── alerts/                    # Alert system and notification management
│   └── __init__.py
│
├── storage/                   # Data storage and management system
│   └── __init__.py
│
├── reporting/                 # Dashboard and reporting system
│   └── __init__.py
│
├── video/                     # Video stream processing and camera management
│   └── __init__.py
│
├── utils/                     # Utility functions and helpers
│   └── __init__.py
│
├── tests/                     # Test suite
│   └── __init__.py
│
├── logs/                      # Log files (always-enabled audit trail)
│   └── .gitkeep
│
└── data/                      # Data storage directories
    ├── employee_db/           # Employee database and photos
    │   └── .gitkeep
    └── evidence/              # Violation evidence photos
        └── .gitkeep
```

## Configuration Features

### PPE Detection Configuration
- Configurable PPE requirements per work zone
- Support for 6 PPE item types: helmets, safety glasses, work uniforms, gloves, safety vests, safety shoes
- Zone-specific compliance rules with validation
- Confidence thresholds and performance settings
- Prevention of invalid safety rule combinations

### Camera Configuration  
- Support for USB, IP, and RTSP camera protocols
- Multi-camera management with 8+ concurrent feeds
- Zone mapping and critical camera prioritization
- Network security with TLS 1.3 (fallback to TLS 1.2 allowed)
- Connection retry and health monitoring

### Logging Configuration
- **Always-enabled logging** (cannot be disabled per requirement 8.5)
- **Always-enabled audit trail** for compliance
- Category-based logging (system, video, PPE detection, face recognition, etc.)
- Performance metrics logging
- 731-735 days data retention tolerance
- Automatic log rotation and cleanup

## Key Features

### Always-Enabled Systems
- **Logging**: Cannot be disabled - requirement 8.5
- **Audit Trail**: Comprehensive audit logging for all system events
- **Video Processing**: Operates regardless of authentication status

### Security & Compliance
- TLS 1.3 preferred with TLS 1.2 fallback support
- AES-256 encryption for sensitive data
- Role-based access controls
- Comprehensive audit logging

### Configuration Management
- Runtime configuration updates
- Critical changes may require system restart
- Configuration validation and error checking
- Environment-specific overrides (development, testing, production)

### Performance Requirements
- 99.5% uptime target
- 8+ concurrent camera feeds
- 15+ FPS per camera
- Auto-recovery within 60 seconds
- Always-enabled logging without performance degradation

## Usage

```python
from ppe_compliance.config import (
    get_config_value,
    get_zone_config, 
    get_camera_config,
    log_audit_event
)

# Get system configuration
max_cameras = get_config_value('system.max_concurrent_cameras')

# Get zone-specific PPE requirements
zone_config = get_zone_config('manufacturing_floor')

# Get camera configuration
camera_config = get_camera_config('cam_manufacturing_01')

# Log audit event (always enabled)
log_audit_event('configuration_access', 'Configuration loaded successfully')
```

## Requirements Implemented

- **Requirement 8.5**: Always-enabled logging and audit trail
- **Requirement 10.1**: Configurable PPE requirements per work zone
- **Requirement 10.2**: Configuration updates without restart (except critical safety settings)
- **Requirement 11.2**: TLS 1.3 with fallback to TLS 1.2 when unavailable
- **Requirement 11.4**: Video processing regardless of authentication status

## Environment Variables

- `PPE_ENVIRONMENT`: Set to 'development', 'testing', or 'production' (default: 'production')

## Next Steps

This directory structure and configuration system provides the foundation for implementing all PPE compliance monitoring system components. Each component directory will contain the specific implementations for video processing, PPE detection, face recognition, compliance evaluation, alerting, and reporting functionality.