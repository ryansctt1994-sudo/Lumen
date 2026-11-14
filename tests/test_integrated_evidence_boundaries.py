"""Cross-component checks for the combined Lumen repair candidates.

This is not external witnessing or production verification. It exercises the
exact combined code path from Chronicle through replay/receipt and the local
SQLite replay cache.
"""
from __future__ import annotations

import json

import pytest

from lumen import Chronicle, Receipt, replay_ledger
from lumen.authority import WeaverVerifier
from lumen.replay_cache import SQLiteReplayCache


def test_receipt_authority_and_sqlite_replay_stay_bounded_to_local_evidence(tmp_path):
    log = tmp_path / "chronicle.jsonl"
    claim = {"intent": "review", "risk": "none asserted"}
    chronicle = Chronicle(log)
    event = chronicle.append("PROPOSE", claim)
    replay = replay_ledger(log)
    assert replay["valid"] is True
    assert replay["entry_count"] == 1
    assert replay["last_hash"] == event["hash"]

    receipt = Receipt.create(
        actor_id="bounded-test",
        event_hash=event["hash"],
        previous_event_hash=event["prev_hash"],
        policy_version="v0.1",
        proposal_payload=claim,
        admissibility_result="REVIEW_ONLY",
        replay_result="PASS",
        verifier_id="self-test",
    )
    result = WeaverVerifier().verify(claim, receipt, replay)
    assert result.authorized is True
    assert result.authority_level == "EVIDENCE_ONLY"

    cache = SQLiteReplayCache(tmp_path / "replay.sqlite")
    h = cache.insert(receipt.receipt_hash, {
        "claim_digest": receipt.proposal_payload_hash,
        "ledger_tip": replay["last_hash"],
        "status": result.authority_level,
    })
    assert cache.verify_chain() == {"valid": True, "entries": 1, "last_hash": h}
    assert cache.get_replay_report(receipt.receipt_hash)["entry_hash"] == h


def test_corrupted_persisted_chronicle_is_not_resumed_or_counted_as_fresh_replay(tmp_path):
    log = tmp_path / "chronicle.jsonl"
    chronicle = Chronicle(log)
    chronicle.append("PROPOSE", {"status": "VETO"})
    lines = log.read_text().splitlines()
    data = json.loads(lines[0])
    data["data"]["status"] = "ALLOW"  # no hash recomputation
    lines[0] = json.dumps(data)
    log.write_text("\n".join(lines) + "\n")

    assert Chronicle.verify(log) is False
    with pytest.raises(ValueError):
        Chronicle(log)
    # The current raw replay helper raises on corrupt history; it does not
    # return a misleading success result or evidence authority.
    with pytest.raises(ValueError):
        replay_ledger(log)


def test_negative_control_forged_replay_report_is_not_an_attested_witness(tmp_path):
    # A caller-supplied replay report is not authenticated. Constructing a
    # self-consistent report from an honest log does not prove its provenance.
    log = tmp_path / "chronicle.jsonl"
    chronicle = Chronicle(log)
    claim = {"intent": "review"}
    event = chronicle.append("VETO", {"status": "VETO"})
    receipt = Receipt.create(
        actor_id="self-test", event_hash=event["hash"],
        previous_event_hash=event["prev_hash"], policy_version="v0.1",
        proposal_payload=claim, admissibility_result="VETO",
        replay_result="PASS", verifier_id="self",
    )
    # Claim-level 'authorized' refers ONLY to admissible local evidence:
    # it neither executes nor permits the underlying action.
    forged = {"valid": True, "last_hash": event["hash"]}
    result = WeaverVerifier().verify(claim, receipt, forged)
    assert result.authorized is True
    assert result.authority_level == "EVIDENCE_ONLY"
