"""Simulated fail-closed hardware veto latch."""

from __future__ import annotations

from enum import Enum
from typing import Optional


class LatchState(str, Enum):
    ARMED = "ARMED"
    TRIGGERED = "TRIGGERED"
    DISABLED = "DISABLED"


class HardwareVeto:
    """Binary latch for externalized safety enforcement.

    Risk assessment may be probabilistic upstream. The boundary is binary:
    at or above threshold, the latch triggers and remains triggered until reset.
    """

    def __init__(self, threshold: float = 0.75):
        if not 0.0 < threshold <= 1.0:
            raise ValueError(f"threshold must be in (0.0, 1.0], got {threshold}")
        self.threshold = threshold
        self.state = LatchState.ARMED
        self._trigger_reason: Optional[str] = None

    def evaluate(self, risk_score: float, reason: str = "") -> LatchState:
        if not 0.0 <= risk_score <= 1.0:
            raise ValueError(f"risk_score must be in [0.0, 1.0], got {risk_score}")
        if self.state != LatchState.ARMED:
            return self.state
        if risk_score >= self.threshold:
            self.state = LatchState.TRIGGERED
            self._trigger_reason = reason or f"risk_score={risk_score:.4f} >= threshold={self.threshold:.4f}"
        return self.state

    def disable(self) -> LatchState:
        self.state = LatchState.DISABLED
        return self.state

    def reset(self) -> LatchState:
        self.state = LatchState.ARMED
        self._trigger_reason = None
        return self.state

    @property
    def trigger_reason(self) -> Optional[str]:
        return self._trigger_reason

    @property
    def is_halted(self) -> bool:
        return self.state == LatchState.TRIGGERED
