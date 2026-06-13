"""Forgetting and clutter detection."""

from __future__ import annotations

from .models import ForgettingReport


class ForgettingDetector:
    """Detect stale, conflicting, or negatively transferring skills."""

    def __init__(self, *, max_days_unused: int = 180, max_conflicts: int = 3):
        self.max_days_unused = max_days_unused
        self.max_conflicts = max_conflicts

    def evaluate(
        self,
        *,
        skill_name: str,
        transfer_gain: float,
        conflict_count: int = 0,
        days_unused: int | None = None,
    ) -> ForgettingReport:
        if transfer_gain < 0:
            return ForgettingReport(skill_name, "DEPRECATED", "negative transfer", conflict_count, days_unused)
        if conflict_count > self.max_conflicts:
            return ForgettingReport(skill_name, "REVIEW", "conflict threshold exceeded", conflict_count, days_unused)
        if days_unused is not None and days_unused > self.max_days_unused:
            return ForgettingReport(skill_name, "STALE", "unused beyond retention window", conflict_count, days_unused)
        return ForgettingReport(skill_name, "ACTIVE", "no forgetting risk detected", conflict_count, days_unused)
