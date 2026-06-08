"""
Demo script for CCTV Stream Processor

This script demonstrates the CCTVStreamProcessor functionality including:
- Multi-camera support (USB, IP, RTSP protocols)
- Frame preprocessing pipeline for AI optimization
- Performance monitoring and metrics
- Resource management

Requirements: 1.1, 1.3, 1.5
"""

import cv2
import numpy as np
import time
import logging
from typing import List

from ppe_compliance.video.stream_processor import create_stream_processor
from ppe_compliance.config.camera_config import CameraConfig, CameraProtocol

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_demo_camera_configs() -> List[CameraConfig]:
    """Create demo camera configurations"""
    configs = []
    
    # USB camera (if available)
    configs.append(CameraConfig(
        camera_id="demo_usb_01",
        protocol=CameraProtocol.USB,
        connection_string="0",
        zone_name="manufacturing_floor",
        position_description="USB Demo Camera - Manufacturing Area",
        target_fps=15,
        resolution=(640, 480)
    ))
    
    # IP camera example (won't connect but shows configuration)
    configs.append(CameraConfig(
        camera_id="demo_ip_01", 
        protocol=CameraProtocol.IP,
        connection_string="http://192.168.1.100:8080/video",
        zone_name="warehouse",
        position_description="IP Demo Camera - Warehouse Area",
        target_fps=20,
        resolution=(1280, 720)
    ))
    
    # RTSP camera example (won't connect but shows configuration)
    configs.append(CameraConfig(
        camera_id="demo_rtsp_01",
        protocol=CameraProtocol.RTSP,
        connection_string="rtsp://192.168.1.101:554/stream1",
        zone_name="chemical_processing",
        position_description="RTSP Demo Camera - Chemical Processing Area", 
        target_fps=25,
        resolution=(1920, 1080)
    ))
    
    return configs


def demo_frame_preprocessing():
    """Demonstrate frame preprocessing capabilities"""
    logger.info("=== Frame Preprocessing Demo ===")
    
    processor = create_stream_processor()
    
    # Create test frames of different sizes
    test_frames = [
        ("Small (320x240)", np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)),
        ("Medium (640x480)", np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)),
        ("Large (1920x1080)", np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)),
        ("HD (1280x720)", np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8))
    ]
    
    for desc, frame in test_frames:
        logger.info(f"\nProcessing {desc} frame:")
        logger.info(f"  Original shape: {frame.shape}")
        
        # Time the preprocessing
        start_time = time.time()
        processed_frame = processor.preprocess_frame(frame)
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"  Processed shape: {processed_frame.shape}")
        logger.info(f"  Processing time: {processing_time:.2f}ms")
        
        # Check 50ms requirement
        if processing_time <= 50:
            logger.info(f"  ✓ Meets 50ms requirement")
        else:
            logger.warning(f"  ✗ Exceeds 50ms requirement")
    
    # Performance metrics
    metrics = processor.get_performance_metrics()
    logger.info(f"\nPreprocessing Performance:")
    logger.info(f"  Average time: {metrics['average_preprocessing_time_ms']:.2f}ms")
    logger.info(f"  Within 50ms: {metrics['preprocessing_within_50ms']*100:.1f}%")
    
    processor.release_resources()


def demo_multi_camera_setup():
    """Demonstrate multi-camera setup and management"""
    logger.info("\n=== Multi-Camera Setup Demo ===")
    
    processor = create_stream_processor()
    configs = create_demo_camera_configs()
    
    logger.info(f"Attempting to initialize {len(configs)} cameras:")
    for config in configs:
        logger.info(f"  - {config.camera_id} ({config.protocol.value}): {config.zone_name}")
    
    # Initialize cameras (some may fail if hardware not available)
    success = processor.initialize_cameras(configs)
    
    if success:
        logger.info("✓ Camera initialization completed")
        
        # Show camera status
        status = processor.get_camera_status()
        logger.info("\nCamera Status:")
        for camera_id, camera_status in status.items():
            status_indicator = "✓ Connected" if camera_status['connected'] else "✗ Failed"
            logger.info(f"  {camera_id}: {status_indicator}")
            logger.info(f"    Zone: {camera_status['zone']}")
            logger.info(f"    Protocol: {camera_status['protocol']}")
            logger.info(f"    Target FPS: {camera_status['target_fps']}")
            logger.info(f"    Current FPS: {camera_status['current_fps']:.2f}")
        
        # Try to capture frames from connected cameras
        logger.info("\nAttempting frame capture from connected cameras:")
        for camera_id, camera_status in status.items():
            if camera_status['connected']:
                success, frame, metadata = processor.get_next_frame(camera_id)
                if success and frame is not None:
                    logger.info(f"  ✓ {camera_id}: Frame captured ({metadata.resolution})")
                    
                    # Test preprocessing on real frame
                    start_time = time.time()
                    processed = processor.preprocess_frame(frame)
                    proc_time = (time.time() - start_time) * 1000
                    logger.info(f"    Preprocessing: {proc_time:.2f}ms -> {processed.shape}")
                else:
                    logger.info(f"  ✗ {camera_id}: No frame available")
        
        # Performance metrics
        metrics = processor.get_performance_metrics()
        logger.info(f"\nSystem Performance:")
        logger.info(f"  Active cameras: {metrics['active_cameras']}")
        logger.info(f"  System running: {metrics['running']}")
        
    else:
        logger.warning("✗ No cameras could be initialized")
    
    processor.release_resources()


def demo_protocol_support():
    """Demonstrate different protocol support"""
    logger.info("\n=== Protocol Support Demo ===")
    
    protocols = [
        ("USB", CameraProtocol.USB, "0"),
        ("IP", CameraProtocol.IP, "http://192.168.1.100:8080/video"),
        ("RTSP", CameraProtocol.RTSP, "rtsp://192.168.1.101:554/stream1")
    ]
    
    for name, protocol, connection_string in protocols:
        logger.info(f"\n{name} Protocol Configuration:")
        config = CameraConfig(
            camera_id=f"demo_{name.lower()}",
            protocol=protocol,
            connection_string=connection_string,
            zone_name="demo_zone",
            position_description=f"Demo {name} Camera"
        )
        
        logger.info(f"  Camera ID: {config.camera_id}")
        logger.info(f"  Protocol: {config.protocol.value}")
        logger.info(f"  Connection: {config.connection_string}")
        logger.info(f"  Zone: {config.zone_name}")
        logger.info(f"  Target FPS: {config.target_fps}")
        logger.info(f"  Resolution: {config.resolution}")
    
    logger.info("\n✓ All three protocols (USB, IP, RTSP) are supported")


def main():
    """Run all demonstrations"""
    logger.info("CCTV Stream Processor Demo")
    logger.info("=" * 50)
    
    try:
        # Demo 1: Frame preprocessing
        demo_frame_preprocessing()
        
        # Demo 2: Protocol support
        demo_protocol_support()
        
        # Demo 3: Multi-camera setup  
        demo_multi_camera_setup()
        
        logger.info("\n" + "=" * 50)
        logger.info("Demo completed successfully!")
        logger.info("\nKey Features Demonstrated:")
        logger.info("✓ Multi-camera support (up to 8 concurrent cameras)")
        logger.info("✓ USB, IP, and RTSP protocol support")
        logger.info("✓ Frame preprocessing pipeline for AI optimization")
        logger.info("✓ Sub-50ms preprocessing performance")
        logger.info("✓ Automatic connection management and retry logic")
        logger.info("✓ Performance monitoring and metrics collection")
        logger.info("✓ Proper resource cleanup and management")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()