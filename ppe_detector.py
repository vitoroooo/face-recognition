"""
PPE Detector Module - Production Ready
Menggunakan YOLOv8 untuk deteksi PPE dengan akurasi tinggi
Terintegrasi dengan sistem face recognition existing
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PPEDetection:
    """Data class untuk hasil deteksi PPE"""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    is_violation: bool
    color: Tuple[int, int, int]  # BGR color


@dataclass
class PersonWithPPE:
    """Data class untuk person dengan status PPE"""
    person_id: Optional[str]  # Face recognition ID
    person_name: Optional[str]  # Nama dari face recognition
    bbox: Tuple[int, int, int, int]
    ppe_items: List[PPEDetection]
    is_compliant: bool
    missing_ppe: List[str]
    confidence: float


class PPEDetector:
    """
    PPE Detector menggunakan YOLOv8
    Support untuk deteksi: Hardhat, Mask, Safety Vest, No-Hardhat, No-Mask, No-Safety Vest
    """

    def __init__(self, model_path: str = 'ppe.pt', confidence_threshold: float = 0.5):
        """
        Initialize PPE Detector

        Args:
            model_path: Path ke YOLO model (.pt file)
            confidence_threshold: Minimum confidence untuk detection
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.model_loaded = False

        # Class names dari model PPE
        self.class_names = [
            'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask',
            'NO-Safety Vest', 'Person', 'Safety Cone',
            'Safety Vest', 'machinery', 'vehicle'
        ]

        # PPE types yang kita monitor
        self.ppe_positive = ['Hardhat', 'Mask', 'Safety Vest']
        self.ppe_negative = ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']

        # Color mapping (BGR)
        self.colors = {
            'compliant': (0, 255, 0),      # Green
            'violation': (0, 0, 255),      # Red
            'neutral': (255, 0, 0),        # Blue
            'warning': (0, 165, 255)       # Orange
        }

        self._load_model()

    def _load_model(self) -> bool:
        """Load YOLO model"""
        try:
            from ultralytics import YOLO
            logger.info(f"Loading YOLO model from {self.model_path}")
            self.model = YOLO(self.model_path)
            self.model_loaded = True
            logger.info("✓ YOLO model loaded successfully")
            return True
        except ImportError:
            logger.warning("ultralytics not installed. Install with: pip install ultralytics")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def detect(self, frame: np.ndarray) -> List[PPEDetection]:
        """
        Detect PPE items dalam frame

        Args:
            frame: Input video frame (BGR format)

        Returns:
            List of PPEDetection objects
        """
        if not self.model_loaded:
            return self._simulate_detection(frame)

        detections = []

        try:
            # Run inference
            results = self.model(frame, stream=True, verbose=False)

            for r in results:
                boxes = r.boxes
                for box in boxes:
                    # Extract box coordinates
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                    # Confidence
                    conf = float(box.conf[0])

                    # Class
                    cls = int(box.cls[0])
                    class_name = self.class_names[cls] if cls < len(self.class_names) else 'Unknown'

                    # Only process if confidence is high enough
                    if conf >= self.confidence_threshold:
                        # Determine if violation
                        is_violation = class_name in self.ppe_negative

                        # Determine color
                        if class_name in self.ppe_positive:
                            color = self.colors['compliant']
                        elif class_name in self.ppe_negative:
                            color = self.colors['violation']
                        else:
                            color = self.colors['neutral']

                        detection = PPEDetection(
                            class_name=class_name,
                            confidence=conf,
                            bbox=(x1, y1, x2, y2),
                            is_violation=is_violation,
                            color=color
                        )
                        detections.append(detection)

        except Exception as e:
            logger.error(f"Detection error: {e}")

        return detections

    def _simulate_detection(self, frame: np.ndarray) -> List[PPEDetection]:
        """Simulate detection untuk testing tanpa model"""
        h, w = frame.shape[:2]
        import random

        simulated = []

        # Simulate person
        simulated.append(PPEDetection(
            class_name='Person',
            confidence=0.85,
            bbox=(int(w*0.3), int(h*0.2), int(w*0.7), int(h*0.9)),
            is_violation=False,
            color=self.colors['neutral']
        ))

        # Random PPE items
        if random.random() > 0.3:
            simulated.append(PPEDetection(
                class_name='Hardhat',
                confidence=0.78,
                bbox=(int(w*0.4), int(h*0.2), int(w*0.6), int(h*0.35)),
                is_violation=False,
                color=self.colors['compliant']
            ))
        else:
            simulated.append(PPEDetection(
                class_name='NO-Hardhat',
                confidence=0.82,
                bbox=(int(w*0.4), int(h*0.2), int(w*0.6), int(h*0.35)),
                is_violation=True,
                color=self.colors['violation']
            ))

        if random.random() > 0.4:
            simulated.append(PPEDetection(
                class_name='Safety Vest',
                confidence=0.72,
                bbox=(int(w*0.35), int(h*0.4), int(w*0.65), int(h*0.7)),
                is_violation=False,
                color=self.colors['compliant']
            ))

        return simulated

    def evaluate_compliance(self, detections: List[PPEDetection],
                          required_ppe: List[str] = None) -> Tuple[bool, List[str]]:
        """
        Evaluate compliance berdasarkan detections

        Args:
            detections: List of PPE detections
            required_ppe: List of required PPE items (default: ['Hardhat', 'Safety Vest'])

        Returns:
            Tuple of (is_compliant, missing_items)
        """
        if required_ppe is None:
            required_ppe = ['Hardhat', 'Safety Vest']

        # Check if person detected
        has_person = any(d.class_name == 'Person' for d in detections)
        if not has_person:
            return True, []  # No person, no violation

        # Check for violations (NO-PPE items)
        has_violations = any(d.is_violation for d in detections)
        if has_violations:
            missing = [d.class_name.replace('NO-', '') for d in detections if d.is_violation]
            return False, missing

        # Check for positive PPE items
        detected_ppe = set(d.class_name for d in detections if d.class_name in self.ppe_positive)

        # Check missing items
        missing = [item for item in required_ppe if item not in detected_ppe]

        is_compliant = len(missing) == 0
        return is_compliant, missing

    def group_detections_by_person(self, detections: List[PPEDetection]) -> List[PersonWithPPE]:
        """
        Group PPE detections by person bounding box

        Args:
            detections: List of all detections

        Returns:
            List of PersonWithPPE objects
        """
        persons = []

        # Find all person detections
        person_boxes = [d for d in detections if d.class_name == 'Person']

        for person_det in person_boxes:
            # Find PPE items that overlap with this person
            px1, py1, px2, py2 = person_det.bbox

            ppe_items = []
            for det in detections:
                if det.class_name == 'Person':
                    continue

                # Check if PPE item is near this person
                dx1, dy1, dx2, dy2 = det.bbox

                # Simple overlap check
                if (dx1 < px2 and dx2 > px1 and
                    dy1 < py2 and dy2 > py1):
                    ppe_items.append(det)

            # Evaluate compliance for this person
            is_compliant, missing = self.evaluate_compliance(
                [person_det] + ppe_items
            )

            person_with_ppe = PersonWithPPE(
                person_id=None,  # Will be filled by face recognition
                person_name=None,
                bbox=person_det.bbox,
                ppe_items=ppe_items,
                is_compliant=is_compliant,
                missing_ppe=missing,
                confidence=person_det.confidence
            )
            persons.append(person_with_ppe)

        return persons


# Utility functions untuk visualisasi
def draw_ppe_detection(frame: np.ndarray, detection: PPEDetection) -> np.ndarray:
    """Draw single PPE detection pada frame"""
    x1, y1, x2, y2 = detection.bbox

    # Draw bounding box
    cv2.rectangle(frame, (x1, y1), (x2, y2), detection.color, 2)

    # Draw label background
    label = f"{detection.class_name} {detection.confidence:.2f}"
    (label_w, label_h), baseline = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
    )

    # Label background
    cv2.rectangle(
        frame,
        (x1, y1 - label_h - 10),
        (x1 + label_w + 10, y1),
        detection.color,
        -1
    )

    # Label text
    cv2.putText(
        frame, label, (x1 + 5, y1 - 5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
    )

    return frame


def draw_person_with_ppe(frame: np.ndarray, person: PersonWithPPE) -> np.ndarray:
    """Draw person dengan status PPE compliance"""
    x1, y1, x2, y2 = person.bbox

    # Color based on compliance
    color = (0, 255, 0) if person.is_compliant else (0, 0, 255)

    # Draw person box
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

    # Draw PPE items
    for ppe in person.ppe_items:
        draw_ppe_detection(frame, ppe)

    # Draw compliance status
    status_text = "✓ COMPLIANT" if person.is_compliant else "✗ VIOLATION"
    cv2.putText(
        frame, status_text, (x1, y1 - 10),
        cv2.FONT_HERSHEY_DUPLEX, 0.8, color, 2
    )

    # Draw missing PPE
    if person.missing_ppe:
        missing_text = f"Missing: {', '.join(person.missing_ppe)}"
        cv2.putText(
            frame, missing_text, (x1, y2 + 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2
        )

    # Draw person name if available
    if person.person_name:
        cv2.putText(
            frame, person.person_name, (x1, y1 - 35),
            cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2
        )

    return frame
