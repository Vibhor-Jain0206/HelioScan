"""
Unit tests for deterministic severity quantification equations and severity tiers.
"""

import pytest
import numpy as np

from src.severity import SeverityEngine, SeverityTier
from src.detector import DefectDetection
from src.config import DefectClass


@pytest.fixture
def engine():
    return SeverityEngine()


def test_severity_bounds(engine):
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    det = DefectDetection(
        bbox=(200, 200, 80, 80),
        category=DefectClass.HOTSPOT,
        confidence=0.95,
        area_pixels=6400,
        contour=cnt,
        intensity_delta=60.0,
        estimated_temp_delta=32.0
    )

    sev = engine.evaluate(det, (512, 640))
    assert 0.0 <= sev.final_score <= 100.0
    assert 0.0 <= sev.area_fraction <= 1.0
    assert sev.temp_differential == 32.0
    assert sev.tier in [SeverityTier.NEGLIGIBLE, SeverityTier.MODERATE, SeverityTier.HIGH, SeverityTier.CRITICAL]


def test_severity_weight_ranking(engine):
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    # Diode failure has hazard_weight 1.50 vs Soiling 0.85
    det_diode = DefectDetection((100, 100, 50, 50), DefectClass.DIODE_FAILURE, 0.9, 2500, cnt, 40.0, 20.0)
    det_soiling = DefectDetection((100, 100, 50, 50), DefectClass.SOILING, 0.9, 2500, cnt, 40.0, 20.0)

    sev_diode = engine.evaluate(det_diode, (512, 640))
    sev_soiling = engine.evaluate(det_soiling, (512, 640))

    assert sev_diode.final_score > sev_soiling.final_score


def test_critical_tier_assignment(engine):
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    # Huge thermal anomaly with massive ΔT
    det_massive = DefectDetection((200, 14, 180, 480), DefectClass.DIODE_FAILURE, 0.98, 86400, cnt, 120.0, 42.0)
    sev = engine.evaluate(det_massive, (512, 640))
    assert sev.final_score >= 75.0
    assert sev.tier == SeverityTier.CRITICAL
