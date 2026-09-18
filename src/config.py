"""
Configuration models, enumerations, and default constants for HelioScan.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple, List


class DefectClass(str, Enum):
    HOTSPOT = "Hotspot"
    MICROCRACK = "Microcrack"
    PID = "PID"
    SOILING = "Soiling"
    DIODE_FAILURE = "Diode_Failure"


class HealthTier(str, Enum):
    OPTIMAL = "Tier 1: Optimal"
    DEGRADED = "Tier 2: Degraded"
    COMPROMISED = "Tier 3: Compromised"
    CRITICAL = "Tier 4: Critical Failure"


@dataclass
class DefectProperty:
    hazard_weight: float
    bgr_color: Tuple[int, int, int]
    description: str
    max_delta_temp: float


DEFECT_REGISTRY: Dict[DefectClass, DefectProperty] = {
    DefectClass.HOTSPOT: DefectProperty(
        hazard_weight=1.30,
        bgr_color=(0, 0, 255),      # Red
        description="Localized thermal shunt dissipation",
        max_delta_temp=35.0,
    ),
    DefectClass.MICROCRACK: DefectProperty(
        hazard_weight=1.15,
        bgr_color=(255, 0, 255),    # Magenta
        description="Wafer fracture cutting electrical fingers",
        max_delta_temp=12.0,
    ),
    DefectClass.PID: DefectProperty(
        hazard_weight=1.40,
        bgr_color=(0, 165, 255),    # Orange
        description="High-voltage potential induced degradation",
        max_delta_temp=20.0,
    ),
    DefectClass.SOILING: DefectProperty(
        hazard_weight=0.85,
        bgr_color=(0, 255, 255),    # Yellow
        description="Surface dust/avian occlusion",
        max_delta_temp=8.0,
    ),
    DefectClass.DIODE_FAILURE: DefectProperty(
        hazard_weight=1.50,
        bgr_color=(50, 50, 255),    # Dark Red / Crimson
        description="Bypass diode open/short sub-string failure",
        max_delta_temp=45.0,
    ),
}


@dataclass
class PreprocessingConfig:
    clahe_clip_limit: float = 2.5
    clahe_tile_grid: Tuple[int, int] = (8, 8)
    bilateral_d: int = 9
    bilateral_sigma_color: float = 75.0
    bilateral_sigma_space: float = 75.0
    rectify_module: bool = True


@dataclass
class DetectorConfig:
    confidence_threshold: float = 0.30
    nms_iou_threshold: float = 0.40
    min_defect_area_px: int = 35
    max_defect_area_ratio: float = 0.65
    hotspot_intensity_thresh: int = 195
    crack_gradient_thresh: int = 42
    soiling_variance_thresh: float = 120.0


@dataclass
class SeverityConfig:
    alpha_area: float = 0.35
    beta_temp: float = 0.45
    gamma_busbar: float = 0.20
    nominal_cell_area_px: int = 15000


@dataclass
class IEC62446Config:
    tier_optimal_threshold: float = 85.0
    tier_degraded_threshold: float = 70.0
    tier_compromised_threshold: float = 50.0
    power_loss_coefficient: float = 0.68


@dataclass
class PipelineConfig:
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    severity: SeverityConfig = field(default_factory=SeverityConfig)
    iec: IEC62446Config = field(default_factory=IEC62446Config)
    output_dir: str = "outputs"
    export_json: bool = True
    export_csv: bool = True
    export_hud: bool = True
