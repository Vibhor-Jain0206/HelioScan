"""
Unit tests for IoU and benchmark evaluation metrics.
"""

from src.metrics import compute_iou, evaluate_detections
from src.detector import DefectDetection
from src.config import DefectClass
import numpy as np


def test_compute_iou():
    box1 = (0, 0, 10, 10)
    box2 = (0, 0, 10, 10)
    assert compute_iou(box1, box2) == 1.0

    box3 = (20, 20, 10, 10)
    assert compute_iou(box1, box3) == 0.0

    box4 = (5, 0, 10, 10)
    iou = compute_iou(box1, box4)
    assert 0.3 < iou < 0.4


def test_evaluate_detections_perfect():
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    gt = [{"category": "Hotspot", "bbox": [100, 100, 50, 50]}]
    preds = [DefectDetection((100, 100, 50, 50), DefectClass.HOTSPOT, 0.9, 2500, cnt, 30.0, 15.0)]

    res = evaluate_detections(gt, preds, iou_thresh=0.5)
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0
    assert res["mean_iou"] == 1.0
    assert res["tp"] == 1
    assert res["fp"] == 0
    assert res["fn"] == 0


def test_evaluate_detections_no_match():
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    gt = [{"category": "Hotspot", "bbox": [100, 100, 50, 50]}]
    preds = [DefectDetection((300, 300, 50, 50), DefectClass.HOTSPOT, 0.9, 2500, cnt, 30.0, 15.0)]

    res = evaluate_detections(gt, preds, iou_thresh=0.5)
    assert res["precision"] == 0.0
    assert res["recall"] == 0.0
    assert res["tp"] == 0
    assert res["fp"] == 1
    assert res["fn"] == 1
