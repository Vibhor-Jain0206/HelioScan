"""
Integration tests for the complete end-to-end HelioScan pipeline.
"""

from pathlib import Path
from src.pipeline import HelioPipeline
from src.config import PipelineConfig


def test_single_image_pipeline():
    cfg = PipelineConfig(
        output_dir="outputs",
        export_hud=True,
        export_json=True,
        export_csv=True
    )
    pipeline = HelioPipeline(cfg)
    test_img = "data/sample/hotspot_01.jpg"

    result = pipeline.process_image(test_img)
    assert result.image_name == "hotspot_01.jpg"
    assert result.execution_time_ms > 0
    assert result.report is not None
    assert result.hud_path is not None
    assert Path(result.hud_path).exists()
    assert result.json_path is not None
    assert Path(result.json_path).exists()
    assert result.csv_path is not None
    assert Path(result.csv_path).exists()


def test_batch_pipeline():
    cfg = PipelineConfig(output_dir="outputs", export_hud=False)
    pipeline = HelioPipeline(cfg)

    results = pipeline.process_batch("data/sample")
    assert len(results) >= 5
    for r in results:
        assert r.report.module_degradation_index >= 0.0
        assert r.execution_time_ms > 0
