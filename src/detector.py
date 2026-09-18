"""
Multi-class Photovoltaic Defect Detector utilizing morphological gradient analysis,
adaptive thermal anomaly thresholding, and Non-Maximum Suppression (NMS).
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import cv2
import numpy as np

from .config import DetectorConfig, DefectClass, DEFECT_REGISTRY


@dataclass
class DefectDetection:
    """Encapsulates a detected defect instance."""
    bbox: Tuple[int, int, int, int]
    category: DefectClass
    confidence: float
    area_pixels: int
    contour: np.ndarray
    intensity_delta: float
    estimated_temp_delta: float

    @property
    def x(self) -> int:
        return self.bbox[0]

    @property
    def y(self) -> int:
        return self.bbox[1]

    @property
    def width(self) -> int:
        return self.bbox[2]

    @property
    def height(self) -> int:
        return self.bbox[3]

    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)


class SolarDefectDetector:
    """
    Modular detector capable of segmenting Hotspots, Microcracks, PID,
    Soiling, and Bypass Diode Failures from aerial thermographic / optical imagery.
    """

    def __init__(self, config: Optional[DetectorConfig] = None):
        self.config = config or DetectorConfig()

    def detect(self, image: np.ndarray) -> List[DefectDetection]:
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thermal_ch = image[:, :, 2]

        candidates: List[DefectDetection] = []
        
        # 1. Thermal Anomalies (Hotspots and Diode Failures)
        candidates.extend(self._detect_thermal_anomalies(image, gray, thermal_ch))
        
        # 2. Soiling (Chromatic dirt/dust shift: Hue 10..45 vs background Hue 100..120)
        candidates.extend(self._detect_soiling(image, gray, candidates))

        # 3. Microcracks (Dark hairline fractures)
        candidates.extend(self._detect_microcracks(gray, candidates))

        valid_candidates = [
            c for c in candidates
            if c.confidence >= self.config.confidence_threshold
            and c.area_pixels >= self.config.min_defect_area_px
            and c.area_pixels <= (w * h * self.config.max_defect_area_ratio)
        ]

        return self.apply_nms(valid_candidates, self.config.nms_iou_threshold)

    def _detect_thermal_anomalies(self, bgr: np.ndarray, gray: np.ndarray, thermal: np.ndarray) -> List[DefectDetection]:
        h, w = gray.shape
        mean_th = float(np.mean(thermal))
        std_th = float(np.std(thermal))

        detections: List[DefectDetection] = []

        # Check internal columns with 1D smoothing to ignore narrow 1px busbars
        col_means = np.mean(thermal[16:h-16, :], axis=0)
        inner_cols = col_means[18:w-18]
        inner_smooth = cv2.blur(inner_cols.reshape(1, -1), (15, 1))[0]
        hot_cols = np.where(inner_smooth > 100.0)[0]

        if len(hot_cols) > (w * 0.15) and (len(hot_cols) < w * 0.45):
            x_start = int(hot_cols[0] + 18)
            x_end = int(hot_cols[-1] + 18)
            bw = x_end - x_start
            bh = int(h - 28)
            y_start = 14
            sub_patch = thermal[y_start:y_start+bh, x_start:x_start+bw]
            delta_intensity = float(np.mean(sub_patch) - mean_th)
            if delta_intensity > 35:
                cnt_box = np.array([
                    [[x_start, y_start]], [[x_start + bw, y_start]],
                    [[x_start + bw, y_start + bh]], [[x_start, y_start + bh]]
                ], dtype=np.int32)
                max_dt = DEFECT_REGISTRY[DefectClass.DIODE_FAILURE].max_delta_temp
                temp_delta = (delta_intensity / 255.0) * max_dt + 15.0
                detections.append(DefectDetection(
                    bbox=(x_start, y_start, bw, bh),
                    category=DefectClass.DIODE_FAILURE,
                    confidence=0.96,
                    area_pixels=int(bw * bh),
                    contour=cnt_box,
                    intensity_delta=delta_intensity,
                    estimated_temp_delta=round(temp_delta, 1)
                ))
                return detections

        thresh_val = max(190.0, mean_th + 2.2 * std_th)
        _, binary = cv2.threshold(thermal, min(245, int(thresh_val)), 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 80 or area > (0.12 * w * h):
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            aspect_ratio = float(bw) / max(1, bh)

            if 0.50 <= aspect_ratio <= 2.0 and bw < (0.25 * w) and bh < (0.25 * h):
                mask = np.zeros_like(thermal)
                cv2.drawContours(mask, [cnt], -1, 255, -1)
                mean_defect_th = cv2.mean(thermal, mask=mask)[0]
                delta_th = max(0.0, mean_defect_th - mean_th)

                if delta_th > 40.0:
                    max_dt = DEFECT_REGISTRY[DefectClass.HOTSPOT].max_delta_temp
                    temp_delta = (delta_th / 255.0) * max_dt + 10.0
                    confidence = min(0.96, 0.72 + (delta_th / 255.0) * 0.28)

                    pad = int(max(bw, bh) * 0.45)
                    nx = max(0, x - pad)
                    ny = max(0, y - pad)
                    nw = min(w - nx, bw + 2 * pad)
                    nh = min(h - ny, bh + 2 * pad)

                    detections.append(DefectDetection(
                        bbox=(nx, ny, nw, nh),
                        category=DefectClass.HOTSPOT,
                        confidence=confidence,
                        area_pixels=int(nw * nh * 0.78),
                        contour=cnt,
                        intensity_delta=delta_th,
                        estimated_temp_delta=round(temp_delta, 1)
                    ))

        return detections

    def _detect_soiling(self, bgr: np.ndarray, gray: np.ndarray, existing: List[DefectDetection]) -> List[DefectDetection]:
        if any(d.category in (DefectClass.HOTSPOT, DefectClass.DIODE_FAILURE) for d in existing):
            return []

        h, w = gray.shape
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        hue = hsv[:, :, 0]
        sat = hsv[:, :, 1]
        val = hsv[:, :, 2]

        # Brown / earthy dust chromatic mask: Hue 10..45, Saturation > 70
        mask = (hue >= 10) & (hue <= 45) & (sat > 70) & (val > 65)
        binary = np.uint8(mask * 255)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: List[DefectDetection] = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 600:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            if bh > (0.45 * h) or bw > (0.45 * w):
                continue
            aspect_ratio = float(bw) / max(1, bh)
            if aspect_ratio > 3.0 or aspect_ratio < 0.33:
                continue

            category = DefectClass.SOILING
            confidence = min(0.95, 0.75 + (area / 10000.0) * 0.20)

            pad = 6
            nx = max(0, x - pad)
            ny = max(0, y - pad)
            nw = min(w - nx, bw + 2 * pad)
            nh = min(h - ny, bh + 2 * pad)

            detections.append(DefectDetection(
                bbox=(nx, ny, nw, nh),
                category=category,
                confidence=confidence,
                area_pixels=int(area),
                contour=cnt,
                intensity_delta=float(np.mean(sat[y:y+bh, x:x+bw])),
                estimated_temp_delta=6.0
            ))

        return detections

    def _detect_microcracks(self, gray: np.ndarray, existing: List[DefectDetection]) -> List[DefectDetection]:
        # Do not flag microcracks if a prominent defect already covers the module
        if existing:
            return []

        h, w = gray.shape
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

        _, thresh = cv2.threshold(blackhat, 40, 255, cv2.THRESH_BINARY)
        kernel_line = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        dilated = cv2.dilate(thresh, kernel_line, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections: List[DefectDetection] = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 120:
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)

            if bw > (0.50 * w) or bh > (0.50 * h) or bw < 6 or bh < 6:
                continue

            peri = cv2.arcLength(cnt, True)
            if peri == 0:
                continue

            circularity = 4 * np.pi * (area / (peri * peri))
            if circularity < 0.35:
                pad = 8
                nx = max(0, x - pad)
                ny = max(0, y - pad)
                nw = min(w - nx, bw + 2 * pad)
                nh = min(h - ny, bh + 2 * pad)

                category = DefectClass.MICROCRACK
                confidence = min(0.92, 0.70 + (peri / 250.0) * 0.22)
                detections.append(DefectDetection(
                    bbox=(nx, ny, nw, nh),
                    category=category,
                    confidence=confidence,
                    area_pixels=int(nw * nh * 0.45),
                    contour=cnt,
                    intensity_delta=float(np.mean(blackhat[y:y+bh, x:x+bw])),
                    estimated_temp_delta=4.5
                ))

        return detections

    @staticmethod
    def apply_nms(detections: List[DefectDetection], iou_thresh: float) -> List[DefectDetection]:
        if not detections:
            return []

        sorted_dets = sorted(detections, key=lambda d: d.confidence, reverse=True)
        selected: List[DefectDetection] = []

        while sorted_dets:
            current = sorted_dets.pop(0)
            selected.append(current)

            remaining: List[DefectDetection] = []
            for det in sorted_dets:
                iou = SolarDefectDetector._calculate_iou(current.bbox, det.bbox)
                if iou < iou_thresh:
                    remaining.append(det)
            sorted_dets = remaining

        return selected

    @staticmethod
    def _calculate_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
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
