"""Memory utility measurement.

MemProbe asks whether memory actually improves later task performance instead
of merely adding context clutter.
"""

from __future__ import annotations

from .models import MemoryUtilityReport


def _clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))


class MemProbe:
    """Compare task performance with and without a memory item."""

    def evaluate(self, *, memory_id: str, with_memory_score: float, without_memory_score: float) -> MemoryUtilityReport:
        with_mem = _clamp_score(with_memory_score)
        without_mem = _clamp_score(without_memory_score)
        return MemoryUtilityReport(
            memory_id=memory_id,
            with_memory_score=with_mem,
            without_memory_score=without_mem,
            memory_utility=with_mem - without_mem,
        )
