import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, BASE / 'scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

request = module('request', 'release-request.py')
remote = module('remote', 'remote-release.py')
controller = module('controller', 'release-controller.py')

class ConnectorRequestTests(unittest.TestCase):
    def plan(self):
        return dict(schema_version=1, request_id='plan-20261104-a', mode='plan', source_sha='a' * 40)

    def test_plan_accepts_request_only_diff(self):
        self.assertEqual(request.validate(self.plan(), [request.REQUEST_PATH])['mode'], 'plan')

    def test_code_change_after_plan_is_rejected(self):
        with self.assertRaises(ValueError):
            request.validate(self.plan(), [request.REQUEST_PATH, 'src/pages/index.astro'])

    def test_auto_mode_and_output_injection_are_rejected(self):
        for value in ('auto', 'deploy\nsource_sha=bad'):
            p = self.plan()
            p['mode'] = value
            with self.assertRaises(ValueError):
                request.validate(p, [])

    def test_deploy_requires_plan_and_exact_approval(self):
        p = self.plan()
        p.update(mode='deploy')
        with self.assertRaises(ValueError):
            request.validate(p, [])
        p.update(plan_id='123-1', plan_sha256='b' * 64, approval='DEPLOY ' + 'a' * 40 + ' ' + 'b' * 64)
        self.assertEqual(request.validate(p, [request.REQUEST_PATH])['mode'], 'deploy')

    def test_real_git_request_commit_path(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def git(*args):
                return subprocess.check_output(['git', '-C', d, *args], text=True).strip()
            git('init', '-q')
            git('config', 'user.name', 'Request test')
            git('config', 'user.email', 'request-test@example.invalid')
            (root / 'code.txt').write_text('approved code')
            git('add', '.')
            git('commit', '-qm', 'approved source')
            source = git('rev-parse', 'HEAD')
            (root / 'ops').mkdir()
            p = self.plan()
            p['source_sha'] = source
            (root / request.REQUEST_PATH).write_text(json.dumps(p))
            git('add', '.')
            git('commit', '-qm', 'explicit plan request')
            trigger = git('rev-parse', 'HEAD')
            event = root / 'event.json'
            event.write_text(json.dumps(dict(before=source, after=trigger, deleted=False, forced=False)))
            output = root / 'output'
            env = dict(os.environ, GITHUB_REF='refs/heads/main', GITHUB_SHA=trigger,
                       GITHUB_EVENT_NAME='push', GITHUB_EVENT_PATH=str(event), GITHUB_OUTPUT=str(output))
            run = subprocess.run(['python3', str(BASE / 'scripts/release-request.py')], cwd=d, env=env, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr.decode())
            self.assertIn('source_sha=' + source, output.read_text())
            event.write_text(json.dumps(dict(before=source, after=trigger, deleted=False, forced=True)))
            run = subprocess.run(['python3', str(BASE / 'scripts/release-request.py')], cwd=d, env=env, capture_output=True)
            self.assertNotEqual(run.returncode, 0)

    def test_failed_actions_run_cannot_authorize_deploy(self):
        class Response:
            def __enter__(self):
                import io
                return io.StringIO(json.dumps(dict(status='completed', conclusion='failure', run_attempt=1,
                    head_branch='main', path='.github/workflows/continuous-release.yml')))
            def __exit__(self, *args):
                pass
        with patch.object(controller.urllib.request, 'urlopen', return_value=Response()):
            with self.assertRaisesRegex(ValueError, 'not succeeded'):
                controller.verify_successful_plan_run('123-1', 'owner/repo', 'test-token')

class ServerProofTests(unittest.TestCase):
    def test_backup_and_recovery_proof_before_apply(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root, candidate = base / 'domain/public_html', base / 'candidate'
            for directory in (root, candidate):
                for filename in ('index.html',) + remote.PROTECTED:
                    p = directory / filename
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text('baseline')
            (candidate / 'index.html').write_text('updated')
            engine = remote.Engine(root, base / 'control')
            before = remote.inventory(root)
            with self.assertRaises(FileNotFoundError):
                engine.require_plan(candidate, 'a' * 40, 'b' * 64, '100-1')
            result = engine.verified_plan(candidate, 'a' * 40, '100-1')
            self.assertTrue(all(result['checks'].values()))
            self.assertEqual(remote.inventory(root), before)
            engine.require_plan(candidate, 'a' * 40, result['plan_sha256'], '100-1')
            backup = base / 'control/plan-100-1/backup/index.html'
            backup.write_text('damaged backup')
            with self.assertRaisesRegex(ValueError, 'backup'):
                engine.require_plan(candidate, 'a' * 40, result['plan_sha256'], '100-1')

    def test_failed_proof_and_server_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root, candidate = base / 'domain/public_html', base / 'candidate'
            for directory in (root, candidate):
                for filename in ('index.html',) + remote.PROTECTED:
                    p = directory / filename
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text('baseline')
            engine = remote.Engine(root, base / 'control')
            result = engine.verified_plan(candidate, 'a' * 40, '100-1')
            receipt = base / 'control/plan-100-1/receipt.json'
            broken = dict(result, checks=dict(result['checks'], isolated_recovery_verified=False))
            remote.write_json(receipt, broken)
            with self.assertRaisesRegex(ValueError, 'proof'):
                engine.require_plan(candidate, 'a' * 40, result['plan_sha256'], '100-1')
            remote.write_json(receipt, result)
            (root / 'index.html').write_text('concurrent change')
            with self.assertRaisesRegex(ValueError, 'changed after plan'):
                engine.require_plan(candidate, 'a' * 40, result['plan_sha256'], '100-1')
