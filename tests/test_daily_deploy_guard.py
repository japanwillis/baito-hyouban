"""Regression tests for the proposed JST date handling and server ledger."""
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts.deploy_window import deploy_jst_date

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("remote_release_guard", BASE / "scripts/remote-release.py")
remote = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remote)
JST = ZoneInfo("Asia/Tokyo")


class DeployDateTests(unittest.TestCase):
    def test_first_deploy_at_three_allowed(self):
        self.assertEqual(deploy_jst_date("deploy", datetime(2026, 11, 17, 3, 0, tzinfo=JST)), "2026-11-17")

    def test_deploy_allowed_outside_the_previous_window(self):
        for hour in (0, 2, 3, 4, 16, 23):
            with self.subTest(hour=hour):
                self.assertEqual(deploy_jst_date("deploy", datetime(2026, 11, 17, hour, 0, tzinfo=JST)), "2026-11-17")

    def test_jst_midnight_boundary_and_utc(self):
        utc = ZoneInfo("UTC")
        self.assertEqual(deploy_jst_date("deploy", datetime(2026, 11, 16, 14, 59, tzinfo=utc)), "2026-11-16")
        self.assertEqual(deploy_jst_date("deploy", datetime(2026, 11, 16, 15, 0, tzinfo=utc)), "2026-11-17")

    def test_plan_and_rollback_not_blocked_by_window(self):
        for mode in ("plan", "rollback"):
            self.assertIsNone(deploy_jst_date(mode, datetime(2026, 11, 17, 16, 0, tzinfo=JST)))

    def test_naive_clock_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            deploy_jst_date("deploy", datetime(2026, 11, 17, 3, 0))


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

    def test_server_accepts_explicit_deploy_outside_scheduled_window(self):
        for hour in (0, 2, 4, 16, 23):
            with self.subTest(hour=hour), tempfile.TemporaryDirectory() as d:
                receipt = remote.reserve_daily_deploy(Path(d), "101-1", datetime(2026, 11, 17, hour, 5, tzinfo=JST))
                self.assertEqual(json.loads(receipt.read_text())["date_jst"], "2026-11-17")
                with self.assertRaisesRegex(ValueError, "already"):
                    remote.reserve_daily_deploy(Path(d), "102-1", datetime(2026, 11, 17, hour, 6, tzinfo=JST))

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
