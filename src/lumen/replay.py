"""Replay verification helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .chronicle import Chronicle


def replay_ledger(path: str | Path) -> Dict[str, Any]:
    """Replay a Chronicle ledger and return a compact verification report."""
    ledger_path = Path(path)
    valid = Chronicle.verify(ledger_path)
    count = 0
    last_hash = None

    if ledger_path.exists():
        chronicle = Chronicle(ledger_path)
        for entry in chronicle.read_all():
            count += 1
            last_hash = entry.get("hash")

    return {
        "path": str(ledger_path),
        "valid": valid,
        "entry_count": count,
        "last_hash": last_hash,
        "authority": "NONE" if not valid else "EVIDENCE_ONLY",
    }
