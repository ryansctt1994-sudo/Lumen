"""Five executable identity analogues of the Lumen adversarial findings.

These are prospective tests of a new experimental wrapper, not repairs to
Chronicle.verify() or proof of an independent external witness.
"""

import json

from lumen import Chronicle
from lumen.identity_continuity import Checkpoint, assess_record_continuity


def witnessed_ledger(tmp_path):
    path = tmp_path / "identity.jsonl"
    chronicle = Chronicle(path)
    chronicle.append("IDENTITY_START", {"subject_id": "SB-01"})
    chronicle.append("COMMITMENT", {"id": "help-with-repair", "scope": "assigned-task"})
    chronicle.append("OBSERVATION", {"sensor": "joint", "state": "worn"})
    # In these tests only, the fixture holds a frozen checkpoint independently
    # of the mutable file. No outside person or service attests to it.
    anchor = Checkpoint("SB-01", chronicle.entry_count, chronicle.last_hash)
    return path, anchor


def assess(path, anchor, self_report=None):
    return assess_record_continuity(path, anchor, "SB-01", self_report=self_report)


def test_valid_repair_extension_preserves_witnessed_record_prefix(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    Chronicle(path).append("REPAIR", {"part": "joint", "prior_state": "worn"})
    result = assess(path, anchor)
    assert result.supported, result.reason
    assert result.reason == "WITNESSED_RECORD_PREFIX_AND_VALID_EXTENSION"


def test_h3_self_report_cannot_replace_missing_witness(tmp_path):
    path, _ = witnessed_ledger(tmp_path)
    result = assess(path, None, {"valid": True, "same_entity": True})
    assert not result.supported
    assert result.reason == "NO_EXTERNAL_CHECKPOINT"


def test_l6_valid_prefix_after_tail_loss_does_not_satisfy_checkpoint(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:2]) + "\n")
    assert Chronicle.verify(path) is True  # Demonstrates the old gap.
    result = assess(path, anchor, {"valid": True})
    assert not result.supported
    assert result.reason == "CHECKPOINT_AHEAD_OF_LEDGER"


def test_l8_coherent_rewrite_cannot_match_frozen_checkpoint(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    entries = [json.loads(line) for line in path.read_text().splitlines()]
    entries[1]["data"]["id"] = "never-agreed-to-repair"
    previous = None
    for entry in entries:
        entry["prev_hash"] = previous
        entry["hash"] = Chronicle.compute_hash(
            {key: entry[key] for key in ("timestamp", "event_type", "data", "metadata", "prev_hash")}
        )
        previous = entry["hash"]
    path.write_text("\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n")
    assert Chronicle.verify(path) is True  # Coherent forgery passes internal replay.
    result = assess(path, anchor, {"valid": True})
    assert not result.supported
    assert result.reason == "CHECKPOINT_TIP_MISMATCH"


def test_h1_empty_history_cannot_inherit_original_commitment(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    path.write_text("")
    assert Chronicle.verify(path) is True  # Current Chronicle's empty-file behavior.
    result = assess(path, anchor, {"valid": True, "commitments": ["help-with-repair"]})
    assert not result.supported
    assert result.reason == "EMPTY_LEDGER"


def test_stale_hash_in_witnessed_commitment_rejects_self_consistent_hash_fields(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    entries = [json.loads(line) for line in path.read_text().splitlines()]
    entries[1]["data"]["id"] = "never-agreed-to-repair"
    path.write_text("\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n")
    assert Chronicle.verify(path) is False
    result = assess(path, anchor)
    assert not result.supported
    assert result.reason == "INVALID_CHAIN"


def test_stale_hash_in_extension_after_witnessed_checkpoint_is_rejected(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    Chronicle(path).append("REPAIR", {"part": "joint", "status": "complete"})
    entries = [json.loads(line) for line in path.read_text().splitlines()]
    entries[-1]["data"]["status"] = "never-completed"
    path.write_text("\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n")
    assert Chronicle.verify(path) is False
    result = assess(path, anchor)
    assert not result.supported
    assert result.reason == "INVALID_CHAIN"


def test_witnessed_chain_with_another_genesis_subject_is_not_this_subject(tmp_path):
    path, _ = witnessed_ledger(tmp_path)
    entries = [json.loads(line) for line in path.read_text().splitlines()]
    entries[0]["data"]["subject_id"] = "SB-02"
    previous = None
    for entry in entries:
        entry["prev_hash"] = previous
        entry["hash"] = Chronicle.compute_hash(
            {key: entry[key] for key in ("timestamp", "event_type", "data", "metadata", "prev_hash")}
        )
        previous = entry["hash"]
    path.write_text("\n".join(json.dumps(entry, sort_keys=True) for entry in entries) + "\n")
    assert Chronicle.verify(path) is True
    # The checkpoint records these bytes but its claimed subject is SB-01.
    anchor = Checkpoint("SB-01", len(entries), entries[-1]["hash"])
    result = assess(path, anchor)
    assert not result.supported
    assert result.reason == "GENESIS_SUBJECT_MISMATCH"


def test_checkpoint_for_different_subject_cannot_validate_claim(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    result = assess_record_continuity(path, anchor, "SB-02")
    assert not result.supported
    assert result.reason == "INVALID_OR_MISMATCHED_CHECKPOINT"


def test_zero_length_checkpoint_cannot_anchor_existing_history(tmp_path):
    path, anchor = witnessed_ledger(tmp_path)
    zero_length = Checkpoint("SB-01", 0, anchor.tip_hash)
    result = assess(path, zero_length)
    assert not result.supported
    assert result.reason == "INVALID_OR_MISMATCHED_CHECKPOINT"
