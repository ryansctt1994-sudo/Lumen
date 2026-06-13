"""Skill extraction from replayed experiences."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List

from .models import ExperienceRecord, SkillCandidate


class SkillExtractor:
    """Extracts conservative skill candidates from successful, replay-valid experiences."""

    def extract(self, experiences: Iterable[ExperienceRecord], *, min_support: int = 2) -> List[SkillCandidate]:
        valid = [e for e in experiences if e.replay_valid and e.outcome == "success"]
        counts = Counter(e.task_type for e in valid)
        candidates: List[SkillCandidate] = []

        for task_type, count in counts.items():
            if count < min_support:
                continue
            sources = [e for e in valid if e.task_type == task_type]
            candidates.append(
                SkillCandidate(
                    name=f"skill_{task_type}",
                    source_task_ids=[e.task_id for e in sources],
                    source_receipts=[e.receipt_hash for e in sources],
                    pattern=f"Repeated successful replay-valid pattern for task_type={task_type}",
                    evidence_level="E1",
                    metadata={"support": count},
                )
            )

        return candidates
