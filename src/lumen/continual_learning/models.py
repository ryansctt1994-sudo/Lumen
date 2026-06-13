"""Data models for Lumen's continual learning layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ExperienceRecord:
    task_id: str
    task_type: str
    outcome: str
    receipt_hash: str
    replay_valid: bool
    artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillCandidate:
    name: str
    source_task_ids: List[str]
    source_receipts: List[str]
    pattern: str
    evidence_level: str = "E1"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TransferReport:
    skill_name: str
    baseline_score: float
    skill_score: float
    transfer_gain: float
    degradation: float
    replay_valid: bool


@dataclass(frozen=True)
class MemoryUtilityReport:
    memory_id: str
    with_memory_score: float
    without_memory_score: float
    memory_utility: float


@dataclass(frozen=True)
class PromotionDecision:
    skill_name: str
    promote: bool
    reason: str
    authority: str = "EVIDENCE_ONLY"


@dataclass(frozen=True)
class ForgettingReport:
    skill_name: str
    status: str
    reason: str
    conflict_count: int = 0
    days_unused: Optional[int] = None
