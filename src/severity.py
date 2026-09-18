"""
Deterministic mathematical severity quantification combining defect area fraction,
calibrated temperature differential (ΔT), busbar proximity, and hazard weighting.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import numpy as np

from .config import SeverityConfig, DefectClass, DEFECT_REGISTRY
from .detector import DefectDetection


class SeverityTier(str, Enum):
    NEGLIGIBLE = "Negligible"
    MODERATE = "Moderate"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class DefectSeverity:
    defect: DefectDetection
    area_fraction: float
    temp_differential: float
    busbar_proximity_factor: float
    raw_severity: float
    final_score: float
    tier: SeverityTier


class SeverityEngine:
    """
    Computes objective mathematical severity indices (0 to 100)
    for detected solar defects according to physical defect models.
    """

    def __init__(self, config: Optional[SeverityConfig] = None):
        self.config = config or SeverityConfig()

    def evaluate(self, defect: DefectDetection, frame_dimensions: tuple) -> DefectSeverity:
        h_frame, w_frame = frame_dimensions[:2]
        cell_area = self.config.nominal_cell_area_px

        area_fraction = min(1.0, float(defect.area_pixels) / cell_area)

        prop = DEFECT_REGISTRY[defect.category]
        max_dt = prop.max_delta_temp
        norm_dt = min(1.0, max(0.0, defect.estimated_temp_delta / max_dt))

        cx, cy = defect.center
        norm_x = (cx % (w_frame / 3.0)) / (w_frame / 3.0)
        dist_to_busbar = abs(norm_x - 0.5) * 2.0
        p_busbar = float(np.clip(1.0 - dist_to_busbar, 0.2, 1.0) * 100.0)

        alpha = self.config.alpha_area
        beta = self.config.beta_temp
        gamma = self.config.gamma_busbar
        w_c = prop.hazard_weight

        component_score = (
            alpha * (area_fraction * 100.0) +
            beta * (norm_dt * 100.0) +
            gamma * p_busbar
        )

        final_score = float(np.clip(w_c * component_score, 0.0, 100.0))

        if final_score < 25.0:
            tier = SeverityTier.NEGLIGIBLE
        elif final_score < 50.0:
            tier = SeverityTier.MODERATE
        elif final_score < 75.0:
            tier = SeverityTier.HIGH
        else:
            tier = SeverityTier.CRITICAL

        return DefectSeverity(
            defect=defect,
            area_fraction=round(area_fraction, 4),
            temp_differential=round(defect.estimated_temp_delta, 1),
            busbar_proximity_factor=round(p_busbar, 2),
            raw_severity=round(component_score, 2),
            final_score=round(final_score, 2),
            tier=tier
        )

    def evaluate_all(self, defects: List[DefectDetection], frame_dim: tuple) -> List[DefectSeverity]:
        return [self.evaluate(d, frame_dim) for d in defects]
