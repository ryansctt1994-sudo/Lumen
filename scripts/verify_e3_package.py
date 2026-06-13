#!/usr/bin/env python3
"""Verify local E3 candidate package integrity."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    package_path = Path("receipts/demo_receipt.json")
    manifest_path = Path("receipts/demo_receipt.sha256")

    if not package_path.exists():
        raise SystemExit("missing receipts/demo_receipt.json")
    if not manifest_path.exists():
        raise SystemExit("missing receipts/demo_receipt.sha256")

    expected = manifest_path.read_text(encoding="utf-8").split()[0]
    actual = sha256_file(package_path)
    if expected != actual:
        raise SystemExit(f"manifest mismatch: expected {expected}, got {actual}")

    package = json.loads(package_path.read_text(encoding="utf-8"))
    replay = package.get("demo_output", {}).get("replay", {})
    receipt = package.get("demo_output", {}).get("receipt", {})

    checks = {
        "manifest_hash_matches": expected == actual,
        "replay_valid": replay.get("valid") is True,
        "authority_evidence_only": package.get("authority") == "EVIDENCE_ONLY",
        "receipt_hash_present": bool(receipt.get("receipt_hash")),
        "event_hash_present": bool(receipt.get("event_hash")),
    }

    if not all(checks.values()):
        raise SystemExit(f"verification failed: {checks}")

    print(json.dumps({"status": "PASS", "checks": checks}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
