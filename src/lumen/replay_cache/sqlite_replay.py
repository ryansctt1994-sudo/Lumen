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
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def insert(self, receipt_id: str, data: Dict[str, Any], prev_hash: Optional[str] = None) -> str:
        entry_hash = self.compute_entry_hash(receipt_id, data, prev_hash)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO replay_entries (receipt_id, entry_hash, timestamp, data, prev_hash)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(receipt_id) DO NOTHING
                """,
                (
                    receipt_id,
                    entry_hash,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(data, sort_keys=True),
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
                "SELECT receipt_id, entry_hash, data, prev_hash FROM replay_entries ORDER BY id"
            ).fetchall()

        previous = None
        for receipt_id, entry_hash, data, prev_hash in rows:
            parsed = json.loads(data)
            expected = self.compute_entry_hash(receipt_id, parsed, prev_hash)
            if expected != entry_hash:
                return {"valid": False, "entries": len(rows), "reason": "hash_mismatch", "last_hash": previous}
            if prev_hash != previous:
                return {"valid": False, "entries": len(rows), "reason": "prev_hash_mismatch", "last_hash": previous}
            previous = entry_hash

        return {"valid": True, "entries": len(rows), "last_hash": previous}
