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


def test_pipeline_missing_image():
    cfg = PipelineConfig(output_dir="outputs")
    pipeline = HelioPipeline(cfg)
    import pytest
    with pytest.raises(Exception):
        pipeline.process_image("non_existent_image_file.jpg")


def test_pipeline_custom_output_dir(tmp_path):
    custom_dir = tmp_path / "custom_outputs"
    cfg = PipelineConfig(
        output_dir=str(custom_dir),
        export_hud=True,
        export_json=True,
        export_csv=True
    )
    pipeline = HelioPipeline(cfg)
    result = pipeline.process_image("data/sample/clean_module_01.jpg")
    assert result.report.total_defects == 0
    assert Path(result.json_path).exists()
    assert str(custom_dir) in result.json_path

