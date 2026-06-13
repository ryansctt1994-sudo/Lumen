"""Minimal Weaver-style authority verifier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from lumen.receipt import Receipt


@dataclass(frozen=True)
class VerificationResult:
    authorized: bool
    reason: str
    authority_level: str
    receipt_hash: Optional[str] = None


class WeaverVerifier:
    """Minimal authority gate.

    The verifier upgrades no claim beyond evidence. It only recognizes local
    evidence status unless independent replay or stronger artifacts are present.
    """

    def __init__(self, policy_version: str = "v0.1"):
        self.policy_version = policy_version

    def verify(self, claim: Dict[str, Any], receipt: Receipt, replay_report: Dict[str, Any]) -> VerificationResult:
        if not claim:
            return self.fails_closed("missing claim")
        if receipt.policy_version != self.policy_version:
            return self.fails_closed("policy version mismatch")
        if not replay_report.get("valid"):
            return self.fails_closed("replay failed")
        if receipt.replay_result != "PASS":
            return VerificationResult(False, "receipt replay result is not PASS", "EVIDENCE_ONLY", receipt.receipt_hash)
        if receipt.event_hash != replay_report.get("last_hash") and replay_report.get("last_hash") is not None:
            return VerificationResult(False, "receipt event hash does not match replay tip", "EVIDENCE_ONLY", receipt.receipt_hash)

        return VerificationResult(True, "checks passed", "EVIDENCE_ONLY", receipt.receipt_hash)

    def fails_closed(self, reason: str) -> VerificationResult:
        return VerificationResult(False, f"fail-closed: {reason}", "NONE", None)
