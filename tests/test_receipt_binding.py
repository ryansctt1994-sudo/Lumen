from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor

import pytest

from lumen.authority import WeaverVerifier
from lumen.receipt import Receipt
from lumen.replay_cache import SQLiteReplayCache


def receipt_for(claim):
    return Receipt.create(
        actor_id="test", event_hash="f" * 64, previous_event_hash=None,
        policy_version="v0.1", proposal_payload=claim, admissibility_result="PASS",
        replay_result="PASS", verifier_id="test",
    )


@pytest.mark.parametrize("report", [
    {"valid": True}, {"valid": True, "last_hash": None},
    {"valid": True, "last_hash": "not-a-hash"},
    {"valid": "true", "last_hash": "f" * 64},
])
def test_report_requires_boolean_pass_and_bound_tip(report):
    claim = {"claim": "A"}
    assert not WeaverVerifier().verify(claim, receipt_for(claim), report).authorized


def test_claim_substitution_is_refused():
    receipt = receipt_for({"claim": "A"})
    assert not WeaverVerifier().verify(
        {"claim": "B"}, receipt, {"valid": True, "last_hash": "f" * 64}
    ).authorized


def test_modified_receipt_is_refused_even_with_matching_tip():
    claim = {"claim": "A"}
    receipt = replace(receipt_for(claim), event_hash="e" * 64)
    assert not WeaverVerifier().verify(
        claim, receipt, {"valid": True, "last_hash": "e" * 64}
    ).authorized


def test_nonfinite_payload_cannot_be_receipted():
    with pytest.raises(ValueError):
        receipt_for({"score": float("nan")})


def test_cache_retry_is_idempotent_but_conflict_is_refused(tmp_path):
    cache = SQLiteReplayCache(tmp_path / "cache.db")
    original = cache.insert("r1", {"value": 1})
    assert cache.insert("r1", {"value": 1}) == original
    with pytest.raises(ValueError, match="conflicting"):
        cache.insert("r1", {"value": 2})
    assert cache.get_replay_report("r1")["entry_hash"] == original
    assert cache.verify_chain()["valid"] is True


def test_concurrent_conflicts_store_exactly_one_payload(tmp_path):
    cache = SQLiteReplayCache(tmp_path / "cache.db")

    def insert(value):
        try:
            return cache.insert("same-id", {"value": value})
        except ValueError:
            return None

    with ThreadPoolExecutor(max_workers=2) as executor:
        hashes = list(executor.map(insert, [1, 2]))
    assert sum(value is not None for value in hashes) == 1
    assert cache.get_replay_report("same-id")["entry_hash"] in hashes
    assert cache.verify_chain()["entries"] == 1


def test_package_generation_can_repeat_without_stale_cache(tmp_path, monkeypatch):
    import importlib.util
    from pathlib import Path

    script = Path(__file__).parents[1] / "scripts" / "generate_e3_receipt.py"
    spec = importlib.util.spec_from_file_location("package_generator", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.chdir(tmp_path)
    first = module.generate_e3_package()
    second = module.generate_e3_package()
    assert first["receipt_id"] != second["receipt_id"]
    cache = SQLiteReplayCache(tmp_path / "receipts" / "demo_replay_cache.sqlite")
    stored = cache.get_replay_report(second["receipt_id"])
    assert stored["data"] == second["demo_output"]
    assert stored["entry_hash"] == second["validation_manifest"]["sqlite_cache_entry_hash"]
    assert cache.verify_chain()["valid"] is True
    assert cache.verify_chain()["entries"] == 2
