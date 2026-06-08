"""
PPE Detection Demo with Insta360 Link 2

This demo script demonstrates PPE (Personal Protective Equipment) detection
using Insta360 Link 2 camera for real-time monitoring.

Features:
- Auto-detect Insta360 Link 2 camera
- YOLOv8-based PPE detection (helmet, vest, glasses, etc.)
- Real-time visualization with bounding boxes
- Integration ready with existing face recognition system

Usage:
    python demo_ppe_insta360.py

Requirements:
    pip install ultralytics torch torchvision
"""

import cv2
import numpy as np
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Try to import YOLO (will install later)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("⚠️  WARNING: ultralytics not installed. Run: pip install ultralytics")
    print("   Demo will run in simulation mode.\n")


class PPEDetector:
    """PPE Detection using YOLOv8"""
    
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """
        Initialize PPE Detector
        
        Args:
            model_path: Path to YOLO model file
        """
        self.model = None
        self.model_available = False
        
        if YOLO_AVAILABLE:
            try:
                print(f"Loading YOLO model: {model_path}")
                self.model = YOLO(model_path)
                self.model_available = True
                print("✓ YOLO model loaded successfully")
            except Exception as e:
                print(f"✗ Failed to load YOLO model: {e}")
                print("  Will run in simulation mode")
        
        # PPE classes we're interested in
        self.ppe_classes = {
            'helmet': 0,
            'safety_vest': 1,
            'safety_glasses': 2,
            'gloves': 3,
            'person': 4
        }
    
    def detect(self, frame: np.ndarray, confidence: float = 0.5) -> List[Dict]:
        """
        Detect PPE items in frame
        
        Args:
            frame: Input video frame
            confidence: Minimum confidence threshold
            
        Returns:
            List of detection dictionaries
        """
        if not self.model_available:
            # Simulation mode - return dummy detections
            return self._simulate_detections(frame)
        
        try:
            # Run YOLO detection
            results = self.model(frame, conf=confidence, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    detection = {
                        'class_name': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': box.xyxy[0].cpu().numpy().tolist(),
                        'class_id': int(box.cls)
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def _simulate_detections(self, frame: np.ndarray) -> List[Dict]:
        """
        Simulate detections for demo purposes when YOLO not available
        
        Args:
            frame: Input frame
            
        Returns:
            List of simulated detections
        """
        h, w = frame.shape[:2]
        
        # Simulate a person in center of frame
        simulated = [
            {
                'class_name': 'person',
                'confidence': 0.85,
                'bbox': [w*0.3, h*0.2, w*0.7, h*0.9],
                'class_id': 4
            }
        ]
        
        # Randomly simulate PPE items
        import random
        if random.random() > 0.5:
            simulated.append({
                'class_name': 'helmet',
                'confidence': 0.75,
                'bbox': [w*0.4, h*0.2, w*0.6, h*0.35],
                'class_id': 0
            })
        
        if random.random() > 0.5:
            simulated.append({
                'class_name': 'safety_vest',
                'confidence': 0.70,
                'bbox': [w*0.35, h*0.4, w*0.65, h*0.7],
                'class_id': 1
            })
        
        return simulated


class Insta360Detector:
    """Detect and configure Insta360 Link 2 camera"""
    
    @staticmethod
    def find_insta360() -> Optional[int]:
        """
        Find Insta360 Link 2 camera index
        
        Returns:
            Camera index if found, None otherwise
        """
        print("🔍 Searching for Insta360 Link 2...")
        
        for index in range(5):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    # Insta360 Link 2 typically runs at 1280x720
                    if width == 1280 and height == 720:
                        print(f"   ✓ Insta360 Link 2 found at index {index}!")
                        print(f"   Resolution: {width}x{height}")
                        cap.release()
                        return index
                    else:
                        print(f"   - Camera at index {index}: {width}x{height}")
                
                cap.release()
        
        print("   ⚠️  Insta360 Link 2 not found, using default camera")
        return 0


def evaluate_ppe_compliance(detections: List[Dict], 
                            required_ppe: List[str] = ['helmet', 'safety_vest']) -> Tuple[bool, List[str]]:
    """
    Evaluate PPE compliance based on detections
    
    Args:
        detections: List of detected items
        required_ppe: List of required PPE items
        
    Returns:
        Tuple of (is_compliant, missing_items)
    """
    detected_ppe = set()
    has_person = False
    
    for det in detections:
        class_name = det['class_name']
        if class_name == 'person':
            has_person = True
        elif class_name in required_ppe:
            detected_ppe.add(class_name)
    
    if not has_person:
        return True, []  # No person detected, no violation
    
    missing = [item for item in required_ppe if item not in detected_ppe]
    is_compliant = len(missing) == 0
    
    return is_compliant, missing


def draw_detections(frame: np.ndarray, detections: List[Dict], 
                   compliance_status: Tuple[bool, List[str]]) -> np.ndarray:
    """
    Draw detection results on frame
    
    Args:
        frame: Input frame
        detections: List of detections
        compliance_status: Tuple of (is_compliant, missing_items)
        
    Returns:
        Annotated frame
    """
    annotated = frame.copy()
    is_compliant, missing = compliance_status
    
    # Draw bounding boxes
    for det in detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        class_name = det['class_name']
        confidence = det['confidence']
        
        # Color based on class
        if class_name == 'person':
            color = (0, 255, 0) if is_compliant else (0, 0, 255)
        else:
            color = (0, 255, 255)  # Yellow for PPE items
        
        # Draw box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        
        # Draw label
        label = f"{class_name}: {confidence:.2f}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(annotated, (x1, y1 - label_h - 10), (x1 + label_w + 10, y1), color, -1)
        cv2.putText(annotated, label, (x1 + 5, y1 - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Draw compliance status
    status_text = "✓ COMPLIANT" if is_compliant else "✗ VIOLATION"
    status_color = (0, 255, 0) if is_compliant else (0, 0, 255)
    
    cv2.putText(annotated, status_text, (10, 40), 
               cv2.FONT_HERSHEY_DUPLEX, 1.0, status_color, 2)
    
    # Draw missing PPE items
    if missing:
        missing_text = f"Missing: {', '.join(missing)}"
        cv2.putText(annotated, missing_text, (10, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return annotated


def main():
    """Main demo function"""
    print("=" * 60)
    print("🦺 PPE Detection Demo with Insta360 Link 2")
    print("=" * 60)
    print()
    
    # Find Insta360 Link 2
    camera_index = Insta360Detector.find_insta360()
    
    # Initialize PPE detector
    print("\n🤖 Initializing PPE Detector...")
    detector = PPEDetector()
    
    if not detector.model_available:
        print("\n📝 SIMULATION MODE")
        print("   Install ultralytics to enable real detection:")
        print("   pip install ultralytics torch torchvision")
        print()
    
    # Open camera
    print(f"📷 Opening camera index {camera_index}...")
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    # Configure camera for best quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"✓ Camera opened: {actual_width}x{actual_height}")
    print()
    print("🎯 PPE Compliance Rules:")
    print("   Required: Helmet, Safety Vest")
    print()
    print("⌨️  Controls:")
    print("   Q - Quit")
    print("   S - Take screenshot")
    print("   D - Toggle debug info")
    print()
    print("🚀 Starting detection...")
    print()
    
    # Required PPE items
    required_ppe = ['helmet', 'safety_vest']
    
    # Performance tracking
    frame_count = 0
    start_time = time.time()
    show_debug = True
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            frame_count += 1
            
            # Detect PPE items
            detections = detector.detect(frame)
            
            # Evaluate compliance
            compliance_status = evaluate_ppe_compliance(detections, required_ppe)
            
            # Annotate frame
            annotated = draw_detections(frame, detections, compliance_status)
            
            # Add debug info
            if show_debug:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fps = frame_count / (time.time() - start_time) if time.time() > start_time else 0
                
                cv2.putText(annotated, f"Time: {timestamp}", (10, annotated.shape[0] - 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(annotated, f"FPS: {fps:.1f}", (10, annotated.shape[0] - 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(annotated, f"Detections: {len(detections)}", (10, annotated.shape[0] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(annotated, f"Frame: {frame_count}", (10, annotated.shape[0] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display
            cv2.imshow('PPE Detection - Insta360 Link 2', annotated)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\n🛑 Stopping detection...")
                break
            elif key == ord('s'):
                screenshot_path = f"ppe_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(screenshot_path, annotated)
                print(f"📸 Screenshot saved: {screenshot_path}")
            elif key == ord('d'):
                show_debug = not show_debug
                print(f"🔧 Debug info: {'ON' if show_debug else 'OFF'}")
    
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    
    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Statistics
        elapsed = time.time() - start_time
        avg_fps = frame_count / elapsed if elapsed > 0 else 0
        
        print()
        print("=" * 60)
        print("📊 Session Statistics")
        print("=" * 60)
        print(f"Total frames processed: {frame_count}")
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Average FPS: {avg_fps:.2f}")
        print()
        print("✅ Demo completed successfully!")


if __name__ == "__main__":
    main()
