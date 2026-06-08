"""
Video stream processing and camera management

This module provides CCTV stream processing capabilities with multi-camera support,
different protocol handling (USB, IP, RTSP), and frame preprocessing for AI analysis.
"""

from .stream_processor import (
    VideoStreamProcessor,
    CCTVStreamProcessor,
    CameraConnection,
    FrameMetadata,
    create_stream_processor
)

__all__ = [
    'VideoStreamProcessor',
    'CCTVStreamProcessor', 
    'CameraConnection',
    'FrameMetadata',
    'create_stream_processor'
]