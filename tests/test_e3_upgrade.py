from lumen import Chronicle, Receipt, replay_ledger
from lumen.authority import WeaverVerifier
from lumen.replay_cache import SQLiteReplayCache


def test_sqlite_replay_cache_chain(tmp_path):
    cache = SQLiteReplayCache(tmp_path / "cache.sqlite")
    h1 = cache.insert("r1", {"valid": True}, None)
    h2 = cache.insert("r2", {"valid": True}, h1)
    report = cache.verify_chain()
    assert report["valid"] is True
    assert report["entries"] == 2
    assert report["last_hash"] == h2


def test_weaver_verifier_authorizes_evidence_only(tmp_path):
    path = tmp_path / "audit.jsonl"
    chronicle = Chronicle(path)
    event = chronicle.append("EVENT", {"ok": True})
    replay = replay_ledger(path)
    receipt = Receipt.create(
        actor_id="tester",
        event_hash=event["hash"],
        previous_event_hash=event["prev_hash"],
        policy_version="v0.1",
        proposal_payload={"claim": "demo"},
        admissibility_result="HALT_ON_THRESHOLD",
        replay_result="PASS",
        verifier_id="unit",
    )
    result = WeaverVerifier(policy_version="v0.1").verify({"claim": "demo"}, receipt, replay)
    assert result.authorized is True
    assert result.authority_level == "EVIDENCE_ONLY"


def test_weaver_verifier_fails_closed_on_bad_replay(tmp_path):
    path = tmp_path / "audit.jsonl"
    chronicle = Chronicle(path)
    event = chronicle.append("EVENT", {"ok": True})
    receipt = Receipt.create(
        actor_id="tester",
        event_hash=event["hash"],
        previous_event_hash=event["prev_hash"],
        policy_version="v0.1",
        proposal_payload={"claim": "demo"},
        admissibility_result="HALT_ON_THRESHOLD",
        replay_result="PASS",
        verifier_id="unit",
    )
    result = WeaverVerifier(policy_version="v0.1").verify({"claim": "demo"}, receipt, {"valid": False})
    assert result.authorized is False
    assert result.authority_level == "NONE"
