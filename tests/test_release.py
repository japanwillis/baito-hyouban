import importlib.util
import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('release', BASE / 'scripts/remote-release.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'domain/public_html'
        self.new = self.base / 'candidate'
        for folder in (self.root, self.new):
            folder.mkdir(parents=True)
            for p, text in [('index.html', 'home'), (r.PROTECTED[0], 'approved article'), (r.PROTECTED[1], 'image')]:
                f = folder / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(text)
        (self.root / '.htaccess').write_text('existing server setting')
        (self.new / 'index.html').write_text('new home')
        (self.new / 'guide/second').mkdir()
        (self.new / 'guide/second/index.html').write_text('new approved article')
        self.engine = r.Engine(self.root, self.base / 'private')
        self.before = r.inventory(self.root)

    def apply(self, rid='1-1', checkpoint=None):
        plan = self.engine.plan(self.new, 'a' * 40)
        return self.engine.apply(self.new, 'a' * 40, plan['plan_sha256'], rid, checkpoint)

    def test_plan_is_read_only_and_identifies_diff(self):
        plan = self.engine.plan(self.new, 'a' * 40)
        self.assertEqual(self.before, r.inventory(self.root))
        self.assertEqual(plan['changed'], ['index.html'])
        self.assertEqual(plan['preserved'], ['.htaccess'])

    def test_server_rehearsal_success_and_interruption(self):
        self.assertEqual(r.rehearsal(self.engine.control), 'server-filesystem-rehearsal-passed')

    def test_deploy_backup_finish_and_manual_rollback(self):
        self.apply()
        self.assertEqual(r.inventory(self.base / 'private/release-1-1/backup'), self.before)
        self.assertEqual((self.root / '.htaccess').read_text(), 'existing server setting')
        self.engine.finish('1-1')
        self.engine.rollback('1-1')
        self.assertEqual(r.inventory(self.root), self.before)
        self.assertTrue((self.base / 'private/release-1-1/failed/guide/second/index.html').exists())

    def test_stale_approval_stops_before_backup_or_write(self):
        plan = self.engine.plan(self.new, 'a' * 40)
        (self.root / 'index.html').write_text('concurrent edit')
        current = r.inventory(self.root)
        with self.assertRaisesRegex(ValueError, 'Plan changed'):
            self.engine.apply(self.new, 'a' * 40, plan['plan_sha256'], '1-1')
        self.assertEqual(current, r.inventory(self.root))
        self.assertFalse((self.base / 'private/release-1-1').exists())

    def test_mid_switch_failure_restores_exact_site(self):
        def fail(phase):
            raise RuntimeError('injected failure after first rename')
        with self.assertRaises(RuntimeError):
            self.apply(checkpoint=fail)
        self.assertEqual(self.before, r.inventory(self.root))
        self.assertFalse(self.engine.pending.exists())

    def test_http_failure_can_rollback_before_finish(self):
        self.apply()
        self.engine.rollback('1-1')
        self.assertEqual(self.before, r.inventory(self.root))

    def test_pending_transaction_blocks_second_deploy(self):
        self.apply()
        with self.assertRaisesRegex(ValueError, 'Unfinished'):
            self.engine.plan(self.new, 'a' * 40)

    def test_bh0001_change_and_article_removal_are_rejected(self):
        f = self.new / r.PROTECTED[0]
        f.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'BH-0001'):
            self.engine.plan(self.new, 'a' * 40)
        f.write_text('approved article')
        (self.root / 'old.html').write_text('old page')
        with self.assertRaisesRegex(ValueError, 'Page removal'):
            self.engine.plan(self.new, 'a' * 40)

    def test_bh0001_adsense_header_only_can_be_planned(self):
        protected = r.PROTECTED[0]
        original = b'<html><head>\n<title>Approved article</title></head><body>Protected text</body></html>'
        before = self.root / protected
        candidate = self.new / protected
        before.write_bytes(original)
        candidate.write_bytes(original.replace(
            b'<head>\n', b'<head>\n' + r.ADSENSE_TAG + b'\n'
        ))
        plan = self.engine.plan(self.new, 'a' * 40)
        self.assertIn(protected, plan['changed'])
        candidate.write_bytes(candidate.read_bytes().replace(b'Protected text', b'Altered text'))
        with self.assertRaisesRegex(ValueError, 'BH-0001'):
            self.engine.plan(self.new, 'a' * 40)

    def test_bh0001_rejects_different_adsense_publisher(self):
        protected = r.PROTECTED[0]
        original = b'<html><head>\n<title>Approved article</title></head><body>Protected text</body></html>'
        (self.root / protected).write_bytes(original)
        (self.new / protected).write_bytes(original.replace(
            b'<head>\n', b'<head>\n' +
            r.ADSENSE_TAG.replace(b'8238079237305844', b'0000000000000000') + b'\n'
        ))
        with self.assertRaisesRegex(ValueError, 'BH-0001'):
            self.engine.plan(self.new, 'a' * 40)

    def test_unexpected_edit_refuses_rollback(self):
        self.apply()
        (self.root / 'index.html').write_text('external edit')
        with self.assertRaisesRegex(ValueError, 'Unexpected server edits'):
            self.engine.rollback('1-1')
        self.assertEqual((self.root / 'index.html').read_text(), 'external edit')

    def test_symlink_root_and_member_are_rejected(self):
        link = self.base / 'linked'
        link.symlink_to(self.root)
        with self.assertRaises(ValueError):
            r.Engine(link, self.base / 'control2')
        (self.new / 'leak').symlink_to('/etc/passwd')
        with self.assertRaises(ValueError):
            self.engine.plan(self.new, 'a' * 40)

    def test_traversal_and_symlink_archives_are_rejected(self):
        for i, name in enumerate(['../escape', '/absolute', 'x.php', '.htaccess']):
            archive = self.base / ('bad%d.tar' % i)
            with tarfile.open(archive, 'w') as t:
                m = tarfile.TarInfo(name)
                m.size = 1
                t.addfile(m, io.BytesIO(b'x'))
            with self.assertRaises(ValueError):
                r.unpack(archive, self.base / ('extract%d' % i))

class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # Deliberately copy only the approved public inputs.
        import shutil
        for folder in ('src', 'public', 'ops'):
            shutil.copytree(BASE / folder, self.root / folder)

    def check(self):
        return subprocess.run(['node', str(BASE / 'scripts/content-gate.mjs'), str(self.root)], capture_output=True)

    def test_approved_baseline(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_draft_direct_route_is_rejected(self):
        (self.root / 'src/pages/guide/draft.md').write_text('---\narticleId: BH-0002\n---\nunapproved')
        self.assertNotEqual(self.check().returncode, 0)

    def test_approved_source_edit_is_rejected(self):
        with (self.root / 'src/pages/guide/first-part-time-job.md').open('a') as f:
            f.write('Unreviewed change')
        self.assertNotEqual(self.check().returncode, 0)

    def test_approved_image_edit_is_rejected(self):
        (self.root / 'public/images/BH-0001-eyecatch.webp').write_bytes(b'changed')
        self.assertNotEqual(self.check().returncode, 0)

if __name__ == '__main__':
    unittest.main()
