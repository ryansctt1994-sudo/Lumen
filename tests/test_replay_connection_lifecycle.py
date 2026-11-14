"""Regression controls frozen before the bounded connection-lifecycle repair."""
import pytest

import lumen.replay_cache.sqlite_replay as module


@pytest.mark.parametrize("operation", ["init", "insert", "verify", "get"])
def test_public_cache_calls_close_every_connection(tmp_path, monkeypatch, operation):
    original = module.sqlite3.connect
    observed = []

    class Tracked:
        def __init__(self, raw):
            self.raw = raw
            self.closed = False

        def __getattr__(self, name):
            return getattr(self.raw, name)

        def __enter__(self):
            self.raw.__enter__()
            return self

        def __exit__(self, *args):
            return self.raw.__exit__(*args)

        def close(self):
            self.raw.close()
            self.closed = True

    def tracked(*args, **kwargs):
        value = Tracked(original(*args, **kwargs))
        observed.append(value)
        return value

    monkeypatch.setattr(module.sqlite3, "connect", tracked)
    try:
        cache = module.SQLiteReplayCache(tmp_path / "cache.sqlite")
        if operation == "insert":
            cache.insert("fixture", {"value": 1})
        elif operation == "verify":
            cache.verify_chain()
        elif operation == "get":
            cache.get_replay_report("missing")
        assert observed and all(conn.closed for conn in observed)
    finally:
        for conn in observed:
            conn.close()
