"""SQLite-backed replay cache.

This cache provides duplicate-resistant storage for replay reports and receipt
artifacts. It is local evidence infrastructure, not production WORM storage.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class SQLiteReplayCache:
    def __init__(self, db_path: str | Path = "lumen_replay.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS replay_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    receipt_id TEXT UNIQUE NOT NULL,
                    entry_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL,
                    prev_hash TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_replay_receipt ON replay_entries(receipt_id);
                CREATE INDEX IF NOT EXISTS idx_replay_entry_hash ON replay_entries(entry_hash);
                """
            )

    @staticmethod
    def compute_entry_hash(receipt_id: str, data: Dict[str, Any], prev_hash: Optional[str]) -> str:
        payload = {
            "receipt_id": receipt_id,
            "data": data,
            "prev_hash": prev_hash,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @classmethod
    def _check_rows(cls, rows: list[tuple[str, str, str, Optional[str]]]) -> Dict[str, Any]:
        """Validate every stored link, not merely the current tail.

        This linear scan is intentional for the bounded local evidence cache.
        A successful scan is not an external anchor or trusted signature.
        """
        previous = None
        for receipt_id, entry_hash, data, prev_hash in rows:
            try:
                parsed = json.loads(data)
                if not isinstance(parsed, dict):
                    raise ValueError("stored replay data is not an object")
                expected = cls.compute_entry_hash(receipt_id, parsed, prev_hash)
            except (TypeError, ValueError):
                return {
                    "valid": False,
                    "entries": len(rows),
                    "reason": "malformed_entry",
                    "last_hash": previous,
                }
            if expected != entry_hash:
                return {
                    "valid": False,
                    "entries": len(rows),
                    "reason": "hash_mismatch",
                    "last_hash": previous,
                }
            if prev_hash != previous:
                return {
                    "valid": False,
                    "entries": len(rows),
                    "reason": "prev_hash_mismatch",
                    "last_hash": previous,
                }
            previous = entry_hash
        return {"valid": True, "entries": len(rows), "last_hash": previous}

    def insert(self, receipt_id: str, data: Dict[str, Any], prev_hash: Optional[str] = None) -> str:
        entry_hash = self.compute_entry_hash(receipt_id, data, prev_hash)
        with self._connect() as conn:
            # SQLite serializes competing writers before predecessor inspection.
            # The check and the append must happen within this same transaction.
            conn.execute("BEGIN IMMEDIATE")
            rows = conn.execute(
                "SELECT receipt_id, entry_hash, data, prev_hash "
                "FROM replay_entries ORDER BY id"
            ).fetchall()
            chain = self._check_rows(rows)
            if chain["valid"] is not True:
                raise ValueError(f"corrupt replay chain: {chain['reason']}")

            existing = conn.execute(
                "SELECT entry_hash, data, prev_hash FROM replay_entries WHERE receipt_id = ?",
                (receipt_id,),
            ).fetchone()
            if existing is not None:
                stored_hash, stored_data, stored_prev = existing
                if (
                    stored_hash != entry_hash
                    or json.loads(stored_data) != data
                    or stored_prev != prev_hash
                ):
                    raise ValueError("conflicting receipt_id already stored")
                return stored_hash

            # A new entry must extend exactly the verified tip (None at genesis).
            # Stale clients must re-read and retry with a fresh predecessor.
            if prev_hash != chain["last_hash"]:
                raise ValueError("stale or mismatched replay predecessor")

            conn.execute(
                """
                INSERT INTO replay_entries (receipt_id, entry_hash, timestamp, data, prev_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    entry_hash,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(data, sort_keys=True, allow_nan=False),
                    prev_hash,
                ),
            )
        return entry_hash

    def get_replay_report(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT receipt_id, entry_hash, timestamp, data, prev_hash FROM replay_entries WHERE receipt_id = ?",
                (receipt_id,),
            ).fetchone()
        if row is None:
            return None
        rid, entry_hash, timestamp, data, prev_hash = row
        return {
            "receipt_id": rid,
            "entry_hash": entry_hash,
            "timestamp": timestamp,
            "data": json.loads(data),
            "prev_hash": prev_hash,
        }

    def verify_chain(self) -> Dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT receipt_id, entry_hash, data, prev_hash "
                "FROM replay_entries ORDER BY id"
            ).fetchall()
        return self._check_rows(rows)
