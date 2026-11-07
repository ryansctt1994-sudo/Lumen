#!/usr/bin/env python3
"""Verify local E3 candidate package integrity.

Implements the R4 protocol freeze (2026-11-07, from LUMEN-AVR-2026-09-21
CE-4/CE-5, Recommendation R4). Validated against the preregistered R4
negative tests (control + five negative cases: 6/6) and the shipped suite
(13/13); the tests also detect protection removal (stubbing the new checks
returns the suite to 1/6).

  R1  Read validation_manifest.audit_log_sha256, compute the SHA-256 of the
      actual audit-log file, fail closed on mismatch / absence / unreadable
      log. (The replay check alone cannot catch an emptied log:
      replay_ledger() on a 0-byte log returns valid=True — vacuous truth —
      so the hash check is load-bearing here.)
  R2  Re-derive replay by calling replay_ledger() against the ledger
      artifact; never trust the package-internal replay.valid field. The
      receipt claims are likewise re-derived from the audit log: the
      receipt's receipt_hash is recomputed from the stored receipt fields
      (Receipt.hash_payload — the same primitive the generator uses) and
      the receipt's event_hash is compared against the fresh replay's
      last_hash. This is what closes CE-5: a forger who rewrites package
      fields and recomputes only the sibling digest leaves a receipt_hash
      that no longer matches the forged fields.
  R3  Fail closed on missing/unreadable artifacts; no default-to-true paths.
  R4  The sibling manifest digest stays a local consistency check only.

Boundary (per the freeze): a forger who also recomputes receipt_hash and
the manifest's audit_log_sha256 defeats these checks — that is the
external-custody problem (R5), explicitly out of scope for this freeze.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# The verifier is run with cwd=<package tree root>; make the tree's own src/
# importable so replay_ledger() and Receipt can be called without PYTHONPATH.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    package_path = Path("receipts/demo_receipt.json")
    manifest_path = Path("receipts/demo_receipt.sha256")
    log_path = Path("receipts/demo_audit_log.jsonl")

    if not package_path.exists():
        raise SystemExit("missing receipts/demo_receipt.json")
    if not manifest_path.exists():
        raise SystemExit("missing receipts/demo_receipt.sha256")

    expected = manifest_path.read_text(encoding="utf-8").split()[0]
    actual = sha256_file(package_path)
    if expected != actual:
        raise SystemExit(f"manifest mismatch: expected {expected}, got {actual}")

    package = json.loads(package_path.read_text(encoding="utf-8"))
    stored_replay = package.get("demo_output", {}).get("replay", {})
    receipt = package.get("demo_output", {}).get("receipt", {})

    # R1/R3 — audit-log hash binding. Read the manifest's recorded hash,
    # hash the actual log file, fail closed on mismatch, absence, or an
    # unreadable log. No default-to-true path.
    recorded_log_hash = package.get("validation_manifest", {}).get("audit_log_sha256")
    try:
        actual_log_hash = sha256_file(log_path)
    except (OSError, ValueError):
        actual_log_hash = None
    audit_log_hash_matches = (
        isinstance(recorded_log_hash, str)
        and recorded_log_hash != ""
        and actual_log_hash is not None
        and actual_log_hash == recorded_log_hash
    )

    # R2 — replay re-derived, never asserted. Call replay_ledger() against
    # the ledger artifact and use the freshly computed result. Any failure
    # to re-derive is a failed check, not a pass.
    fresh_replay = None
    try:
        from lumen.replay import replay_ledger

        fresh_replay = replay_ledger(log_path)
        replay_valid = fresh_replay.get("valid") is True
    except Exception:
        replay_valid = False

    # R2 (receipt claims re-derived from the audit log). The stored replay
    # claims must agree with what the log actually says, and the receipt
    # must be bound to the log: its receipt_hash must recompute from its
    # own stored fields, and its event_hash must equal the fresh replay's
    # last_hash (the hash of the log's final entry).
    replay_claims_agree = False
    receipt_hash_matches = False
    receipt_event_bound_to_log = False
    if fresh_replay is not None:
        replay_claims_agree = (
            stored_replay.get("entry_count") == fresh_replay.get("entry_count")
            and stored_replay.get("last_hash") == fresh_replay.get("last_hash")
        )
        last_hash = fresh_replay.get("last_hash")
        receipt_event_bound_to_log = (
            last_hash is not None and receipt.get("event_hash") == last_hash
        )
    try:
        from lumen.receipt import Receipt

        stored_hash = receipt.get("receipt_hash")
        fields = {k: v for k, v in receipt.items() if k != "receipt_hash"}
        receipt_hash_matches = (
            isinstance(stored_hash, str)
            and stored_hash != ""
            and Receipt.hash_payload(fields) == stored_hash
        )
    except Exception:
        receipt_hash_matches = False

    checks = {
        "manifest_hash_matches": expected == actual,
        "audit_log_hash_matches": audit_log_hash_matches,
        "replay_valid": replay_valid,
        "replay_claims_agree": replay_claims_agree,
        "receipt_hash_matches": receipt_hash_matches,
        "receipt_event_bound_to_log": receipt_event_bound_to_log,
        "authority_evidence_only": package.get("authority") == "EVIDENCE_ONLY",
        "receipt_hash_present": bool(receipt.get("receipt_hash")),
        "event_hash_present": bool(receipt.get("event_hash")),
    }

    if not all(checks.values()):
        raise SystemExit(f"verification failed: {checks}")

    print(json.dumps({"status": "PASS", "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
