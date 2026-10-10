"""Chronicle startup / append hardening: native fail-closed regressions."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from lumen.chronicle import Chronicle


class ChronicleResumeIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "history.jsonl"
        ledger = Chronicle(self.path)
        ledger.append("synthetic", {"v": 1})
        ledger.append("synthetic", {"v": 2})

    def test_healthy_history_resumes(self):
        resumed = Chronicle(self.path)
        self.assertEqual(resumed.entry_count, 2)
        self.assertEqual(resumed.last_hash, list(resumed.read_all())[-1]["hash"])
        self.assertTrue(Chronicle.verify(self.path))

    def test_prior_entry_tamper_denied_at_construction(self):
        self.path.write_text(self.path.read_text().replace('"v": 1', '"v": 8'))
        self.assertFalse(Chronicle.verify(self.path))
        with self.assertRaises(ValueError):
            Chronicle(self.path)

    def test_forged_final_hash_denied(self):
        records = self.path.read_text().splitlines()
        last = json.loads(records[-1])
        last["hash"] = "f" * 64
        records[-1] = json.dumps(last)
        self.path.write_text("\n".join(records) + "\n")
        with self.assertRaises(ValueError):
            Chronicle(self.path)

    def test_duplicate_json_key_denied(self):
        self.path.write_text(self.path.read_text().replace('"hash": ', '"hash": "f", "hash": ', 1))
        with self.assertRaises(ValueError):
            Chronicle(self.path)

    def test_nonfinite_exponent_denied(self):
        self.path.write_text(self.path.read_text().replace('"v": 1', '"v": 1e999', 1))
        with self.assertRaises(ValueError):
            Chronicle(self.path)

    def test_append_refuses_external_file_drift(self):
        c = Chronicle(self.path)
        self.path.write_text(self.path.read_text().splitlines()[0] + "\n")
        with self.assertRaises(ValueError):
            c.append("other", {"v": 3})
        self.assertEqual(c.entry_count, 2)

    def test_nan_refused_without_mutation(self):
        c = Chronicle(self.path)
        before = (c.last_hash, c.entry_count, self.path.read_bytes())
        with self.assertRaises(ValueError):
            c.append("bad", {"v": float("nan")})
        self.assertEqual((c.last_hash, c.entry_count, self.path.read_bytes()), before)

    def test_unknown_fsync_write_poisoned_by_disk_drift(self):
        c = Chronicle(self.path)
        with patch("lumen.chronicle.os.fsync", side_effect=OSError("injected durability unknown")):
            with self.assertRaises(OSError):
                c.append("unknown", {"v": 3})
        with self.assertRaises(RuntimeError):
            c.append("retry", {"v": 4})
        self.assertEqual(c.entry_count, 2)

    def test_fsync_unknown_stays_poisoned_even_after_disk_restoration(self):
        c = Chronicle(self.path)
        before = self.path.read_bytes()
        with patch("lumen.chronicle.os.fsync", side_effect=OSError("uncertain")):
            with self.assertRaises(OSError):
                c.append("uncertain", {"v": 3})
        self.path.write_bytes(before)
        with self.assertRaises(RuntimeError):
            c.append("must-not-retry", {"v": 4})
        self.assertEqual(c.entry_count, 2)

    def test_truncated_record_denied(self):
        self.path.write_text(self.path.read_text()[:-9])
        with self.assertRaises(ValueError):
            Chronicle(self.path)

    def test_missing_file_verify_fails(self):
        self.path.unlink()
        self.assertFalse(Chronicle.verify(self.path))

    def test_no_false_independent_authority(self):
        self.assertNotIn("signature", Chronicle(self.path).__dict__)
        self.assertNotIn("witness", Chronicle(self.path).__dict__)


if __name__ == "__main__":
    unittest.main()
