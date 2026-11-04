"""Server-side deployment engine. No secrets, third-party dependencies or recursive deletion.

CLI always uses the single verified domain root and a private sibling control directory.
The Engine constructor is separately usable with temporary directories in tests.
"""
import fcntl
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

PROTECTED = ('guide/first-part-time-job/index.html', 'images/BH-0001-eyecatch.webp')
# The publisher-authorized global AdSense code is the sole allowed modification
# to the protected BH-0001 HTML. All underlying article bytes remain unchanged.
ADSENSE_TAG = b'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-8238079237305844" crossorigin="anonymous"></script>'

def approved_adsense_header_only(root, candidate):
    original = (root / PROTECTED[0]).read_bytes()
    updated = (candidate / PROTECTED[0]).read_bytes()
    if updated.count(ADSENSE_TAG) != 1:
        return False
    start, end = updated.find(b'<head>'), updated.find(b'</head>')
    where = updated.find(ADSENSE_TAG)
    if not (start >= 0 and start < where < end):
        return False
    # Explicitly allow one script line immediately after <head>, not article edits.
    return updated.replace(ADSENSE_TAG, b'', 1) == original

def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()

def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def inventory(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Missing or symbolic root')
    result = {}
    for p in sorted(root.rglob('*')):
        s = p.lstat()
        if stat.S_ISLNK(s.st_mode) or not (stat.S_ISREG(s.st_mode) or stat.S_ISDIR(s.st_mode)):
            raise ValueError('Links and special files refused')
        if p.is_file():
            result[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result

def write_json(path, value):
    tmp = path.with_suffix('.tmp')
    tmp.write_bytes(canonical(value))
    os.replace(str(tmp), str(path))

class Engine:
    def __init__(self, root, control):
        self.root, self.control = Path(root), Path(control)
        for p in [self.root, self.control]:
            for ancestor in [p] + list(p.parents):
                if ancestor.is_symlink():
                    raise ValueError('Symbolic directory refused')
        self.control.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(str(self.control), 0o700)
        if self.root.parent.stat().st_dev != self.control.stat().st_dev:
            raise ValueError('Root and staging must be on the same filesystem')
        self.pending = self.control / 'pending.json'

    def plan(self, candidate, source_sha):
        if self.pending.exists():
            raise ValueError('Unfinished transaction; rollback required')
        before, proposed = inventory(self.root), inventory(candidate)
        if not before or 'index.html' not in before:
            raise ValueError('Existing site required; initial deployment forbidden')
        for p in PROTECTED:
            if p not in before or p not in proposed:
                raise ValueError('Protected BH-0001 asset missing: ' + p)
            if proposed[p] != before[p]:
                if p != PROTECTED[0] or not approved_adsense_header_only(self.root, candidate):
                    raise ValueError('BH-0001 content/image must remain byte-identical: ' + p)
        # Article removal is a separate, explicitly reviewed operation. Old hashed assets
        # and unknown server files remain intact, including any server configuration.
        removed_html = [p for p in before if p.endswith('.html') and p not in proposed]
        if removed_html:
            raise ValueError('Page removal refused: ' + ', '.join(removed_html))
        added = sorted(set(proposed) - set(before))
        changed = sorted(p for p in proposed if p in before and proposed[p] != before[p])
        kept = sorted(set(before) - set(proposed))
        data = dict(source_sha=source_sha, before=before, candidate=proposed,
                    added=added, changed=changed, preserved=kept)
        return dict(data, plan_sha256=digest(data))

    def apply(self, candidate, source_sha, approved_digest, release_id, checkpoint=None):
        if not re.fullmatch(r'[0-9]+-[0-9]+', release_id):
            raise ValueError('Invalid release ID')
        plan = self.plan(candidate, source_sha)
        if plan['plan_sha256'] != approved_digest:
            raise ValueError('Plan changed since approval; no write performed')
        if not plan['added'] and not plan['changed']:
            raise ValueError('No changes to publish')
        target = self.control / ('release-' + release_id)
        target.mkdir(mode=0o700)  # Never reuse a release/backup ID.
        backup, staged, retired = [target / x for x in ('backup', 'staged', 'retired')]
        shutil.copytree(str(self.root), str(backup), copy_function=shutil.copy2)
        if inventory(backup) != plan['before'] or inventory(self.root) != plan['before']:
            raise ValueError('Backup mismatch or concurrent server edit')
        shutil.copytree(str(backup), str(staged), copy_function=shutil.copy2)
        for p in sorted(plan['candidate']):
            destination = staged / p
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(Path(candidate) / p), str(destination))
        expected = dict(plan['before'], **plan['candidate'])
        if inventory(staged) != expected:
            raise ValueError('Staging verification failed')
        state = dict(release_id=release_id, source_sha=source_sha, before=plan['before'],
                     after=expected, candidate=plan['candidate'], phase='prepared')
        write_json(target / 'state.json', state)
        write_json(self.pending, state)  # Durable recovery point before either rename.
        try:
            if inventory(self.root) != plan['before']:
                raise ValueError('Concurrent server edit')
            os.rename(str(self.root), str(retired))
            if checkpoint:
                checkpoint('root-moved')
            os.rename(str(staged), str(self.root))
            if inventory(self.root) != expected:
                raise ValueError('Published file verification failed')
            state['phase'] = 'awaiting-https'
            write_json(target / 'state.json', state)
            write_json(self.pending, state)
        except BaseException:
            self.rollback(release_id)
            raise
        return state

    def verified_plan(self, candidate, source_sha, plan_id):
        if not re.fullmatch(r'[0-9]+-[0-9]+', plan_id):
            raise ValueError('Invalid plan ID')
        plan = self.plan(candidate, source_sha)
        rehearsal(self.control)
        target = self.control / ('plan-' + plan_id)
        target.mkdir(mode=0o700)
        backup = target / 'backup'
        shutil.copytree(str(self.root), str(backup), copy_function=shutil.copy2)
        if inventory(backup) != plan['before'] or inventory(self.root) != plan['before']:
            raise ValueError('Plan backup mismatch or concurrent server edit')
        result = dict(plan, plan_id=plan_id, checks={'diff_verified': True,
                      'production_backup_verified': True, 'isolated_recovery_verified': True})
        write_json(target / 'receipt.json', result)
        return result

    def require_plan(self, candidate, source_sha, approved_digest, plan_id):
        if not re.fullmatch(r'[0-9]+-[0-9]+', plan_id):
            raise ValueError('Verified plan ID is required')
        target = self.control / ('plan-' + plan_id)
        receipt = json.loads((target / 'receipt.json').read_text())
        checks = receipt.get('checks', {})
        if (receipt.get('source_sha') != source_sha or receipt.get('plan_sha256') != approved_digest or
            any(checks.get(k) is not True for k in ('diff_verified', 'production_backup_verified', 'isolated_recovery_verified'))):
            raise ValueError('Successful diff, backup and recovery proof required')
        if inventory(target / 'backup') != receipt['before']:
            raise ValueError('Plan backup no longer matches')
        if self.plan(candidate, source_sha)['plan_sha256'] != approved_digest:
            raise ValueError('Source, candidate or production changed after plan')
        return receipt

    def finish(self, release_id):
        state = self._state(release_id)
        if state['phase'] != 'awaiting-https' or inventory(self.root) != state['after']:
            raise ValueError('Cannot finish an unverified transaction')
        state['phase'] = 'verified'
        write_json(self.control / ('release-' + release_id) / 'state.json', state)
        write_json(self.control / 'active.json', state)
        self.pending.unlink()
        return state

    def _state(self, release_id):
        if not re.fullmatch(r'[0-9]+-[0-9]+', release_id):
            raise ValueError('Invalid backup ID')
        path = self.control / ('release-' + release_id) / 'state.json'
        state = json.loads(path.read_text())
        if self.pending.exists():
            if json.loads(self.pending.read_text())['release_id'] != release_id:
                raise ValueError('Another transaction is pending')
        elif (not (self.control / 'active.json').exists() or
              json.loads((self.control / 'active.json').read_text())['release_id'] != release_id):
            raise ValueError('Only latest active release can be rolled back')
        return state

    def rollback(self, release_id):
        state = self._state(release_id)
        target = self.control / ('release-' + release_id)
        backup, recovery = target / 'backup', target / 'recovery'
        if inventory(backup) != state['before']:
            raise ValueError('Backup integrity failed; manual recovery required')
        if self.root.exists() and inventory(self.root) not in (state['before'], state['after']):
            raise ValueError('Unexpected server edits; refusing rollback overwrite')
        if recovery.exists():
            raise ValueError('Recovery already exists; manual inspection required')
        shutil.copytree(str(backup), str(recovery), copy_function=shutil.copy2)
        # Keep the failed version outside public_html; never delete an unknown tree.
        if self.root.exists():
            os.rename(str(self.root), str(target / 'failed'))
        os.rename(str(recovery), str(self.root))
        if inventory(self.root) != state['before']:
            raise ValueError('Rollback verification failed')
        state['phase'] = 'rolled-back'
        write_json(target / 'state.json', state)
        if self.pending.exists():
            self.pending.unlink()
        active = self.control / 'active.json'
        if active.exists() and json.loads(active.read_text())['release_id'] == release_id:
            active.unlink()
        return state

def rehearsal(control):
    # Exercise success and interruption on the server filesystem, outside public_html.
    with tempfile.TemporaryDirectory(prefix='rehearsal-', dir=str(control)) as folder:
        base = Path(folder)
        root, candidate = base / 'domain/public_html', base / 'candidate'
        for directory in (root, candidate):
            directory.mkdir(parents=True)
            for name in ('index.html',) + PROTECTED:
                file = directory / name
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('baseline')
        (candidate / 'index.html').write_text('updated')
        engine = Engine(root, base / 'control')
        before = inventory(root)
        plan = engine.plan(candidate, 'a' * 40)
        engine.apply(candidate, 'a' * 40, plan['plan_sha256'], '1-1')
        engine.finish('1-1')
        engine.rollback('1-1')
        if inventory(root) != before:
            raise ValueError('Rehearsal rollback failed')
        def fail(phase):
            raise RuntimeError('rehearsal interruption')
        try:
            plan = engine.plan(candidate, 'a' * 40)
            engine.apply(candidate, 'a' * 40, plan['plan_sha256'], '2-1', fail)
        except RuntimeError:
            pass
        else:
            raise ValueError('Rehearsal did not interrupt')
        if inventory(root) != before or engine.pending.exists():
            raise ValueError('Rehearsal interruption recovery failed')
    return 'server-filesystem-rehearsal-passed'

def unpack(archive, destination):
    destination.mkdir(mode=0o700)
    with tarfile.open(str(archive), 'r:') as t:
        members = t.getmembers()
        if len(members) > 10000 or sum(x.size for x in members) > 256 * 1024 * 1024:
            raise ValueError('Release too large')
        seen = set()
        for m in members:
            p = PurePosixPath(m.name)
            if (not m.isfile() or p.is_absolute() or not p.parts or
                any(x in ('.', '..') or x.startswith('.') for x in p.parts) or
                p.as_posix() in seen or not re.fullmatch(r'[A-Za-z0-9_./-]+', m.name)):
                raise ValueError('Unsafe archive member')
            seen.add(p.as_posix())
            if p.suffix.lower() not in ('.html', '.css', '.js', '.json', '.webp', '.png', '.jpg', '.svg', '.ico', '.xml', '.txt', '.woff', '.woff2'):
                raise ValueError('Non-static file refused')
        for m in members:
            out = destination / m.name
            out.parent.mkdir(parents=True, exist_ok=True)
            with t.extractfile(m) as stream, out.open('wb') as f:
                shutil.copyfileobj(stream, f)
            out.chmod(0o644)

def main():
    mode, release_id, source_sha, approved, plan_id = sys.argv[1:]
    if not re.fullmatch(r'[0-9]+-[0-9]+', release_id) or not re.fullmatch(r'[a-f0-9]{40}', source_sha):
        raise ValueError('Invalid release ID or commit')
    home = Path.home()
    engine = Engine(home / 'baito-hyouban.com/public_html', home / '.baito-hyouban-deploy')
    with (engine.control / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if mode in ('plan', 'apply'):
            candidate = engine.control / ('incoming-' + release_id)
            unpack(engine.control / (release_id + '.tar'), candidate)
            if mode == 'plan':
                result = engine.verified_plan(candidate, source_sha, release_id)
            else:
                engine.require_plan(candidate, source_sha, approved, plan_id)
                result = engine.apply(candidate, source_sha, approved, release_id)
        elif mode == 'rollback':
            result = engine.rollback(release_id)
        elif mode == 'finish':
            result = engine.finish(release_id)
        else:
            raise ValueError('Invalid operation')
        print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
