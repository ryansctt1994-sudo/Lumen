"""P0-002: concurrent append admission and on-disk chain corruption tests."""

from __future__ import annotations

import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from lumen.replay_cache import SQLiteReplayCache


def test_non_genesis_predecessor_refused_on_empty_ledger(tmp_path):
    cache = SQLiteReplayCache(tmp_path / "cache.sqlite")
    with pytest.raises(ValueError, match="predecessor|chain"):
        cache.insert("first", {"value": 1}, "f" * 64)
    assert cache.verify_chain() == {"valid": True, "entries": 0, "last_hash": None}


@pytest.mark.parametrize("wrong_tip", [None, "0" * 64])
def test_nonempty_ledger_refuses_stale_or_missing_predecessor(tmp_path, wrong_tip):
    cache = SQLiteReplayCache(tmp_path / "cache.sqlite")
    first = cache.insert("first", {"value": 1})
    with pytest.raises(ValueError, match="predecessor|chain"):
        cache.insert("second", {"value": 2}, wrong_tip)
    report = cache.verify_chain()
    assert report["valid"] is True
    assert report["entries"] == 1
    assert report["last_hash"] == first


def test_two_independent_writers_competing_for_one_tip(tmp_path):
    path = tmp_path / "cache.sqlite"
    seed = SQLiteReplayCache(path)
    tip = seed.insert("seed", {"value": 0})
    barrier = Barrier(2)

    def attempt(item):
        cache = SQLiteReplayCache(path)
        barrier.wait()
        try:
            return cache.insert(f"writer-{item}", {"value": item}, tip)
        except ValueError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, (1, 2)))

    assert sum(hash_value is not None for hash_value in outcomes) == 1
    report = SQLiteReplayCache(path).verify_chain()
    assert report["valid"] is True
    assert report["entries"] == 2
    assert report["last_hash"] in outcomes


def test_existing_idempotent_retry_survives_head_advance(tmp_path):
    cache = SQLiteReplayCache(tmp_path / "cache.sqlite")
    first = cache.insert("first", {"value": 1})
    second = cache.insert("second", {"value": 2}, first)
    assert cache.insert("first", {"value": 1}) == first
    assert cache.verify_chain() == {"valid": True, "entries": 2, "last_hash": second}


def test_tampered_prior_entry_blocks_new_write(tmp_path):
    path = tmp_path / "cache.sqlite"
    cache = SQLiteReplayCache(path)
    first = cache.insert("first", {"value": 1})
    with sqlite3.connect(path) as conn:
        conn.execute(
            "UPDATE replay_entries SET data = ? WHERE receipt_id = ?",
            (json.dumps({"value": 999}), "first"),
        )
    assert cache.verify_chain()["valid"] is False
    with pytest.raises(ValueError, match="corrupt|chain"):
        cache.insert("second", {"value": 2}, first)
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM replay_entries").fetchone()[0] == 1


def test_malformed_disk_json_fails_closed_and_cannot_be_extended(tmp_path):
    path = tmp_path / "cache.sqlite"
    cache = SQLiteReplayCache(path)
    first = cache.insert("first", {"value": 1})
    with sqlite3.connect(path) as conn:
        conn.execute("UPDATE replay_entries SET data = 'not-json' WHERE receipt_id = 'first'")
    report = cache.verify_chain()
    assert report["valid"] is False
    assert report["reason"] == "malformed_entry"
    with pytest.raises(ValueError, match="corrupt|chain"):
        cache.insert("second", {"value": 2}, first)
