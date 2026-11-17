"""GitHub runner: pinned SSH, manual approval, HTTPS hash checks, rollback on failure."""
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

# GitHub invokes these entrypoints by path, not as modules.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.deploy_window import require_deploy_window
from scripts.github_deploy_audit import audit_daily_releases

HOST_FP = 'SHA256:VBukSLflrITK4l8kOHlHhvV5YrpzMEtiwOJO8uMYKY8'
BASE = 'https://baito-hyouban.com'

def preserve_bh0001_live_html(dist):
    """Keep the protected first article byte-for-byte identical across unrelated releases.

    Astro may assign a different shared CSS asset name when new articles are added.
    The content approval gate has already validated the article source and image;
    this operation prevents re-rendering of the protected published HTML. The
    server-side release engine independently verifies equality with its disk copy.
    """
    target = Path(dist) / 'guide/first-part-time-job/index.html'
    if not target.is_file() or target.is_symlink():
        raise ValueError('Protected article build output missing or unsafe')
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args):
            return None
    request = urllib.request.Request(
        BASE + '/guide/first-part-time-job/',
        headers={'Cache-Control': 'no-cache', 'Accept-Encoding': 'identity'})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError('Protected live article is unavailable')
        original = response.read(2_000_001)
    if len(original) < 500 or len(original) > 2_000_000 or b'<html' not in original.lower():
        raise ValueError('Unexpected protected live article bytes')
    if target.read_bytes() != original:
        target.write_bytes(original)
        print('Preserved protected BH-0001 live HTML verbatim; server plan will verify disk match')
    return hashlib.sha256(original).hexdigest()


def verify_successful_plan_run(plan_id, repository, token):
    if not re.fullmatch(r'[0-9]+-[0-9]+', plan_id) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid plan reference')
    if not token:
        raise ValueError('Read-only Actions token required')
    run_id, attempt = plan_id.split('-')
    req = urllib.request.Request('https://api.github.com/repos/' + repository + '/actions/runs/' + run_id,
          headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json'})
    # Fixed GitHub API destination; credentials never appear in request logs/output.
    with urllib.request.urlopen(req, timeout=30) as response:
        run = json.load(response)
    if (run.get('status') != 'completed' or run.get('conclusion') != 'success' or
        str(run.get('run_attempt')) != attempt or run.get('head_branch') != 'main' or
        run.get('path') != '.github/workflows/continuous-release.yml'):
        raise ValueError('The referenced plan workflow has not succeeded')

def public_verify(manifest):
    # Verify EVERY changed/new file and all public HTML entrypoints. Requests do not
    # follow redirects, so a redirect or soft error cannot count as a successful release.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args):
            return None
    client = urllib.request.build_opener(NoRedirect)
    for p, expected in sorted(manifest.items()):
        if any(part.startswith('.') for part in p.split('/')):
            continue  # Private/server configuration is verified on disk, never requested.
        url = BASE + '/' + p
        if p == 'index.html':
            url = BASE + '/'
        elif p.endswith('/index.html'):
            url = BASE + '/' + p[:-10]
        req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
        with client.open(req, timeout=30) as response:
            if response.status != 200 or hashlib.sha256(response.read()).hexdigest() != expected:
                raise ValueError('HTTPS content hash mismatch: ' + url)
        print('Verified HTTPS:', url)

def main():
    mode = os.environ['RELEASE_MODE']
    sha = os.environ['RELEASE_SHA']
    approval = os.environ.get('RELEASE_APPROVAL', '')
    plan_digest = os.environ.get('PLAN_SHA256', '')
    plan_id = os.environ.get('PLAN_ID', '')
    current_id = os.environ['GITHUB_RUN_ID'] + '-' + os.environ['GITHUB_RUN_ATTEMPT']
    backup_id = os.environ.get('BACKUP_ID', '')
    if mode not in ('plan', 'deploy', 'rollback') or not re.fullmatch(r'[a-f0-9]{40}', sha):
        raise ValueError('Invalid mode or SHA')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    if head != sha or os.environ['GITHUB_REF'] != 'refs/heads/main':
        raise ValueError('Only the exact requested main commit can run')
    if mode == 'deploy' and (not re.fullmatch(r'[a-f0-9]{64}', plan_digest) or
        approval != 'DEPLOY ' + sha + ' ' + plan_digest):
        raise ValueError('Explicit approval of commit and plan required')
    if mode == 'deploy':
        # Recheck immediately before any SSH setup or server-side operations.
        require_deploy_window(mode)
        audit_daily_releases(os.environ.get('GITHUB_REPOSITORY', ''),
                             os.environ.get('GH_READ_TOKEN', ''),
                             os.environ.get('GITHUB_RUN_ID', ''))
        verify_successful_plan_run(plan_id, os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GH_READ_TOKEN', ''))
    if mode == 'rollback' and (not re.fullmatch(r'[0-9]+-[0-9]+', backup_id) or approval != 'ROLLBACK ' + backup_id):
        raise ValueError('Explicit approval of backup ID required')
    host, user, port = [os.environ.get('XSERVER_' + n, '') for n in ('HOST', 'USER', 'PORT')]
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9.-]*', host) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', user) or not re.fullmatch(r'[0-9]{1,5}', port):
        raise ValueError('Invalid server settings')
    if not 1 <= int(port) <= 65535:
        raise ValueError('Invalid port')
    key = os.environ.pop('XSERVER_KEY', '')
    if not key:
        raise ValueError('Missing SSH identity')
    os.umask(0o077)
    Path('release-evidence').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='bh-ssh-') as d:
        temp = Path(d)
        known = temp / 'known_hosts'
        known.write_bytes(subprocess.check_output(['ssh-keyscan', '-T', '12', '-p', port, '-t', 'ed25519', host], stderr=subprocess.DEVNULL))
        lines = subprocess.check_output(['ssh-keygen', '-lf', str(known), '-E', 'sha256'], text=True).splitlines()
        if not lines or any(line.split()[1] != HOST_FP for line in lines):
            raise ValueError('Pinned SSH host key mismatch')
        identity = temp / 'key'
        identity.write_text(key + '\n')
        identity.chmod(0o600)
        del key
        ssh = ['ssh', '-T', '-i', str(identity), '-p', port, '-o', 'BatchMode=yes', '-o', 'IdentitiesOnly=yes',
               '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(known), user + '@' + host]
        engine = Path('scripts/remote-release.py').read_bytes()
        def remote(op, rid, digest='-', proof='-'):
            command = 'python3 - ' + ' '.join(shlex.quote(x) for x in [op, rid, sha, digest, proof])
            result = subprocess.run(ssh + [command], input=engine, stdout=subprocess.PIPE, check=True)
            return json.loads(result.stdout)
        if mode in ('plan', 'deploy'):
            preserve_bh0001_live_html(Path('dist'))
            archive = temp / 'release.tar'
            with tarfile.open(archive, 'w') as t:
                for p in sorted(Path('dist').rglob('*')):
                    if p.is_symlink():
                        raise ValueError('Symlink in output')
                    if p.is_file():
                        t.add(str(p), arcname=p.relative_to('dist').as_posix(), recursive=False)
            # Known, validated numeric filename. This upload never touches public_html.
            command = 'umask 077; test ! -L "$HOME/.baito-hyouban-deploy" && mkdir -p "$HOME/.baito-hyouban-deploy" && chmod 700 "$HOME/.baito-hyouban-deploy" && test ! -e "$HOME/.baito-hyouban-deploy/' + current_id + '.tar" && cat > "$HOME/.baito-hyouban-deploy/' + current_id + '.tar"'
            subprocess.run(ssh + [command], input=archive.read_bytes(), check=True)
            result = remote('plan' if mode == 'plan' else 'apply', current_id, plan_digest or '-', plan_id or '-')
            Path('release-evidence/result.json').write_text(json.dumps(result, indent=2))
            if mode == 'plan':
                summary = '## Plan only — public files unchanged\n\nCommit: `' + sha + '`\n\nPlan SHA256: `' + result['plan_sha256'] + '`\n'
                for name in ('added', 'changed', 'preserved'):
                    summary += '\n### ' + name + '\n\n' + ''.join('- `' + p + '`\n' for p in result[name])
                summary += '\nPlan ID: `' + current_id + '`\n\nDiff, real-site backup and isolated recovery rehearsal passed.\n'
                summary += '\nAfter reviewing result.json, submit a separate deploy request with plan_id and approval:\n\n`DEPLOY ' + sha + ' ' + result['plan_sha256'] + '`\n'
                with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
                    f.write(summary)
                print(summary)
                return
            try:
                public_verify(result['candidate'])
                result = remote('finish', current_id)
            except BaseException:
                restored = remote('rollback', current_id)
                Path('release-evidence/rollback.json').write_text(json.dumps(restored, indent=2))
                public_verify(restored['before'])
                raise
        else:
            result = remote('rollback', backup_id)
            public_verify(result['before'])
        Path('release-evidence/final.json').write_text(json.dumps(result, indent=2))
        print('Release operation completed:', result['phase'])

if __name__ == '__main__':
    main()
