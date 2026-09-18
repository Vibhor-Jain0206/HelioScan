"""
Unit tests for IEC 62446-3 Module Degradation Index (MDI) and health triage logic.
"""

import pytest
import numpy as np

from src.analyzer import IECHealthAnalyzer
from src.severity import DefectSeverity, SeverityTier
from src.detector import DefectDetection
from src.config import DefectClass, HealthTier


@pytest.fixture
def analyzer():
    return IECHealthAnalyzer()


def test_clean_panel_mdi(analyzer):
    report = analyzer.analyze([])
    assert report.module_degradation_index == 100.0
    assert report.health_tier == HealthTier.OPTIMAL
    assert report.total_defects == 0
    assert report.critical_defects_count == 0
    assert report.estimated_power_loss_pct == 0.0


def test_degraded_panel_mdi(analyzer):
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    det = DefectDetection((100, 100, 40, 40), DefectClass.SOILING, 0.8, 1600, cnt, 20.0, 5.0)
    sev = DefectSeverity(det, 0.10, 5.0, 50.0, 20.0, 22.0, SeverityTier.NEGLIGIBLE)

    report = analyzer.analyze([sev])
    assert report.module_degradation_index < 100.0
    assert report.total_defects == 1
    assert report.health_tier == HealthTier.OPTIMAL or report.health_tier == HealthTier.DEGRADED


def test_critical_failure_panel_mdi(analyzer):
    cnt = np.zeros((4, 1, 2), dtype=np.int32)
    det = DefectDetection((200, 14, 190, 480), DefectClass.DIODE_FAILURE, 0.98, 91200, cnt, 100.0, 40.0)
    sev = DefectSeverity(det, 0.90, 40.0, 80.0, 85.0, 95.0, SeverityTier.CRITICAL)

    report = analyzer.analyze([sev])
    assert report.module_degradation_index < 50.0
    assert report.health_tier == HealthTier.CRITICAL
    assert report.critical_defects_count == 1
    assert "CRITICAL ANOMALY" in report.recommended_action
