"""Skill manifest schema.

Skill manifests describe capability candidates. A manifest is not runtime
authority. Promotion requires tests, evaluation, receipt, and review.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SkillIO:
    name: str
    schema: Dict[str, Any]
    description: str = ""


@dataclass(frozen=True)
class SkillEvaluation:
    command: str
    success_criteria: str
    required: bool = True


@dataclass(frozen=True)
class SkillManifest:
    name: str
    version: str
    description: str
    inputs: List[SkillIO]
    outputs: List[SkillIO]
    required_providers: List[str] = field(default_factory=list)
    evaluations: List[SkillEvaluation] = field(default_factory=list)
    evidence_level: str = "E0"
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))

    def manifest_hash(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def validate_for_candidate(self) -> None:
        if not self.name.strip():
            raise ValueError("skill name is required")
        if not self.version.strip():
            raise ValueError("skill version is required")
        if self.evidence_level not in {"E0", "E1", "E2", "E3", "E4", "E5"}:
            raise ValueError(f"invalid evidence_level: {self.evidence_level}")
