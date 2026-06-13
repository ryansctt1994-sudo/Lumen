"""Append-only SHA-256 hash-chained audit ledger."""

from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, Optional


class Chronicle:
    """Append-only tamper-evident ledger.

    This is tamper-evident, not tamper-proof. Production deployments should add
    WORM storage, external witnesses, transparency logs, or checkpoint signing.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.last_hash: Optional[str] = None
        self.entry_count = 0
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._resume()

    def _resume(self) -> None:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    entry = json.loads(line)
                    self.last_hash = entry["hash"]
                    self.entry_count += 1

    @staticmethod
    def _canonical(payload: Dict[str, Any]) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def compute_hash(cls, payload: Dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical(payload)).hexdigest()

    def append(self, event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with self.lock:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "data": data,
                "metadata": metadata or {},
                "prev_hash": self.last_hash,
            }
            entry["hash"] = self.compute_hash(entry)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
            self.last_hash = entry["hash"]
            self.entry_count += 1
            return entry

    @classmethod
    def verify(cls, path: str | Path) -> bool:
        prev = None
        try:
            with Path(path).open("r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    payload = {k: entry[k] for k in ["timestamp", "event_type", "data", "metadata", "prev_hash"]}
                    if cls.compute_hash(payload) != entry["hash"]:
                        return False
                    if entry["prev_hash"] != prev:
                        return False
                    prev = entry["hash"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return False
        return True

    def read_all(self) -> Iterator[Dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
