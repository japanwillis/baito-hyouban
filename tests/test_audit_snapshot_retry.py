import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from scripts.github_deploy_audit import audit_daily_releases

NOW = datetime(2026, 11, 17, 18, 40, tzinfo=timezone.utc)

class SnapshotRetryTests(unittest.TestCase):
    def run_audit(self, api, log=None):
        return audit_daily_releases('owner/repo', 'dummy', '999', NOW,
                                    get_json=api, get_log=log or (lambda *_: ''))

    def changing_then_stable(self, inserted=None):
        calls = []
        old = [{'id': n, 'name': 'Verify build'} for n in range(1, 101)]
        stable = ([inserted] if inserted else []) + old
        def api(path, *_):
            calls.append(path)
            if len(calls) == 1:
                return {'total_count': 101, 'workflow_runs': old}
            if len(calls) == 2:
                return {'total_count': 102, 'workflow_runs': [{'id': 102}]}
            if '/jobs?' in path:
                return {'jobs': [{'name': 'request', 'id': 300},
                                 {'name': 'release', 'id': 301,
                                  'started_at': NOW.isoformat(), 'completed_at': NOW.isoformat()}]}
            page = int(path.rsplit('=', 1)[1])
            return {'total_count': len(stable), 'workflow_runs': stable[(page-1)*100:page*100]}
        return api, calls

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_unrelated_qa_churn_restarts_from_page_one(self, sleep):
        api, calls = self.changing_then_stable()
        self.assertEqual(self.run_audit(api), 0)
        self.assertEqual(calls[2], '/actions/runs?per_page=100&page=1')
        sleep.assert_called_once_with(2)

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_new_parallel_publisher_is_not_lost_on_retry(self, sleep):
        api, calls = self.changing_then_stable(dict(id=102, name='publish', status='in_progress', created_at=NOW.isoformat()))
        with self.assertRaisesRegex(ValueError, 'still active'):
            self.run_audit(api)
        sleep.assert_called_once_with(2)

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_new_same_day_deploy_is_not_lost_on_retry(self, sleep):
        api, _ = self.changing_then_stable(dict(id=102, name='publish', status='completed',
            created_at=NOW.isoformat(), updated_at=NOW.isoformat(), run_started_at=NOW.isoformat()))
        with self.assertRaisesRegex(ValueError, 'Another deploy attempt'):
            self.run_audit(api, lambda *_: 'Validated explicit request: reviewed-deploy deploy ' + 'a'*40)
        sleep.assert_called_once_with(2)

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_persistent_churn_is_bounded_and_fails_closed(self, sleep):
        calls = []
        def api(path, *_):
            calls.append(path)
            return {'total_count': 101 if len(calls)%2 else 102,
                    'workflow_runs': [{'id': n} for n in range(100)]}
        with self.assertRaisesRegex(ValueError, 'history changed'):
            self.run_audit(api)
        self.assertEqual(len(calls), 6)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4])

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_api_failure_is_not_retried(self, sleep):
        with self.assertRaisesRegex(ValueError, 'OSError'):
            self.run_audit(unittest.mock.Mock(side_effect=OSError('not available')))
        sleep.assert_not_called()

    @patch('scripts.github_deploy_audit.time.sleep')
    def test_ambiguous_failed_request_remains_blocked(self, sleep):
        run=dict(id=102, name='publish', status='completed', created_at=NOW.isoformat(),
                 updated_at=NOW.isoformat(), run_started_at=NOW.isoformat())
        def api(path, *_):
            if '/jobs?' in path: return {'jobs': [{'id': 300, 'name': 'request', 'conclusion': 'failure'},
                                               {'id': 301, 'name': 'release', 'conclusion': 'skipped'}]}
            return {'total_count': 1, 'workflow_runs': [run]}
        with self.assertRaisesRegex(ValueError, 'could not be proven'):
            self.run_audit(api)
        sleep.assert_not_called()
