"""
HelioScan: Drone-Based Photovoltaic Defect Detection & IEC 62446-3 Severity Mapping
Core Library Package
"""

__version__ = "1.0.0"
__author__ = "Vibhor Jain (24BAI10742)"

from .config import PipelineConfig, DefectClass, HealthTier
from .preprocessing import PreprocessingEngine
from .detector import SolarDefectDetector, DefectDetection
from .severity import SeverityEngine, DefectSeverity
from .analyzer import IECHealthAnalyzer, ModuleHealthReport
from .metrics import compute_iou, evaluate_detections
from .visualization import Visualizer
from .pipeline import HelioPipeline, InspectionResult

__all__ = [
    "PipelineConfig",
    "DefectClass",
    "HealthTier",
    "PreprocessingEngine",
    "SolarDefectDetector",
    "DefectDetection",
    "SeverityEngine",
    "DefectSeverity",
    "IECHealthAnalyzer",
    "ModuleHealthReport",
    "compute_iou",
    "evaluate_detections",
    "Visualizer",
    "HelioPipeline",
    "InspectionResult",
]
