"""
CCTV Stream Processor Implementation

This module implements the CCTVStreamProcessor class that manages multiple CCTV cameras
simultaneously, handles different camera protocols (USB, IP, RTSP), and provides
frame preprocessing for AI optimization.

Requirements: 1.1, 1.3, 1.5
"""

import cv2
import numpy as np
import threading
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor

from ..config.camera_config import CameraConfig, CameraProtocol, CAMERA_SYSTEM_CONFIG


logger = logging.getLogger(__name__)


@dataclass
class FrameMetadata:
    """Metadata associated with a video frame"""
    camera_id: str
    timestamp: float
    frame_number: int
    fps: float
    zone_name: str
    resolution: Tuple[int, int]
    preprocessing_time_ms: float


class VideoStreamProcessor(ABC):
    """Abstract base class for video stream processing"""
    
    @abstractmethod
    def initialize_cameras(self, camera_configs: List[CameraConfig]) -> bool:
        """Initialize multiple CCTV camera connections"""
        pass
    
    @abstractmethod
    def get_next_frame(self, camera_id: str) -> Tuple[bool, Optional[np.ndarray], Optional[FrameMetadata]]:
        """Get next frame from specified camera with metadata"""
        pass
    
    @abstractmethod
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for AI analysis (resize, normalize, etc.)"""
        pass
    
    @abstractmethod
    def release_resources(self) -> None:
        """Clean up camera connections and resources"""
        pass


class CameraConnection:
    """Manages individual camera connection and frame capture"""
    
    def __init__(self, config: CameraConfig):
        self.config = config
        self.capture = None
        self.is_connected = False
        self.last_frame_time = 0
        self.frame_count = 0
        self.current_fps = 0.0
        self.connection_attempts = 0
        self.last_reconnect_attempt = 0
        self.frame_buffer = Queue(maxsize=CAMERA_SYSTEM_CONFIG['buffer_size'])
        self.lock = threading.Lock()
        
    def connect(self) -> bool:
        """Establish connection to camera"""
        try:
            logger.info(f"Connecting to camera {self.config.camera_id} using {self.config.protocol.value}")
            
            if self.config.protocol == CameraProtocol.USB:
                # USB camera - use integer index
                camera_index = int(self.config.connection_string)
                self.capture = cv2.VideoCapture(camera_index)
            elif self.config.protocol in [CameraProtocol.IP, CameraProtocol.RTSP]:
                # IP or RTSP camera - use connection string
                self.capture = cv2.VideoCapture(self.config.connection_string)
            else:
                logger.error(f"Unsupported camera protocol: {self.config.protocol}")
                return False
            
            if not self.capture or not self.capture.isOpened():
                logger.error(f"Failed to open camera {self.config.camera_id}")
                return False
            
            # Configure camera properties
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.resolution[0])
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.resolution[1])
            self.capture.set(cv2.CAP_PROP_FPS, self.config.target_fps)
            
            # Set buffer size to minimize latency
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test frame capture
            ret, frame = self.capture.read()
            if not ret or frame is None:
                logger.error(f"Failed to capture test frame from camera {self.config.camera_id}")
                self.capture.release()
                return False
            
            self.is_connected = True
            self.connection_attempts = 0
            logger.info(f"Successfully connected to camera {self.config.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Exception connecting to camera {self.config.camera_id}: {e}")
            if self.capture:
                self.capture.release()
            return False
    
    def disconnect(self):
        """Disconnect from camera"""
        with self.lock:
            if self.capture:
                self.capture.release()
                self.capture = None
            self.is_connected = False
            logger.info(f"Disconnected from camera {self.config.camera_id}")
    
    def capture_frame(self) -> Tuple[bool, Optional[np.ndarray], Optional[FrameMetadata]]:
        """Capture a single frame with metadata"""
        if not self.is_connected or not self.capture:
            return False, None, None
        
        try:
            with self.lock:
                ret, frame = self.capture.read()
                
            if not ret or frame is None:
                logger.warning(f"Failed to capture frame from camera {self.config.camera_id}")
                return False, None, None
            
            # Calculate FPS
            current_time = time.time()
            if self.last_frame_time > 0:
                frame_interval = current_time - self.last_frame_time
                if frame_interval > 0:
                    self.current_fps = 1.0 / frame_interval
            
            self.last_frame_time = current_time
            self.frame_count += 1
            
            # Create metadata
            metadata = FrameMetadata(
                camera_id=self.config.camera_id,
                timestamp=current_time,
                frame_number=self.frame_count,
                fps=self.current_fps,
                zone_name=self.config.zone_name,
                resolution=(frame.shape[1], frame.shape[0]),
                preprocessing_time_ms=0.0  # Will be set during preprocessing
            )
            
            return True, frame, metadata
            
        except Exception as e:
            logger.error(f"Exception capturing frame from camera {self.config.camera_id}: {e}")
            return False, None, None


class CCTVStreamProcessor(VideoStreamProcessor):
    """CCTV Stream Processor implementation with multi-camera support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or CAMERA_SYSTEM_CONFIG
        self.cameras: Dict[str, CameraConnection] = {}
        self.capture_threads: Dict[str, threading.Thread] = {}
        self.frame_buffers: Dict[str, Queue] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=self.config.get('max_cameras', 8))
        
        # Performance monitoring
        self.fps_monitoring: Dict[str, List[float]] = {}
        self.preprocessing_times: List[float] = []
        
        logger.info("CCTVStreamProcessor initialized")
    
    def initialize_cameras(self, camera_configs: List[CameraConfig]) -> bool:
        """Initialize multiple CCTV camera connections"""
        logger.info(f"Initializing {len(camera_configs)} cameras")
        
        if len(camera_configs) > self.config.get('max_cameras', 8):
            logger.warning(f"Too many cameras ({len(camera_configs)}), maximum supported: {self.config.get('max_cameras', 8)}")
            camera_configs = camera_configs[:self.config.get('max_cameras', 8)]
        
        success_count = 0
        
        for camera_config in camera_configs:
            try:
                logger.info(f"Initializing camera {camera_config.camera_id}")
                
                # Create camera connection
                camera_connection = CameraConnection(camera_config)
                
                # Attempt to connect
                if camera_connection.connect():
                    self.cameras[camera_config.camera_id] = camera_connection
                    self.frame_buffers[camera_config.camera_id] = Queue(maxsize=self.config['buffer_size'])
                    self.fps_monitoring[camera_config.camera_id] = []
                    success_count += 1
                    logger.info(f"Camera {camera_config.camera_id} initialized successfully")
                else:
                    logger.error(f"Failed to initialize camera {camera_config.camera_id}")
                    
            except Exception as e:
                logger.error(f"Exception initializing camera {camera_config.camera_id}: {e}")
        
        if success_count > 0:
            self.running = True
            self._start_capture_threads()
            logger.info(f"Successfully initialized {success_count}/{len(camera_configs)} cameras")
            return True
        else:
            logger.error("Failed to initialize any cameras")
            return False
    
    def _start_capture_threads(self):
        """Start background capture threads for all cameras"""
        for camera_id, camera_connection in self.cameras.items():
            thread = threading.Thread(
                target=self._capture_loop,
                args=(camera_id, camera_connection),
                daemon=True,
                name=f"capture_{camera_id}"
            )
            thread.start()
            self.capture_threads[camera_id] = thread
            logger.info(f"Started capture thread for camera {camera_id}")
    
    def _capture_loop(self, camera_id: str, camera_connection: CameraConnection):
        """Background capture loop for individual camera"""
        logger.info(f"Starting capture loop for camera {camera_id}")
        
        while self.running:
            try:
                success, frame, metadata = camera_connection.capture_frame()
                
                if success and frame is not None:
                    # Add frame to buffer (non-blocking)
                    try:
                        self.frame_buffers[camera_id].put_nowait((frame, metadata))
                    except:
                        # Buffer full, drop oldest frame
                        try:
                            self.frame_buffers[camera_id].get_nowait()
                            self.frame_buffers[camera_id].put_nowait((frame, metadata))
                        except:
                            pass
                    
                    # Monitor FPS
                    if metadata:
                        self.fps_monitoring[camera_id].append(metadata.fps)
                        # Keep only last 30 FPS measurements
                        if len(self.fps_monitoring[camera_id]) > 30:
                            self.fps_monitoring[camera_id] = self.fps_monitoring[camera_id][-30:]
                
                else:
                    # Frame capture failed, attempt reconnection
                    self._attempt_reconnection(camera_id, camera_connection)
                    time.sleep(1)  # Wait before retrying
                
                # Maintain target FPS
                target_fps = camera_connection.config.target_fps
                if target_fps > 0:
                    time.sleep(max(0, 1.0 / target_fps - 0.001))
                    
            except Exception as e:
                logger.error(f"Exception in capture loop for camera {camera_id}: {e}")
                time.sleep(1)
        
        logger.info(f"Capture loop ended for camera {camera_id}")
    
    def _attempt_reconnection(self, camera_id: str, camera_connection: CameraConnection):
        """Attempt to reconnect to camera with backoff"""
        current_time = time.time()
        
        # Check if enough time has passed since last reconnection attempt
        if (current_time - camera_connection.last_reconnect_attempt) < camera_connection.config.retry_interval_seconds:
            return
        
        camera_connection.connection_attempts += 1
        camera_connection.last_reconnect_attempt = current_time
        
        logger.info(f"Attempting reconnection to camera {camera_id} (attempt {camera_connection.connection_attempts})")
        
        # Disconnect first
        camera_connection.disconnect()
        
        # Wait briefly before reconnecting
        time.sleep(2)
        
        # Attempt reconnection
        if camera_connection.connect():
            logger.info(f"Successfully reconnected to camera {camera_id}")
        else:
            logger.warning(f"Failed to reconnect to camera {camera_id}")
    
    def get_next_frame(self, camera_id: str) -> Tuple[bool, Optional[np.ndarray], Optional[FrameMetadata]]:
        """Get next frame from specified camera with metadata"""
        if camera_id not in self.frame_buffers:
            logger.warning(f"Camera {camera_id} not found")
            return False, None, None
        
        try:
            # Get frame from buffer (non-blocking with timeout)
            frame, metadata = self.frame_buffers[camera_id].get(timeout=0.1)
            return True, frame, metadata
            
        except Empty:
            # No frame available
            return False, None, None
        except Exception as e:
            logger.error(f"Exception getting frame from camera {camera_id}: {e}")
            return False, None, None
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for AI analysis (resize, normalize, etc.)"""
        start_time = time.time()
        
        try:
            processed_frame = frame.copy()
            
            # Resize for AI processing if enabled
            if self.config.get('resize_for_ai', True):
                target_size = self.config.get('resize_dimensions', (640, 640))
                processed_frame = cv2.resize(processed_frame, target_size, interpolation=cv2.INTER_LINEAR)
            
            # Normalize pixels if enabled
            if self.config.get('normalize_pixels', True):
                processed_frame = processed_frame.astype(np.float32) / 255.0
            
            # Denoising if enabled
            if self.config.get('enable_denoising', False):
                processed_frame = cv2.fastNlMeansDenoisingColored(
                    (processed_frame * 255).astype(np.uint8) if processed_frame.dtype == np.float32 else processed_frame
                )
                if processed_frame.dtype == np.uint8 and self.config.get('normalize_pixels', True):
                    processed_frame = processed_frame.astype(np.float32) / 255.0
            
            # Track preprocessing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self.preprocessing_times.append(processing_time)
            
            # Keep only last 100 measurements
            if len(self.preprocessing_times) > 100:
                self.preprocessing_times = self.preprocessing_times[-100:]
            
            # Check if preprocessing time exceeds 50ms requirement
            if processing_time > 50:
                logger.warning(f"Frame preprocessing took {processing_time:.2f}ms (exceeds 50ms requirement)")
            
            return processed_frame
            
        except Exception as e:
            logger.error(f"Exception during frame preprocessing: {e}")
            return frame
    
    def get_camera_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status information for all cameras"""
        status = {}
        
        for camera_id, camera_connection in self.cameras.items():
            fps_history = self.fps_monitoring.get(camera_id, [])
            avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0.0
            
            status[camera_id] = {
                'connected': camera_connection.is_connected,
                'zone': camera_connection.config.zone_name,
                'protocol': camera_connection.config.protocol.value,
                'target_fps': camera_connection.config.target_fps,
                'current_fps': avg_fps,
                'frame_count': camera_connection.frame_count,
                'connection_attempts': camera_connection.connection_attempts,
                'buffer_size': self.frame_buffers[camera_id].qsize() if camera_id in self.frame_buffers else 0
            }
        
        return status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        avg_preprocessing_time = sum(self.preprocessing_times) / len(self.preprocessing_times) if self.preprocessing_times else 0.0
        
        return {
            'active_cameras': len(self.cameras),
            'running': self.running,
            'average_preprocessing_time_ms': avg_preprocessing_time,
            'preprocessing_within_50ms': sum(1 for t in self.preprocessing_times if t <= 50) / len(self.preprocessing_times) if self.preprocessing_times else 0.0,
            'camera_status': self.get_camera_status()
        }
    
    def release_resources(self) -> None:
        """Clean up camera connections and resources"""
        logger.info("Releasing CCTV stream processor resources")
        
        # Stop capture threads
        self.running = False
        
        # Wait for capture threads to finish
        for camera_id, thread in self.capture_threads.items():
            if thread.is_alive():
                logger.info(f"Waiting for capture thread {camera_id} to finish")
                thread.join(timeout=5)
                if thread.is_alive():
                    logger.warning(f"Capture thread {camera_id} did not finish gracefully")
        
        # Disconnect all cameras
        for camera_id, camera_connection in self.cameras.items():
            logger.info(f"Disconnecting camera {camera_id}")
            camera_connection.disconnect()
        
        # Clean up resources
        self.cameras.clear()
        self.capture_threads.clear()
        self.frame_buffers.clear()
        self.fps_monitoring.clear()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        logger.info("CCTV stream processor resources released")


def create_stream_processor(config: Optional[Dict[str, Any]] = None) -> CCTVStreamProcessor:
    """Factory function to create CCTV stream processor"""
    return CCTVStreamProcessor(config)