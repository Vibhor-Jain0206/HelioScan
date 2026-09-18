"""
Unified HelioScan Pipeline orchestrating ingestion, preprocessing,
defect detection, mathematical severity quantification, IEC 62446-3 health analysis,
and structured JSON/CSV/HUD export.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any
import csv
import json
import time
import cv2

from .config import PipelineConfig
from .preprocessing import PreprocessingEngine
from .detector import SolarDefectDetector
from .severity import SeverityEngine
from .analyzer import IECHealthAnalyzer, ModuleHealthReport
from .visualization import Visualizer


@dataclass
class InspectionResult:
    image_name: str
    image_path: str
    execution_time_ms: float
    report: ModuleHealthReport
    hud_path: Optional[str] = None
    json_path: Optional[str] = None
    csv_path: Optional[str] = None


class HelioPipeline:
    """Top-level pipeline interface for single-image and batch processing."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.preprocessor = PreprocessingEngine(self.config.preprocessing)
        self.detector = SolarDefectDetector(self.config.detector)
        self.severity_engine = SeverityEngine(self.config.severity)
        self.analyzer = IECHealthAnalyzer(self.config.iec)
        self.visualizer = Visualizer()

        self.out_dir = Path(self.config.output_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, image_path: str) -> InspectionResult:
        start_t = time.perf_counter()
        img_path = Path(image_path)

        raw_bgr = self.preprocessor.load_and_validate(str(img_path))
        preprocessed_bgr, _ = self.preprocessor.process(raw_bgr)
        detections = self.detector.detect(preprocessed_bgr)
        severities = self.severity_engine.evaluate_all(detections, preprocessed_bgr.shape)
        health_report = self.analyzer.analyze(severities)

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        hud_file = None
        json_file = None
        csv_file = None
        stem = img_path.stem

        if self.config.export_hud:
            hud_img = self.visualizer.draw_hud(raw_bgr, health_report)
            hud_file = str(self.out_dir / f"{stem}_hud.jpg")
            cv2.imwrite(hud_file, hud_img)

        if self.config.export_json:
            json_file = str(self.out_dir / f"{stem}_telemetry.json")
            data_dict = self._serialize_report(stem, str(img_path), elapsed_ms, health_report)
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data_dict, f, indent=2)

        if self.config.export_csv:
            csv_file = str(self.out_dir / f"{stem}_defects.csv")
            self._write_csv(csv_file, stem, health_report)

        return InspectionResult(
            image_name=img_path.name,
            image_path=str(img_path),
            execution_time_ms=round(elapsed_ms, 2),
            report=health_report,
            hud_path=hud_file,
            json_path=json_file,
            csv_path=csv_file
        )

    def process_batch(self, directory_path: str) -> List[InspectionResult]:
        dir_p = Path(directory_path)
        if not dir_p.exists() or not dir_p.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory_path}")

        image_files = sorted(
            list(dir_p.glob("*.jpg")) +
            list(dir_p.glob("*.jpeg")) +
            list(dir_p.glob("*.png"))
        )

        results = []
        for img_p in image_files:
            res = self.process_image(str(img_p))
            results.append(res)

        return results

    def _serialize_report(self, stem: str, img_path: str, elapsed_ms: float, report: ModuleHealthReport) -> Dict[str, Any]:
        defects_list = []
        for s in report.severities:
            defects_list.append({
                "category": s.defect.category.value,
                "confidence": round(s.defect.confidence, 3),
                "bbox_xywh": list(s.defect.bbox),
                "area_pixels": s.defect.area_pixels,
                "area_fraction": s.area_fraction,
                "temp_delta_celsius": s.temp_differential,
                "busbar_proximity": s.busbar_proximity_factor,
                "severity_score": s.final_score,
                "severity_tier": s.tier.value
            })

        return {
            "metadata": {
                "system": "HelioScan PV Inspection Engine",
                "standards_compliance": "IEC 62446-3",
                "inspector": "Vibhor Jain (24BAI10742)",
                "image_stem": stem,
                "image_path": img_path,
                "inference_time_ms": elapsed_ms
            },
            "summary": {
                "module_degradation_index": report.module_degradation_index,
                "health_tier": report.health_tier.value,
                "total_defects": report.total_defects,
                "critical_defects_count": report.critical_defects_count,
                "estimated_power_loss_percent": report.estimated_power_loss_pct,
                "recommended_action": report.recommended_action
            },
            "defects": defects_list
        }

    def _write_csv(self, csv_file: str, stem: str, report: ModuleHealthReport):
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "image_stem", "defect_id", "category", "confidence",
                "bbox_x", "bbox_y", "bbox_w", "bbox_h", "area_px",
                "temp_delta_c", "severity_score", "severity_tier"
            ])
            for idx, s in enumerate(report.severities):
                x, y, w, h = s.defect.bbox
                writer.writerow([
                    stem, idx + 1, s.defect.category.value, round(s.defect.confidence, 3),
                    x, y, w, h, s.defect.area_pixels, s.temp_differential,
                    s.final_score, s.tier.value
                ])
