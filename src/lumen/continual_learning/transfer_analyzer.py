"""Transfer-gain analysis."""

from __future__ import annotations

from .models import TransferReport


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


class TransferAnalyzer:
    """Compares baseline performance with skill-assisted performance."""

    def analyze(self, *, skill_name: str, baseline_score: float, skill_score: float, replay_valid: bool) -> TransferReport:
        baseline = _clamp_score(baseline_score)
        skill = _clamp_score(skill_score)
        gain = skill - baseline
        degradation = max(0.0, baseline - skill)
        return TransferReport(
            skill_name=skill_name,
            baseline_score=baseline,
            skill_score=skill,
            transfer_gain=gain,
            degradation=degradation,
            replay_valid=replay_valid,
        )
