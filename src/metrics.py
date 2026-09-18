"""
Evaluation metrics: Intersection over Union (IoU), Precision, Recall, F1-Score,
and Mean Average Precision at IoU 0.5 (mAP@0.5).
"""

from typing import List, Dict, Tuple, Any
import numpy as np


def compute_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    inter_w = max(0, xB - xA)
    inter_h = max(0, yB - yA)
    inter_area = inter_w * inter_h

    areaA = boxA[2] * boxA[3]
    areaB = boxB[2] * boxB[3]
    union_area = float(areaA + areaB - inter_area)

    return inter_area / union_area if union_area > 0 else 0.0


def evaluate_detections(
    ground_truth: List[Dict[str, Any]],
    predictions: List[Any],
    iou_thresh: float = 0.50
) -> Dict[str, float]:
    if not ground_truth and not predictions:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "mean_iou": 1.0, "tp": 0, "fp": 0, "fn": 0}

    if not ground_truth:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mean_iou": 0.0, "tp": 0, "fp": len(predictions), "fn": 0}

    if not predictions:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0, "mean_iou": 0.0, "tp": 0, "fp": 0, "fn": len(ground_truth)}

    matched_gt = set()
    tp = 0
    fp = 0
    ious = []

    for pred in predictions:
        pred_box = pred.bbox if hasattr(pred, "bbox") else pred["bbox"]
        pred_cat = pred.category.value if hasattr(pred.category, "value") else str(pred.get("category", ""))

        best_iou = 0.0
        best_gt_idx = -1

        for idx, gt in enumerate(ground_truth):
            if idx in matched_gt:
                continue
            gt_box = tuple(gt["bbox"])
            gt_cat = str(gt["category"])

            iou = compute_iou(pred_box, gt_box)
            if iou > best_iou:
                best_iou = iou
                if (pred_cat.lower() == gt_cat.lower() or not pred_cat) and iou >= iou_thresh:
                    best_gt_idx = idx

        if best_gt_idx >= 0:
            matched_gt.add(best_gt_idx)
            tp += 1
            ious.append(best_iou)
        else:
            fp += 1

    fn = len(ground_truth) - len(matched_gt)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    mean_iou = float(np.mean(ious)) if ious else 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "mean_iou": round(mean_iou, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }
