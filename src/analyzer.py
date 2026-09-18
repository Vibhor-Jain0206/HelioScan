"""
IEC 62446-3 Module Degradation Index (MDI) calculator, health tiering,
power loss estimation, and automated maintenance dispatch recommendations.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from .config import IEC62446Config, HealthTier
from .severity import DefectSeverity, SeverityTier


@dataclass
class ModuleHealthReport:
    module_degradation_index: float
    health_tier: HealthTier
    total_defects: int
    critical_defects_count: int
    estimated_power_loss_pct: float
    recommended_action: str
    severities: List[DefectSeverity]


class IECHealthAnalyzer:
    """
    Evaluates global panel degradation adhering to the international IEC 62446-3
    photovoltaic thermographic inspection standard.
    """

    def __init__(self, config: Optional[IEC62446Config] = None):
        self.config = config or IEC62446Config()

    def analyze(self, severities: List[DefectSeverity]) -> ModuleHealthReport:
        if not severities:
            return ModuleHealthReport(
                module_degradation_index=100.0,
                health_tier=HealthTier.OPTIMAL,
                total_defects=0,
                critical_defects_count=0,
                estimated_power_loss_pct=0.0,
                recommended_action="Normal routine monitoring; panel is operating within pristine limits.",
                severities=[]
            )

        n = len(severities)
        scores = [s.final_score for s in severities]
        critical_count = sum(1 for s in severities if s.tier == SeverityTier.CRITICAL)

        interaction_multiplier = 1.0 + 0.12 * max(0, n - 1)
        mean_severity = float(np.mean(scores))
        max_severity = float(np.max(scores))

        degradation_penalty = (0.60 * max_severity + 0.40 * mean_severity) * interaction_multiplier
        mdi = float(np.clip(100.0 - degradation_penalty, 0.0, 100.0))
        power_loss = float(np.clip((100.0 - mdi) * self.config.power_loss_coefficient, 0.0, 100.0))

        if mdi >= self.config.tier_optimal_threshold and critical_count == 0:
            tier = HealthTier.OPTIMAL
            action = "Tier 1: Nominal performance. Continue routine scheduled aerial drone monitoring."
        elif mdi >= self.config.tier_degraded_threshold and critical_count == 0:
            tier = HealthTier.DEGRADED
            action = "Tier 2: Degradation detected. Schedule surface washing and visual inspection within 30 days."
        elif mdi >= self.config.tier_compromised_threshold:
            tier = HealthTier.COMPROMISED
            action = "Tier 3: Electrical string compromised. Dispatch field technician to test bypass diodes."
        else:
            tier = HealthTier.CRITICAL
            action = "Tier 4: CRITICAL ANOMALY. Immediate string isolation and module replacement required (Fire Risk)."

        return ModuleHealthReport(
            module_degradation_index=round(mdi, 1),
            health_tier=tier,
            total_defects=n,
            critical_defects_count=critical_count,
            estimated_power_loss_pct=round(power_loss, 1),
            recommended_action=action,
            severities=severities
        )
