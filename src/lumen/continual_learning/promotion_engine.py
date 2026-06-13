"""Skill promotion policy."""

from __future__ import annotations

from .models import MemoryUtilityReport, PromotionDecision, TransferReport


class PromotionEngine:
    """Promotes only skills with measurable transfer benefit and low degradation."""

    def __init__(self, *, min_transfer_gain: float = 0.10, max_degradation: float = 0.03, min_memory_utility: float = 0.0):
        self.min_transfer_gain = min_transfer_gain
        self.max_degradation = max_degradation
        self.min_memory_utility = min_memory_utility

    def decide(self, transfer: TransferReport, memory: MemoryUtilityReport | None = None) -> PromotionDecision:
        if not transfer.replay_valid:
            return PromotionDecision(transfer.skill_name, False, "replay invalid")
        if transfer.transfer_gain < self.min_transfer_gain:
            return PromotionDecision(transfer.skill_name, False, "transfer gain below threshold")
        if transfer.degradation > self.max_degradation:
            return PromotionDecision(transfer.skill_name, False, "degradation above threshold")
        if memory is not None and memory.memory_utility < self.min_memory_utility:
            return PromotionDecision(transfer.skill_name, False, "memory utility below threshold")
        return PromotionDecision(transfer.skill_name, True, "promotion criteria satisfied")
