import importlib.util
import io
import json
import os
import tempfile
import unittest
import urllib.request
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo
from scripts.github_deploy_audit import audit_daily_releases, TokenFreeLogRedirect, NoRedirect
ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
remote=load('hard_remote','remote-release.py')
request=load('hard_request','release-request.py')
NOW=datetime(2026,11,18,3,5,tzinfo=ZoneInfo('Asia/Tokyo'))

class AuditHardeningTests(unittest.TestCase):
    def test_old_created_run_rerun_today_is_not_filtered(self):
        run=dict(id=101,path='.github/workflows/continuous-release.yml',name='publish',status='completed',
                 created_at='2026-10-01T01:00:00Z',updated_at='2026-11-17T18:02:00Z',run_started_at='2026-11-17T18:00:00Z')
        def api(path,*_):
            self.assertNotIn('created=',path)
            if '/jobs?' not in path:return {'total_count':1,'workflow_runs':[run]}
            return {'jobs':[{'id':200,'name':'request'},{'id':201,'name':'release','status':'completed',
              'started_at':'2026-11-17T18:01:00Z','completed_at':'2026-11-17T18:02:00Z'}]}
        with self.assertRaisesRegex(ValueError,'Another deploy attempt'):
            audit_daily_releases('owner/repo','dummy','999',NOW,get_json=api,
              get_log=lambda *_:'Validated explicit request: deploy-request deploy '+ 'a'*40)
    def test_provably_old_completed_initial_publish_needs_no_expired_logs(self):
        run=dict(id=101,path='.github/workflows/initial-publish-xserver.yml',name='Initial publish',status='completed',
                 created_at='2026-10-01T01:00:00Z',updated_at='2026-10-01T01:02:00Z',run_started_at='2026-10-01T01:00:00Z')
        self.assertEqual(audit_daily_releases('owner/repo','dummy','999',NOW,
            get_json=lambda *_:{'total_count':1,'workflow_runs':[run]},
            get_log=lambda *_:self.fail('Old logs must not be requested')),1)
    def test_redirect_drops_credentials_and_cookies(self):
        original=urllib.request.Request('https://api.github.com/repos/o/r/actions/jobs/1/logs',
            headers={'Authorization':'Bearer dummy','Cookie':'secret-cookie','User-Agent':'test'})
        redirected=TokenFreeLogRedirect().redirect_request(original,None,302,'',{},'https://logs.example/signed?sig=test')
        self.assertFalse(redirected.has_header('Authorization'));self.assertFalse(redirected.has_header('Cookie'))
        self.assertEqual(redirected.full_url,'https://logs.example/signed?sig=test')
    def test_unsafe_redirects_refused(self):
        original=urllib.request.Request('https://api.github.com')
        for dest in ('http://logs.example','https://user:pass@logs.example','https://logs.example:444','file:///tmp/log'):
            with self.assertRaises(ValueError):TokenFreeLogRedirect().redirect_request(original,None,302,'',{},dest)
        with self.assertRaises(ValueError):NoRedirect().redirect_request(original,None,302,'',{},'https://api.github.com/new')
    def test_missing_lifecycle_timestamp_fails_closed(self):
        run=dict(id=101,path='.github/workflows/continuous-release.yml',name='publish',status='completed',created_at='2026-10-01T01:00:00Z')
        with self.assertRaises(ValueError):
            audit_daily_releases('owner/repo','dummy','999',NOW,
                get_json=lambda *_:{'total_count':1,'workflow_runs':[run]},get_log=lambda *_:'')

class DurableLedgerTests(unittest.TestCase):
    def test_receipt_and_directories_fsynced(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(remote.os,'fsync',wraps=os.fsync) as sync:
                receipt=remote.reserve_daily_deploy(Path(d),'123-1',NOW)
                self.assertTrue(receipt.is_file());self.assertGreaterEqual(sync.call_count,4)
    def test_fsync_failure_never_grants_reservation(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(remote.os,'fsync',side_effect=OSError('disk sync failed')):
                with self.assertRaises(OSError):remote.reserve_daily_deploy(Path(d),'123-1',NOW)
    def test_receipt_failure_leaves_day_consumed(self):
        with tempfile.TemporaryDirectory() as d:
            with patch.object(remote,'write_json',side_effect=OSError('crash')):
                with self.assertRaises(OSError):remote.reserve_daily_deploy(Path(d),'123-1',NOW)
            with self.assertRaisesRegex(ValueError,'already reserved'):remote.reserve_daily_deploy(Path(d),'124-1',NOW)

class RequestGateTests(unittest.TestCase):
    def test_failed_api_audit_produces_no_release_outputs(self):
        sha='a'*40;digest='b'*64
        with tempfile.TemporaryDirectory() as d:
            event=Path(d)/'event.json';output=Path(d)/'output'
            event.write_text(json.dumps({'inputs':dict(mode='deploy',source_sha=sha,plan_id='123-1',plan_sha256=digest,approval='DEPLOY '+sha+' '+digest)}))
            env=dict(GITHUB_REF='refs/heads/main',GITHUB_SHA=sha,GITHUB_EVENT_PATH=str(event),GITHUB_OUTPUT=str(output),
                     GITHUB_EVENT_NAME='workflow_dispatch',GITHUB_RUN_ID='999',GITHUB_REPOSITORY='owner/repo',GH_READ_TOKEN='dummy')
            with patch.dict(os.environ,env),patch.object(request,'git',side_effect=[sha,'']), \
                 patch.object(request.subprocess,'run'), \
                 patch.object(request,'audit_daily_releases',side_effect=ValueError('audit failed')) as audit:
                with self.assertRaisesRegex(ValueError,'audit failed'):request.main()
                audit.assert_called_once_with('owner/repo','dummy','999')
                self.assertFalse(output.exists())
    def test_workflow_request_has_read_only_audit_token_no_server_secrets(self):
        text=(ROOT/'.github/workflows/continuous-release.yml').read_text().split('  release:')[0]
        self.assertIn('actions: read',text);self.assertIn('GH_READ_TOKEN:',text)
        self.assertNotIn('secrets.',text);self.assertNotIn('contents: write',text)
