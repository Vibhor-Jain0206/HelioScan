"""
Headless OpenCV HUD visualizer generating corner-bracket bounding boxes,
thermal false-color enhancements, severity badges, and telemetry dashboards.
"""

from typing import List, Tuple
import cv2
import numpy as np
import datetime

from .config import DEFECT_REGISTRY, HealthTier
from .severity import DefectSeverity, SeverityTier
from .analyzer import ModuleHealthReport


class Visualizer:
    """Renders diagnostic inspection overlays completely headlessly without X11/GUI."""

    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_hud(self, image: np.ndarray, report: ModuleHealthReport) -> np.ndarray:
        canvas = image.copy()
        h, w = canvas.shape[:2]

        for item in report.severities:
            self._draw_defect_box(canvas, item)

        self._draw_telemetry_banner(canvas, report)
        return canvas

    def _draw_defect_box(self, canvas: np.ndarray, item: DefectSeverity):
        x, y, bw, bh = item.defect.bbox
        cat = item.defect.category
        prop = DEFECT_REGISTRY[cat]
        color = prop.bgr_color

        blen = max(6, min(18, min(bw, bh) // 4))
        thick = 2

        cv2.line(canvas, (x, y), (x + blen, y), color, thick)
        cv2.line(canvas, (x, y), (x, y + blen), color, thick)
        cv2.line(canvas, (x + bw, y), (x + bw - blen, y), color, thick)
        cv2.line(canvas, (x + bw, y), (x + bw, y + blen), color, thick)
        cv2.line(canvas, (x, y + bh), (x + blen, y + bh), color, thick)
        cv2.line(canvas, (x, y + bh), (x, y + bh - blen), color, thick)
        cv2.line(canvas, (x + bw, y + bh), (x + bw - blen, y + bh), color, thick)
        cv2.line(canvas, (x + bw, y + bh), (x + bw, y + bh - blen), color, thick)

        overlay = canvas.copy()
        cv2.rectangle(overlay, (x, y), (x + bw, y + bh), color, -1)
        cv2.addWeighted(overlay, 0.12, canvas, 0.88, 0, canvas)

        label = f"{cat.value} [{item.final_score:.0f}] +{item.temp_differential:.1f}C"
        (lw, lh), _ = cv2.getTextSize(label, self.font, 0.42, 1)

        badge_y = max(lh + 4, y - 6)
        cv2.rectangle(canvas, (x, badge_y - lh - 4), (x + lw + 6, badge_y + 2), (18, 18, 18), -1)
        cv2.rectangle(canvas, (x, badge_y - lh - 4), (x + lw + 6, badge_y + 2), color, 1)
        cv2.putText(canvas, label, (x + 3, badge_y - 2), self.font, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

    def _draw_telemetry_banner(self, canvas: np.ndarray, report: ModuleHealthReport):
        w = canvas.shape[1]
        banner_h = 56

        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, 0), (w, banner_h), (12, 14, 20), -1)
        cv2.addWeighted(overlay, 0.85, canvas, 0.15, 0, canvas)
        cv2.line(canvas, (0, banner_h), (w, banner_h), (60, 65, 80), 1)

        cv2.putText(canvas, "HELIOSCAN // IEC 62446-3 TELEMETRY", (14, 22),
                    self.font, 0.50, (0, 210, 255), 1, cv2.LINE_AA)

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        cv2.putText(canvas, f"INSPECTION: {now_str} | RESOLUTION: {w}x{canvas.shape[0]}",
                    (14, 44), self.font, 0.38, (170, 175, 190), 1, cv2.LINE_AA)

        mdi = report.module_degradation_index
        if report.health_tier == HealthTier.OPTIMAL:
            tier_color = (0, 220, 100)
        elif report.health_tier == HealthTier.DEGRADED:
            tier_color = (0, 220, 240)
        elif report.health_tier == HealthTier.COMPROMISED:
            tier_color = (0, 140, 255)
        else:
            tier_color = (40, 40, 255)

        mdi_text = f"MDI: {mdi:.1f}/100"
        (tw, th), _ = cv2.getTextSize(mdi_text, self.font, 0.62, 2)
        rx = w - tw - 24
        cv2.putText(canvas, mdi_text, (rx, 26), self.font, 0.62, tier_color, 2, cv2.LINE_AA)

        sub_text = f"DEFECTS: {report.total_defects} | EST. LOSS: {report.estimated_power_loss_pct:.1f}%"
        cv2.putText(canvas, sub_text, (w - 240, 45), self.font, 0.38, (210, 215, 225), 1, cv2.LINE_AA)
