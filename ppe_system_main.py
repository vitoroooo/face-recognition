"""
PPE Compliance Monitoring System - Main Application
Integrated Face Recognition + PPE Detection dengan Insta360 Link 2
UI/UX Professional dengan statistik real-time
"""

import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import time
import json
from pathlib import Path

from ppe_detector import PPEDetector, PersonWithPPE, draw_person_with_ppe


class FaceRecognitionIntegration:
    """Integrasi sistem face recognition existing dengan PPE detection"""
    
    def __init__(self, faces_dir: str = "faces"):
        """
        Initialize face recognition system
        
        Args:
            faces_dir: Directory containing known faces
        """
        self.faces_dir = faces_dir
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load semua wajah dari directory faces/"""
        print(f"🔍 Loading known faces dari {self.faces_dir}/...")
        
        if not os.path.exists(self.faces_dir):
            print(f"⚠️  Directory {self.faces_dir}/ tidak ditemukan")
            return
        
        face_files = [f for f in os.listdir(self.faces_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        for filename in face_files:
            filepath = os.path.join(self.faces_dir, filename)
            try:
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    self.known_face_encodings.append(encodings[0])
                    name = os.path.splitext(filename)[0].title()
                    self.known_face_names.append(name)
                    print(f"   ✓ Loaded: {name}")
                else:
                    print(f"   ✗ No face found in {filename}")
            except Exception as e:
                print(f"   ✗ Error loading {filename}: {e}")
        
        print(f"✓ Loaded {len(self.known_face_names)} known faces\n")
    
    def recognize_faces(self, frame: np.ndarray) -> List[Dict]:
        """
        Recognize faces dalam frame
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            List of dict dengan face info
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        faces = []
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Match dengan known faces
            matches = face_recognition.compare_faces(
                self.known_face_encodings, face_encoding, tolerance=0.6
            )
            name = "Unknown"
            confidence = 0.0
            
            if True in matches:
                # Get distances
                face_distances = face_recognition.face_distance(
                    self.known_face_encodings, face_encoding
                )
                best_match_index = np.argmin(face_distances)
                
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
            
            faces.append({
                'name': name,
                'bbox': (left, top, right, bottom),
                'confidence': confidence
            })
        
        return faces


class PPEComplianceSystem:
    """Main PPE Compliance Monitoring System"""
    
    def __init__(self, camera_index: int = 1, model_path: str = None):
        """
        Initialize PPE Compliance System
        
        Args:
            camera_index: Camera index (1 untuk Insta360 Link 2)
            model_path: Path ke PPE model file
        """
        self.camera_index = camera_index
        self.model_path = model_path or "ppe_reference/ppe.pt"
        
        # Initialize components
        print("🚀 Initializing PPE Compliance System...")
        print("=" * 60)
        
        self.ppe_detector = PPEDetector(
            model_path=self.model_path,
            confidence_threshold=0.5
        )
        
        self.face_recognizer = FaceRecognitionIntegration()
        
        # Statistics
        self.stats = {
            'total_frames': 0,
            'total_persons': 0,
            'compliant_count': 0,
            'violation_count': 0,
            'start_time': time.time(),
            'violations_log': []
        }
        
        # UI settings
        self.show_debug = True
        self.show_fps = True
        self.show_stats = True
        
        # Camera
        self.cap = None
        
        print("=" * 60)
        print("✓ System initialized successfully!\n")
    
    def find_insta360(self) -> int:
        """Auto-detect Insta360 Link 2"""
        print("🔍 Searching for Insta360 Link 2...")
        
        for index in range(5):
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    
                    if width == 1280 and height == 720:
                        print(f"   ✓ Insta360 Link 2 found at index {index}!")
                        cap.release()
                        return index
                    else:
                        print(f"   - Camera at index {index}: {width}x{height}")
                
                cap.release()
        
        print("   ⚠️  Insta360 not found, using default camera")
        return 0
    
    def initialize_camera(self) -> bool:
        """Initialize camera dengan Insta360 Link 2"""
        camera_idx = self.find_insta360()
        
        print(f"\n📷 Opening camera index {camera_idx}...")
        self.cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            print("❌ Failed to open camera!")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✓ Camera opened: {width}x{height}\n")
        return True
    
    def associate_faces_with_persons(self, faces: List[Dict], 
                                     persons: List[PersonWithPPE]) -> List[PersonWithPPE]:
        """
        Associate detected faces dengan persons from PPE detection
        
        Args:
            faces: List of face detections
            persons: List of persons with PPE
            
        Returns:
            Updated list of persons with face info
        """
        for face in faces:
            fx1, fy1, fx2, fy2 = face['bbox']
            face_center_x = (fx1 + fx2) / 2
            face_center_y = (fy1 + fy2) / 2
            
            # Find closest person
            best_person = None
            best_distance = float('inf')
            
            for person in persons:
                px1, py1, px2, py2 = person.bbox
                
                # Check if face is inside person bbox
                if (fx1 >= px1 and fx2 <= px2 and 
                    fy1 >= py1 and fy2 <= py2):
                    person_center_x = (px1 + px2) / 2
                    person_center_y = (py1 + py2) / 2
                    
                    distance = ((face_center_x - person_center_x)**2 + 
                              (face_center_y - person_center_y)**2) ** 0.5
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_person = person
            
            if best_person:
                best_person.person_name = face['name']
                best_person.person_id = face['name'].lower()
        
        return persons
    
    def draw_ui(self, frame: np.ndarray) -> np.ndarray:
        """Draw UI overlay pada frame"""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        
        # Semi-transparent header bar
        cv2.rectangle(overlay, (0, 0), (w, 100), (40, 40, 40), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Title
        cv2.putText(frame, "PPE COMPLIANCE MONITORING SYSTEM", (20, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
        
        # Camera info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Insta360 Link 2 | {timestamp}", (20, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        if self.show_stats:
            # Stats panel
            stats_y = 120
            elapsed = time.time() - self.stats['start_time']
            fps = self.stats['total_frames'] / elapsed if elapsed > 0 else 0
            
            # Semi-transparent stats panel
            overlay = frame.copy()
            cv2.rectangle(overlay, (w - 350, stats_y - 20), (w - 10, stats_y + 180), 
                         (40, 40, 40), -1)
            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
            
            # Stats text
            stats_text = [
                f"FPS: {fps:.1f}",
                f"Frames: {self.stats['total_frames']}",
                f"Persons Detected: {self.stats['total_persons']}",
                f"Compliant: {self.stats['compliant_count']}",
                f"Violations: {self.stats['violation_count']}",
            ]
            
            for i, text in enumerate(stats_text):
                y_pos = stats_y + (i * 35)
                color = (100, 255, 100) if i >= 3 and i == 3 else (255, 100, 100) if i == 4 else (255, 255, 255)
                cv2.putText(frame, text, (w - 330, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Controls help
        if self.show_debug:
            help_y = h - 120
            overlay = frame.copy()
            cv2.rectangle(overlay, (10, help_y - 10), (400, h - 10), (40, 40, 40), -1)
            frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
            
            controls = [
                "Q - Quit",
                "S - Screenshot",
                "D - Toggle Debug",
                "R - Reset Stats"
            ]
            
            for i, text in enumerate(controls):
                cv2.putText(frame, text, (20, help_y + 20 + (i * 25)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def log_violation(self, person: PersonWithPPE):
        """Log violation ke file"""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'person_name': person.person_name or 'Unknown',
            'person_id': person.person_id or 'unknown',
            'missing_ppe': person.missing_ppe,
            'confidence': person.confidence
        }
        
        self.stats['violations_log'].append(violation)
        
        # Save to file setiap 10 violations
        if len(self.stats['violations_log']) % 10 == 0:
            self.save_violations_log()
    
    def save_violations_log(self):
        """Save violations log ke JSON file"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"violations_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(log_file, 'w') as f:
            json.dump(self.stats['violations_log'], f, indent=2)
    
    def run(self):
        """Main loop untuk menjalankan sistem"""
        if not self.initialize_camera():
            return
        
        print("🎯 Required PPE: Hardhat, Safety Vest")
        print("\n⌨️  Controls:")
        print("   Q - Quit")
        print("   S - Screenshot")
        print("   D - Toggle Debug Info")
        print("   R - Reset Statistics")
        print("\n🚀 Starting monitoring...\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to capture frame")
                    break
                
                self.stats['total_frames'] += 1
                
                # PPE Detection
                ppe_detections = self.ppe_detector.detect(frame)
                persons = self.ppe_detector.group_detections_by_person(ppe_detections)
                
                # Face Recognition (run setiap 5 frames untuk performa)
                if self.stats['total_frames'] % 5 == 0:
                    faces = self.face_recognizer.recognize_faces(frame)
                    persons = self.associate_faces_with_persons(faces, persons)
                
                # Update statistics
                self.stats['total_persons'] += len(persons)
                for person in persons:
                    if person.is_compliant:
                        self.stats['compliant_count'] += 1
                    else:
                        self.stats['violation_count'] += 1
                        self.log_violation(person)
                
                # Draw detections
                for person in persons:
                    frame = draw_person_with_ppe(frame, person)
                
                # Draw UI
                frame = self.draw_ui(frame)
                
                # Display
                cv2.imshow('PPE Compliance System - Insta360 Link 2', frame)
                
                # Keyboard controls
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n🛑 Shutting down system...")
                    break
                elif key == ord('s'):
                    screenshot_path = f"screenshots/ppe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    os.makedirs("screenshots", exist_ok=True)
                    cv2.imwrite(screenshot_path, frame)
                    print(f"📸 Screenshot saved: {screenshot_path}")
                elif key == ord('d'):
                    self.show_debug = not self.show_debug
                    print(f"🔧 Debug info: {'ON' if self.show_debug else 'OFF'}")
                elif key == ord('r'):
                    self.stats['compliant_count'] = 0
                    self.stats['violation_count'] = 0
                    self.stats['total_persons'] = 0
                    self.stats['start_time'] = time.time()
                    print("🔄 Statistics reset")
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            # Cleanup & save final report
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources dan save final report"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        
        # Save violations log
        if self.stats['violations_log']:
            self.save_violations_log()
        
        # Print final statistics
        elapsed = time.time() - self.stats['start_time']
        print("\n" + "=" * 60)
        print("📊 FINAL STATISTICS")
        print("=" * 60)
        print(f"Total Runtime: {elapsed:.2f} seconds")
        print(f"Total Frames: {self.stats['total_frames']}")
        print(f"Average FPS: {self.stats['total_frames']/elapsed:.2f}")
        print(f"Total Persons Detected: {self.stats['total_persons']}")
        print(f"Compliant: {self.stats['compliant_count']}")
        print(f"Violations: {self.stats['violation_count']}")
        
        if self.stats['total_persons'] > 0:
            compliance_rate = (self.stats['compliant_count'] / self.stats['total_persons']) * 100
            print(f"Compliance Rate: {compliance_rate:.1f}%")
        
        print("=" * 60)
        print("✅ System shutdown complete")


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("🦺 PPE COMPLIANCE MONITORING SYSTEM")
    print("   Integrated Face Recognition + PPE Detection")
    print("   Powered by YOLOv8 & Insta360 Link 2")
    print("=" * 60 + "\n")
    
    # Initialize and run system
    system = PPEComplianceSystem(
        camera_index=1,  # Insta360 Link 2
        model_path="ppe_reference/ppe.pt"
    )
    
    system.run()


if __name__ == "__main__":
    main()
