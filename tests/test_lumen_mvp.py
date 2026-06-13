from pathlib import Path

from lumen import Chronicle, HardwareVeto, LatchState, Receipt, replay_ledger


def test_chronicle_hash_chain_verifies(tmp_path):
    path = tmp_path / "audit.jsonl"
    chronicle = Chronicle(path)
    chronicle.append("START", {"ok": True})
    chronicle.append("END", {"ok": True})
    assert Chronicle.verify(path) is True


def test_hardware_veto_latches():
    veto = HardwareVeto(threshold=0.5)
    assert veto.evaluate(0.1) == LatchState.ARMED
    assert veto.evaluate(0.5) == LatchState.TRIGGERED
    assert veto.evaluate(0.0) == LatchState.TRIGGERED
    assert veto.is_halted is True


def test_replay_report(tmp_path):
    path = tmp_path / "audit.jsonl"
    chronicle = Chronicle(path)
    chronicle.append("EVENT", {"x": 1})
    report = replay_ledger(path)
    assert report["valid"] is True
    assert report["entry_count"] == 1
    assert report["authority"] == "EVIDENCE_ONLY"


def test_receipt_creation():
    receipt = Receipt.create(
        actor_id="tester",
        event_hash="abc",
        previous_event_hash=None,
        policy_version="v0.1",
        proposal_payload={"a": 1},
        admissibility_result="ALLOW",
        replay_result="PASS",
        verifier_id="unit",
    )
    assert receipt.receipt_hash
    assert receipt.proposal_payload_hash
