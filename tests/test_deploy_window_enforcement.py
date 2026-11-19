"""Fail-closed JST deploy-hour regression checks; no GitHub or SSH needed."""
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from scripts.deploy_window import require_deploy_window

JST = ZoneInfo('Asia/Tokyo')

class DeployHourEnforcementTests(unittest.TestCase):
    def test_exact_window_open_and_close(self):
        for t in [(3, 0, 0, 0), (3, 30, 0, 0), (3, 59, 59, 999999)]:
            with self.subTest(t=t):
                self.assertEqual(require_deploy_window('deploy', datetime(2026, 11, 20, *t, tzinfo=JST)), '2026-11-20')

    def test_off_hours_fail_closed(self):
        for hour in (0, 1, 2, 4, 5, 16, 22, 23):
            with self.subTest(hour=hour):
                with self.assertRaisesRegex(ValueError, '03:00'):
                    require_deploy_window('deploy', datetime(2026, 11, 20, hour, tzinfo=JST))

    def test_utc_conversion_and_day_boundary(self):
        self.assertEqual(require_deploy_window('deploy', datetime(2026, 11, 19, 18, 0, tzinfo=timezone.utc)), '2026-11-20')
        with self.assertRaises(ValueError):
            require_deploy_window('deploy', datetime(2026, 11, 19, 17, 59, 59, tzinfo=timezone.utc))
        with self.assertRaises(ValueError):
            require_deploy_window('deploy', datetime(2026, 11, 19, 19, 0, tzinfo=timezone.utc))

    def test_naive_time_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'timezone'):
            require_deploy_window('deploy', datetime(2026, 11, 20, 3, 0))

    def test_plan_and_rollback_unrestricted(self):
        for mode in ('plan', 'rollback'):
            self.assertIsNone(require_deploy_window(mode, datetime(2026, 11, 20, 22, tzinfo=JST)))

if __name__ == '__main__':
    unittest.main()
