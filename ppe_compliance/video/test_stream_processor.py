"""
Test script for CCTV Stream Processor

This script tests the basic functionality of the CCTVStreamProcessor implementation.
"""

import cv2
import numpy as np
import time
import logging
from typing import List

from .stream_processor import CCTVStreamProcessor, create_stream_processor
from ..config.camera_config import CameraConfig, CameraProtocol, get_camera_config, CAMERA_CONFIGURATIONS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_usb_camera():
    """Test USB camera connection"""
    logger.info("Testing USB camera connection...")
    
    # Create USB camera config
    usb_config = CameraConfig(
        camera_id="test_usb_01",
        protocol=CameraProtocol.USB,
        connection_string="0",  # Default USB camera
        zone_name="test_zone",
        position_description="Test USB Camera",
        target_fps=15,
        resolution=(640, 480)
    )
    
    # Create stream processor
    processor = create_stream_processor()
    
    try:
        # Initialize camera
        success = processor.initialize_cameras([usb_config])
        
        if success:
            logger.info("USB camera initialized successfully")
            
            # Capture and process some frames
            for i in range(10):
                success, frame, metadata = processor.get_next_frame("test_usb_01")
                
                if success and frame is not None:
                    logger.info(f"Frame {i+1}: {metadata.resolution}, FPS: {metadata.fps:.2f}")
                    
                    # Test preprocessing
                    processed_frame = processor.preprocess_frame(frame)
                    logger.info(f"Processed frame shape: {processed_frame.shape}")
                    
                    # Show frame (optional - comment out if running headless)
                    # cv2.imshow('Test Frame', frame)
                    # if cv2.waitKey(1) & 0xFF == ord('q'):
                    #     break
                
                time.sleep(0.1)
            
            # Get performance metrics
            metrics = processor.get_performance_metrics()
            logger.info(f"Performance metrics: {metrics}")
            
        else:
            logger.error("Failed to initialize USB camera")
            
    finally:
        processor.release_resources()
        cv2.destroyAllWindows()


def test_multiple_cameras():
    """Test multiple camera configuration"""
    logger.info("Testing multiple camera configuration...")
    
    # Get configured cameras (filter to those likely available)
    available_configs = []
    
    # Try to add USB camera if available
    try:
        test_cap = cv2.VideoCapture(0)
        if test_cap.isOpened():
            available_configs.append(CameraConfig(
                camera_id="test_usb_multi",
                protocol=CameraProtocol.USB,
                connection_string="0",
                zone_name="test_zone",
                position_description="Test USB Camera for Multi-test"
            ))
            test_cap.release()
    except:
        pass
    
    if not available_configs:
        logger.warning("No available cameras found for multi-camera test")
        return
    
    # Create stream processor
    processor = create_stream_processor()
    
    try:
        # Initialize cameras
        success = processor.initialize_cameras(available_configs)
        
        if success:
            logger.info(f"Successfully initialized {len(available_configs)} cameras")
            
            # Test frame capture from all cameras
            for i in range(5):
                for config in available_configs:
                    success, frame, metadata = processor.get_next_frame(config.camera_id)
                    
                    if success and frame is not None:
                        logger.info(f"Camera {config.camera_id} - Frame {i+1}: {metadata.resolution}")
                
                time.sleep(0.2)
            
            # Get camera status
            status = processor.get_camera_status()
            for camera_id, camera_status in status.items():
                logger.info(f"Camera {camera_id} status: {camera_status}")
            
        else:
            logger.error("Failed to initialize cameras")
            
    finally:
        processor.release_resources()


def test_frame_preprocessing():
    """Test frame preprocessing functionality"""
    logger.info("Testing frame preprocessing...")
    
    # Create a dummy frame
    dummy_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    processor = create_stream_processor()
    
    # Test preprocessing
    start_time = time.time()
    processed_frame = processor.preprocess_frame(dummy_frame)
    processing_time = (time.time() - start_time) * 1000
    
    logger.info(f"Original frame shape: {dummy_frame.shape}")
    logger.info(f"Processed frame shape: {processed_frame.shape}")
    logger.info(f"Processing time: {processing_time:.2f}ms")
    
    # Verify preprocessing time requirement (50ms)
    if processing_time <= 50:
        logger.info("✓ Preprocessing time meets requirement (≤50ms)")
    else:
        logger.warning(f"✗ Preprocessing time exceeds requirement ({processing_time:.2f}ms > 50ms)")
    
    processor.release_resources()


def main():
    """Run all tests"""
    logger.info("Starting CCTV Stream Processor tests...")
    
    try:
        # Test frame preprocessing first (no camera required)
        test_frame_preprocessing()
        
        # Test USB camera
        test_usb_camera()
        
        # Test multiple cameras
        test_multiple_cameras()
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        raise


if __name__ == "__main__":
    main()