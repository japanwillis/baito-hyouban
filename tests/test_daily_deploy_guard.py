"""Regression tests for the proposed fail-closed JST publication window and server ledger."""
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts.deploy_window import require_deploy_window

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("remote_release_guard", BASE / "scripts/remote-release.py")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)
JST = ZoneInfo("Asia/Tokyo")


class WindowTests(unittest.TestCase):
    def test_first_deploy_at_three_allowed(self):
        self.assertEqual(require_deploy_window("deploy", datetime(2026, 11, 17, 3, 0, tzinfo=JST)), "2026-11-17")

    def test_at_16_rejected(self):
        with self.assertRaisesRegex(ValueError, "03:00"):
            require_deploy_window("deploy", datetime(2026, 11, 17, 16, 0, tzinfo=JST))

    def test_jst_midnight_boundary_and_utc(self):
        with self.assertRaises(ValueError):
            require_deploy_window("deploy", datetime(2026, 11, 17, 2, 59, tzinfo=JST))
        self.assertEqual(require_deploy_window("deploy", datetime(2026, 11, 16, 18, 59, tzinfo=ZoneInfo("UTC"))), "2026-11-17")
        with self.assertRaises(ValueError):
            require_deploy_window("deploy", datetime(2026, 11, 17, 4, 0, tzinfo=JST))

    def test_plan_and_rollback_not_blocked_by_window(self):
        for mode in ("plan", "rollback"):
            self.assertIsNone(require_deploy_window(mode, datetime(2026, 11, 17, 16, 0, tzinfo=JST)))

    def test_naive_clock_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            require_deploy_window("deploy", datetime(2026, 11, 17, 3, 0))


class ServerLedgerTests(unittest.TestCase):
    def test_same_day_rejects_second_even_different_release_id(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            at = datetime(2026, 11, 17, 3, 5, tzinfo=JST)
            receipt = remote.reserve_daily_deploy(base, "101-1", at)
            self.assertEqual(json.loads(receipt.read_text())["release_id"], "101-1")
            self.assertEqual(json.loads(receipt.read_text())["date_jst"], "2026-11-17")
            with self.assertRaisesRegex(ValueError, "already reserved"):
                remote.reserve_daily_deploy(base, "102-1", at)
            self.assertEqual(len(list((base / "daily-deploy").iterdir())), 1)

    def test_second_day_is_distinct_and_old_day_not_erased(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            remote.reserve_daily_deploy(base, "101-1", datetime(2026, 11, 17, 3, 5, tzinfo=JST))
            remote.reserve_daily_deploy(base, "102-1", datetime(2026, 11, 18, 3, 5, tzinfo=JST))
            self.assertEqual(len(list((base / "daily-deploy").iterdir())), 2)

    def test_guard_rejects_missed_window_before_ledger_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            with self.assertRaisesRegex(ValueError, "03:00"):
                remote.reserve_daily_deploy(base, "101-1", datetime(2026, 11, 17, 16, 5, tzinfo=JST))
            self.assertFalse((base / "daily-deploy").exists())

    def test_legacy_same_day_release_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            old = base / "release-100-1"
            old.mkdir()
            state = old / "state.json"
            state.write_text('{"phase":"verified"}')
            timestamp = datetime(2026, 11, 17, 2, 40, tzinfo=JST).timestamp()
            os.utime(old, (timestamp, timestamp))
            os.utime(state, (timestamp, timestamp))
            with self.assertRaisesRegex(ValueError, "Existing release"):
                remote.reserve_daily_deploy(base, "101-1", datetime(2026, 11, 17, 3, 5, tzinfo=JST))

    def test_invalid_release_id_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                remote.reserve_daily_deploy(Path(d), "../bad", datetime(2026, 11, 17, 3, 5, tzinfo=JST))

    def test_symlink_ledger_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            (base / "daily-deploy").symlink_to(base / "elsewhere")
            with self.assertRaises(ValueError):
                remote.reserve_daily_deploy(base, "101-1", datetime(2026, 11, 17, 3, 5, tzinfo=JST))


if __name__ == "__main__":
    unittest.main()
