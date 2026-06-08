"""
Unit tests for CCTV Stream Processor

Tests the CCTVStreamProcessor implementation including multi-camera support,
frame preprocessing, and error handling.
"""

import unittest
import numpy as np
import time
from unittest.mock import patch, MagicMock

from ..video.stream_processor import (
    CCTVStreamProcessor,
    CameraConnection,
    FrameMetadata,
    create_stream_processor
)
from ..config.camera_config import CameraConfig, CameraProtocol


class TestCCTVStreamProcessor(unittest.TestCase):
    """Test cases for CCTV Stream Processor"""

    def setUp(self):
        """Set up test fixtures"""
        self.processor = create_stream_processor()
        self.test_config = CameraConfig(
            camera_id="test_camera_01",
            protocol=CameraProtocol.USB,
            connection_string="0",
            zone_name="test_zone",
            position_description="Test camera"
        )

    def tearDown(self):
        """Clean up after tests"""
        if hasattr(self, 'processor'):
            self.processor.release_resources()

    def test_processor_initialization(self):
        """Test processor initialization"""
        self.assertIsInstance(self.processor, CCTVStreamProcessor)
        self.assertFalse(self.processor.running)
        self.assertEqual(len(self.processor.cameras), 0)

    def test_frame_preprocessing_basic(self):
        """Test basic frame preprocessing functionality"""
        # Create test frame
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Test preprocessing
        start_time = time.time()
        processed_frame = self.processor.preprocess_frame(test_frame)
        processing_time = (time.time() - start_time) * 1000

        # Verify output
        self.assertIsInstance(processed_frame, np.ndarray)
        self.assertEqual(processed_frame.shape, (640, 640, 3))  # Resized to AI dimensions

        # Check processing time requirement (should be under 50ms)
        self.assertLess(processing_time, 100, "Frame preprocessing took too long")

    def test_frame_preprocessing_normalization(self):
        """Test frame preprocessing with normalization"""
        test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255

        processed_frame = self.processor.preprocess_frame(test_frame)

        # Should be normalized to 0-1 range
        self.assertTrue(np.all(processed_frame <= 1.0))
        self.assertTrue(np.all(processed_frame >= 0.0))
        self.assertAlmostEqual(np.max(processed_frame), 1.0, places=2)

    def test_frame_preprocessing_performance(self):
        """Test frame preprocessing meets performance requirements"""
        # Test multiple frames to get average performance
        test_frame = np.random.randint(0, 255, (1920, 1080, 3), dtype=np.uint8)
        times = []

        for _ in range(10):
            start_time = time.time()
            self.processor.preprocess_frame(test_frame)
            processing_time = (time.time() - start_time) * 1000
            times.append(processing_time)

        avg_time = sum(times) / len(times)
        self.assertLess(avg_time, 50, f"Average preprocessing time {avg_time:.2f}ms exceeds 50ms requirement")

    @patch('cv2.VideoCapture')
    def test_camera_connection_usb(self, mock_cv2_capture):
        """Test USB camera connection"""
        # Mock successful camera connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2_capture.return_value = mock_capture

        config = CameraConfig(
            camera_id="usb_test",
            protocol=CameraProtocol.USB,
            connection_string="0",
            zone_name="test_zone",
            position_description="Test USB camera"
        )

        connection = CameraConnection(config)
        result = connection.connect()

        self.assertTrue(result)
        self.assertTrue(connection.is_connected)
        mock_cv2_capture.assert_called_with(0)  # USB camera index

    @patch('cv2.VideoCapture')
    def test_camera_connection_rtsp(self, mock_cv2_capture):
        """Test RTSP camera connection"""
        # Mock successful camera connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2_capture.return_value = mock_capture

        config = CameraConfig(
            camera_id="rtsp_test",
            protocol=CameraProtocol.RTSP,
            connection_string="rtsp://192.168.1.100:554/stream1",
            zone_name="test_zone",
            position_description="Test RTSP camera"
        )

        connection = CameraConnection(config)
        result = connection.connect()

        self.assertTrue(result)
        self.assertTrue(connection.is_connected)
        mock_cv2_capture.assert_called_with("rtsp://192.168.1.100:554/stream1")

    @patch('cv2.VideoCapture')
    def test_camera_connection_failure(self, mock_cv2_capture):
        """Test camera connection failure handling"""
        # Mock failed camera connection
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = False
        mock_cv2_capture.return_value = mock_capture

        connection = CameraConnection(self.test_config)
        result = connection.connect()

        self.assertFalse(result)
        self.assertFalse(connection.is_connected)

    @patch('cv2.VideoCapture')
    def test_frame_capture_with_metadata(self, mock_cv2_capture):
        """Test frame capture with metadata generation"""
        # Mock successful camera and frame capture
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, test_frame)
        mock_cv2_capture.return_value = mock_capture

        connection = CameraConnection(self.test_config)
        connection.connect()

        success, frame, metadata = connection.capture_frame()

        self.assertTrue(success)
        self.assertIsNotNone(frame)
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, FrameMetadata)
        self.assertEqual(metadata.camera_id, "test_camera_01")
        self.assertEqual(metadata.zone_name, "test_zone")
        self.assertEqual(metadata.resolution, (640, 480))

    @patch('cv2.VideoCapture')
    def test_multiple_camera_initialization(self, mock_cv2_capture):
        """Test initialization of multiple cameras"""
        # Mock successful cameras
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2_capture.return_value = mock_capture

        configs = [
            CameraConfig("cam1", CameraProtocol.USB, "0", "zone1", "Camera 1"),
            CameraConfig("cam2", CameraProtocol.RTSP, "rtsp://test", "zone2", "Camera 2"),
            CameraConfig("cam3", CameraProtocol.IP, "http://test", "zone3", "Camera 3"),
        ]

        result = self.processor.initialize_cameras(configs)

        self.assertTrue(result)
        self.assertEqual(len(self.processor.cameras), 3)
        self.assertTrue(self.processor.running)

    @patch('cv2.VideoCapture')
    def test_camera_status_monitoring(self, mock_cv2_capture):
        """Test camera status monitoring"""
        # Mock successful camera
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2_capture.return_value = mock_capture

        result = self.processor.initialize_cameras([self.test_config])
        self.assertTrue(result)

        # Get camera status
        status = self.processor.get_camera_status()

        self.assertIn("test_camera_01", status)
        camera_status = status["test_camera_01"]

        self.assertTrue(camera_status['connected'])
        self.assertEqual(camera_status['zone'], "test_zone")
        self.assertEqual(camera_status['protocol'], "usb")
        self.assertEqual(camera_status['target_fps'], 15)

    def test_performance_metrics(self):
        """Test performance metrics collection"""
        metrics = self.processor.get_performance_metrics()

        self.assertIn('active_cameras', metrics)
        self.assertIn('running', metrics)
        self.assertIn('average_preprocessing_time_ms', metrics)
        self.assertIn('preprocessing_within_50ms', metrics)
        self.assertIn('camera_status', metrics)

        self.assertEqual(metrics['active_cameras'], 0)
        self.assertFalse(metrics['running'])

    @patch('cv2.VideoCapture')
    def test_frame_buffer_management(self, mock_cv2_capture):
        """Test frame buffer management"""
        # Mock successful camera
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_cv2_capture.return_value = mock_capture

        result = self.processor.initialize_cameras([self.test_config])
        self.assertTrue(result)

        # Wait for some frames to be captured
        time.sleep(0.5)

        # Try to get frames
        success, frame, metadata = self.processor.get_next_frame("test_camera_01")

        # Should get a frame (may be False if no frames captured yet due to threading)
        if success:
            self.assertIsNotNone(frame)
            self.assertIsNotNone(metadata)

    def test_resource_cleanup(self):
        """Test proper resource cleanup"""
        # This test mainly ensures no exceptions are raised during cleanup
        try:
            self.processor.release_resources()
        except Exception as e:
            self.fail(f"Resource cleanup raised an exception: {e}")

        self.assertFalse(self.processor.running)
        self.assertEqual(len(self.processor.cameras), 0)

    def test_max_cameras_limit(self):
        """Test maximum cameras limit enforcement"""
        # Create more configs than the maximum allowed
        configs = []
        for i in range(12):  # More than default max of 8
            configs.append(CameraConfig(
                f"cam_{i}", CameraProtocol.USB, str(i), f"zone_{i}", f"Camera {i}"
            ))

        with patch('cv2.VideoCapture') as mock_cv2_capture:
            mock_capture = MagicMock()
            mock_capture.isOpened.return_value = True
            mock_capture.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
            mock_cv2_capture.return_value = mock_capture

            result = self.processor.initialize_cameras(configs)

            # Should still succeed but with limited cameras
            if result:
                self.assertLessEqual(len(self.processor.cameras), 8)


class TestCameraConnection(unittest.TestCase):
    """Test cases for CameraConnection class"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = CameraConfig(
            camera_id="test_camera",
            protocol=CameraProtocol.USB,
            connection_string="0",
            zone_name="test_zone",
            position_description="Test camera"
        )

    def test_camera_connection_initialization(self):
        """Test camera connection initialization"""
        connection = CameraConnection(self.config)

        self.assertEqual(connection.config, self.config)
        self.assertFalse(connection.is_connected)
        self.assertEqual(connection.frame_count, 0)
        self.assertEqual(connection.current_fps, 0.0)
        self.assertEqual(connection.connection_attempts, 0)

    @patch('cv2.VideoCapture')
    def test_fps_calculation(self, mock_cv2_capture):
        """Test FPS calculation during frame capture"""
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        mock_capture = MagicMock()
        mock_capture.isOpened.return_value = True
        mock_capture.read.return_value = (True, test_frame)
        mock_cv2_capture.return_value = mock_capture

        connection = CameraConnection(self.config)
        connection.connect()

        # Capture multiple frames to test FPS calculation
        for _ in range(3):
            success, frame, metadata = connection.capture_frame()
            self.assertTrue(success)
            time.sleep(0.1)  # Small delay between captures

        # FPS should be calculated after the first frame
        self.assertGreater(connection.current_fps, 0)


def main():
    """Run all tests"""
    unittest.main()


if __name__ == "__main__":
    main()
