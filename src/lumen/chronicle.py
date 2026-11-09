"""Append-only SHA-256 hash-chained audit ledger."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
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
        self._uncertain_persist = False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._resume()

    @staticmethod
    def _unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate Chronicle JSON key")
            result[key] = value
        return result

    @staticmethod
    def _reject_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    @staticmethod
    def _finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("nonfinite JSON exponent")
        return number

    @classmethod
    def _scan_history(cls, path: str | Path) -> tuple[Optional[str], int]:
        """Validate before accepting a persisted head. No external trust claimed."""
        previous: Optional[str] = None
        count = 0
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    raise ValueError("blank Chronicle record")
                entry = json.loads(line, object_pairs_hook=cls._unique_keys,
                                   parse_constant=cls._reject_constant,
                                   parse_float=cls._finite_float)
                if not isinstance(entry, dict) or set(entry) != {
                    "timestamp", "event_type", "data", "metadata", "prev_hash", "hash"
                }:
                    raise ValueError("invalid Chronicle record schema")
                if not isinstance(entry["timestamp"], str) or not isinstance(entry["event_type"], str):
                    raise ValueError("invalid Chronicle record identity")
                if not isinstance(entry["data"], dict) or not isinstance(entry["metadata"], dict):
                    raise ValueError("invalid Chronicle record payload")
                if not isinstance(entry["hash"], str) or re.fullmatch(r"[0-9a-f]{64}", entry["hash"]) is None:
                    raise ValueError("invalid Chronicle record hash")
                if entry["prev_hash"] != previous:
                    raise ValueError("Chronicle predecessor mismatch")
                body = {k: entry[k] for k in ("timestamp", "event_type", "data", "metadata", "prev_hash")}
                if cls.compute_hash(body) != entry["hash"]:
                    raise ValueError("Chronicle record digest mismatch")
                previous = entry["hash"]
                count += 1
        return previous, count

    def _resume(self) -> None:
        if not self.path.exists():
            return
        # No partial state is admitted on an invalid or ambiguous history.
        last, count = self._scan_history(self.path)
        self.last_hash, self.entry_count = last, count

    @staticmethod
    def _canonical(payload: Dict[str, Any]) -> bytes:
        return json.dumps(payload, sort_keys=True, separators=(",", ":"),
                          allow_nan=False).encode("utf-8")

    @classmethod
    def compute_hash(cls, payload: Dict[str, Any]) -> str:
        return hashlib.sha256(cls._canonical(payload)).hexdigest()

    def append(self, event_type: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not isinstance(event_type, str) or not isinstance(data, dict) or not isinstance(metadata, (dict, type(None))):
            raise ValueError("invalid Chronicle append payload")
        with self.lock:
            if self._uncertain_persist:
                raise RuntimeError("prior Chronicle write outcome unknown; reopen and verify")
            if self.path.exists():
                last, count = self._scan_history(self.path)
                if (last, count) != (self.last_hash, self.entry_count):
                    raise ValueError("Chronicle on-disk history diverged")
            elif self.entry_count:
                raise ValueError("Chronicle history disappeared")
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": event_type,
                "data": data,
                "metadata": metadata or {},
                "prev_hash": self.last_hash,
            }
            entry["hash"] = self.compute_hash(entry)
            encoded = json.dumps(entry, sort_keys=True, allow_nan=False) + "\n"
            try:
                with self.path.open("a", encoding="utf-8") as handle:
                    handle.write(encoded)
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError:
                # The append effect may be absent, partial or durable. No
                # in-process retry can safely decide which; reopen and verify.
                self._uncertain_persist = True
                raise
            self.last_hash = entry["hash"]
            self.entry_count += 1
            return entry

    @classmethod
    def verify(cls, path: str | Path) -> bool:
        try:
            cls._scan_history(path)
            return True
        except (OSError, UnicodeError, ValueError, TypeError, OverflowError):
            return False

    def read_all(self) -> Iterator[Dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
