"""Experimental, evidence-limited continuity check over a Chronicle ledger.

The checkpoint must be held outside the ledger and supplied by a trusted caller.
This checks record continuity only: it cannot establish personal identity,
subjective experience, moral standing, or permission to act.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .chronicle import Chronicle


@dataclass(frozen=True)
class Checkpoint:
    subject_id: str
    entry_count: int
    tip_hash: str


@dataclass(frozen=True)
class ContinuityAssessment:
    supported: bool
    reason: str


def assess_record_continuity(
    ledger_path: str | Path,
    checkpoint: Checkpoint | None,
    claimed_subject_id: str,
    *,
    self_report: dict | None = None,
) -> ContinuityAssessment:
    """Check a witnessed prefix and subsequent chain, ignoring self-assertions.

    ``self_report`` is accepted to make its untrusted status explicit. A valid
    report cannot replace the checkpoint or repair missing records. The check
    says nothing about events after the most recent observed ledger tip that
    were never included in an independently retained checkpoint.
    """
    del self_report
    if checkpoint is None:
        return ContinuityAssessment(False, "NO_EXTERNAL_CHECKPOINT")
    if (
        not checkpoint.subject_id
        or not claimed_subject_id
        or checkpoint.entry_count < 1
        or not checkpoint.tip_hash
        or checkpoint.subject_id != claimed_subject_id
    ):
        return ContinuityAssessment(False, "INVALID_OR_MISMATCHED_CHECKPOINT")
    if not Chronicle.verify(ledger_path):
        return ContinuityAssessment(False, "INVALID_CHAIN")

    entries = list(Chronicle(ledger_path).read_all())
    if not entries:
        return ContinuityAssessment(False, "EMPTY_LEDGER")
    if len(entries) < checkpoint.entry_count:
        return ContinuityAssessment(False, "CHECKPOINT_AHEAD_OF_LEDGER")
    genesis = entries[0]
    if genesis["event_type"] != "IDENTITY_START" or genesis["data"].get("subject_id") != claimed_subject_id:
        return ContinuityAssessment(False, "GENESIS_SUBJECT_MISMATCH")
    if entries[checkpoint.entry_count - 1]["hash"] != checkpoint.tip_hash:
        return ContinuityAssessment(False, "CHECKPOINT_TIP_MISMATCH")
    return ContinuityAssessment(True, "WITNESSED_RECORD_PREFIX_AND_VALID_EXTENSION")
