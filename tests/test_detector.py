"""
Unit tests for solar defect detection, NMS bounding box deduplication, and filtering.
"""

import pytest
import numpy as np
import cv2

from src.detector import SolarDefectDetector, DefectDetection
from src.config import DetectorConfig, DefectClass


@pytest.fixture
def detector():
    return SolarDefectDetector()


def test_clean_panel_detection(detector):
    clean_panel = np.full((512, 640, 3), (85, 55, 30), dtype=np.uint8)
    cv2.rectangle(clean_panel, (0, 0), (639, 511), (180, 180, 190), 8)
    detections = detector.detect(clean_panel)
    assert len(detections) == 0


def test_hotspot_detection(detector):
    img = np.full((512, 640, 3), (85, 55, 30), dtype=np.uint8)
    cv2.circle(img, (300, 200), 30, (20, 120, 245), -1)
    cv2.circle(img, (300, 200), 10, (255, 255, 255), -1)

    detections = detector.detect(img)
    assert len(detections) >= 1
    det = detections[0]
    assert det.category == DefectClass.HOTSPOT
    assert det.confidence >= 0.70
    assert det.estimated_temp_delta > 10.0


def test_soiling_detection(detector):
    img = np.full((512, 640, 3), (85, 55, 30), dtype=np.uint8)
    # Earthy tan dust patch (Hue ~ 20)
    dirt_pts = np.array([[300, 200], [360, 190], [390, 240], [350, 270], [290, 230]])
    cv2.fillPoly(img, [dirt_pts], (45, 95, 120))

    detections = detector.detect(img)
    assert len(detections) >= 1
    assert any(d.category == DefectClass.SOILING for d in detections)


def test_apply_nms():
    box1 = (100, 100, 50, 50)
    box2 = (105, 105, 50, 50)  # High overlap with box1
    box3 = (300, 300, 50, 50)  # Distinct non-overlapping box

    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    dets = [
        DefectDetection(box1, DefectClass.HOTSPOT, 0.90, 2500, cnt, 50.0, 25.0),
        DefectDetection(box2, DefectClass.HOTSPOT, 0.80, 2500, cnt, 45.0, 22.0),
        DefectDetection(box3, DefectClass.HOTSPOT, 0.85, 2500, cnt, 2500, 20.0),
    ]

    filtered = SolarDefectDetector.apply_nms(dets, iou_thresh=0.40)
    assert len(filtered) == 2
    # Highest confidence box should be kept
    assert filtered[0].confidence == 0.90
    assert filtered[1].confidence == 0.85


def test_iou_calculation():
    boxA = (100, 100, 50, 50)
    boxB = (100, 100, 50, 50)
    assert SolarDefectDetector._calculate_iou(boxA, boxB) == 1.0

    boxC = (200, 200, 50, 50)
    assert SolarDefectDetector._calculate_iou(boxA, boxC) == 0.0
