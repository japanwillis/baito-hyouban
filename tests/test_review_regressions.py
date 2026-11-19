import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from scripts.github_deploy_audit import audit_daily_releases
NOW=datetime(2026,11,18,3,5,tzinfo=ZoneInfo('Asia/Tokyo'))
class ReviewTests(unittest.TestCase):
    def audit(self,runs,jobs=None,current='999'):
        def api(path,*_):
            return {'total_count':len(runs),'workflow_runs':runs} if path.startswith('/actions/runs?') else {'jobs':jobs}
        return audit_daily_releases('owner/repo','dummy',current,now=NOW,get_json=api,
          get_log=lambda *_:'Validated explicit request: valid-request deploy '+ 'a'*40)
    def test_current_run_rerun_must_not_hide_prior_attempt(self):
        run={'id':101,'path':'.github/workflows/continuous-release.yml','name':'publish',
             'created_at':'2026-11-17T18:00:00Z','status':'in_progress','run_attempt':2}
        with self.assertRaises(ValueError):self.audit([run],current='101')
    def test_missing_completion_timestamps_must_fail_closed(self):
        run={'id':101,'path':'.github/workflows/continuous-release.yml','name':'publish',
             'created_at':'2026-11-16T18:00:00Z','updated_at':'2026-11-17T18:00:00Z',
             'run_started_at':'2026-11-17T18:00:00Z','status':'completed'}
        jobs=[{'id':200,'name':'request','status':'completed'},
              {'id':201,'name':'release','status':'completed','started_at':None,'completed_at':None}]
        with self.assertRaises(ValueError):self.audit([run],jobs)
    def test_partial_history_must_not_be_empty_success(self):
        with self.assertRaises(ValueError):
            audit_daily_releases('owner/repo','dummy','999',now=NOW,
                get_json=lambda *_:{'total_count':1,'workflow_runs':[]},get_log=lambda *_:'')
