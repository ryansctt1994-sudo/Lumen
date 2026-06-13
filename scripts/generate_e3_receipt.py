#!/usr/bin/env python3
"""Generate a local E3 candidate receipt package.

This script produces local artifacts that can support an E3 promotion after
review. E3 is not claimed merely by generating the files; the files must be
committed, hashed, and independently checked.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from lumen import Chronicle, HardwareVeto, LatchState, Receipt, replay_ledger
from lumen.replay_cache import SQLiteReplayCache


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "UNKNOWN"


def run_demo(log_path: Path) -> Dict[str, Any]:
    if log_path.exists():
        log_path.unlink()

    chronicle = Chronicle(log_path)
    veto = HardwareVeto(threshold=0.75)
    proposal = {"action": "simulated_inference", "model": "demo", "risk_policy": "v0.1"}
    start = chronicle.append("PROPOSAL_RECEIVED", proposal)
    final_event = start

    for step, risk in enumerate([0.10, 0.25, 0.43, 0.62, 0.77], start=1):
        state = veto.evaluate(risk, reason=f"risk threshold crossed at step {step}")
        final_event = chronicle.append(
            "INFERENCE_STEP",
            {"step": step, "risk_score": risk, "latch_state": state.value, "halted": veto.is_halted},
        )
        if state == LatchState.TRIGGERED:
            final_event = chronicle.append(
                "SYSTEM_HALT",
                {"step": step, "reason": veto.trigger_reason, "latch_state": state.value},
            )
            break

    replay = replay_ledger(log_path)
    receipt = Receipt.create(
        actor_id="demo_operator",
        event_hash=final_event["hash"],
        previous_event_hash=final_event["prev_hash"],
        policy_version="v0.1",
        proposal_payload=proposal,
        admissibility_result="HALT_ON_THRESHOLD",
        replay_result="PASS" if replay["valid"] else "FAIL",
        verifier_id="lumen.scripts.generate_e3_receipt",
    )
    return {"replay": replay, "receipt": receipt.to_dict()}


def generate_e3_package() -> Dict[str, Any]:
    receipts_dir = Path("receipts")
    receipts_dir.mkdir(exist_ok=True)
    log_path = receipts_dir / "demo_audit_log.jsonl"
    package_path = receipts_dir / "demo_receipt.json"
    manifest_path = receipts_dir / "demo_receipt.sha256"
    cache_path = receipts_dir / "demo_replay_cache.sqlite"

    demo_output = run_demo(log_path)
    cache = SQLiteReplayCache(cache_path)
    cache_hash = cache.insert("demo_receipt", demo_output)
    cache_report = cache.verify_chain()

    package = {
        "receipt_id": f"demo_e3_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "commit_hash": git_head(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evidence_level": "E3_CANDIDATE",
        "authority": "EVIDENCE_ONLY",
        "demo_output": demo_output,
        "validation_manifest": {
            "audit_log_sha256": sha256_file(log_path),
            "sqlite_cache_entry_hash": cache_hash,
            "sqlite_cache_valid": cache_report["valid"],
        },
        "verification_instructions": "Run `python scripts/verify_e3_package.py`",
    }

    package_path.write_text(json.dumps(package, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest_path.write_text(f"{sha256_file(package_path)}  {package_path}\n", encoding="utf-8")
    print(f"E3 candidate package written to {package_path}")
    print(f"Manifest written to {manifest_path}")
    return package


if __name__ == "__main__":
    generate_e3_package()
