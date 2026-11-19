"""Validate connector requests before server secrets become available."""
import json
import os
import re
import subprocess
from pathlib import Path

# GitHub invokes these entrypoints by path, not as modules.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.github_deploy_audit import audit_daily_releases
from scripts.deploy_window import require_deploy_window

REQUEST_PATH = 'ops/release-request.json'

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

def validate(request, source_diff):
    allowed = {'schema_version', 'request_id', 'mode', 'source_sha', 'plan_id', 'plan_sha256', 'approval', 'backup_id'}
    if not isinstance(request, dict) or set(request) - allowed:
        raise ValueError('Unknown request fields')
    if request.get('schema_version') != 1 or not re.fullmatch(r'[a-zA-Z0-9_-]{8,80}', request.get('request_id', '')):
        raise ValueError('Invalid request version or ID')
    sha, mode = request.get('source_sha', ''), request.get('mode')
    if not re.fullmatch(r'[a-f0-9]{40}', sha) or mode not in ('plan', 'deploy', 'rollback'):
        raise ValueError('Invalid commit or operation; automatic publishing is unsupported')
    if set(source_diff) - {REQUEST_PATH}:
        raise ValueError('Code changed after the specified source; make a new plan')
    result = {k: request.get(k, '') for k in ('mode', 'source_sha', 'plan_id', 'plan_sha256', 'approval', 'backup_id')}
    if not all(isinstance(v, str) and '\n' not in v and '\r' not in v for v in result.values()):
        raise ValueError('Invalid request value')
    if mode == 'plan' and any(result[k] for k in ('plan_id', 'plan_sha256', 'approval', 'backup_id')):
        raise ValueError('Plan cannot include a publish approval')
    if mode == 'deploy':
        if not re.fullmatch(r'[0-9]+-[0-9]+', result['plan_id']) or not re.fullmatch(r'[a-f0-9]{64}', result['plan_sha256']):
            raise ValueError('Successful plan evidence is required')
        if result['approval'] != 'DEPLOY ' + sha + ' ' + result['plan_sha256'] or result['backup_id']:
            raise ValueError('Explicit approval of the exact diff is required')
    if mode == 'rollback':
        if not re.fullmatch(r'[0-9]+-[0-9]+', result['backup_id']) or result['approval'] != 'ROLLBACK ' + result['backup_id']:
            raise ValueError('Explicit backup approval required')
        if result['plan_id'] or result['plan_sha256']:
            raise ValueError('Rollback does not accept plan fields')
    return result

def main():
    if os.environ['GITHUB_REF'] != 'refs/heads/main':
        raise ValueError('Only main requests are accepted')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text())
    trigger = os.environ['GITHUB_SHA']
    if git('rev-parse', 'HEAD') != trigger:
        raise ValueError('Checkout differs from trigger')
    if os.environ['GITHUB_EVENT_NAME'] == 'push':
        if event.get('deleted') or event.get('forced') or event.get('after') != trigger:
            raise ValueError('Deleted/forced/mismatched push refused')
        if git('rev-parse', trigger + '^') != event.get('before'):
            raise ValueError('Request must be a single direct commit')
        if len(git('rev-list', '--parents', '-n', '1', trigger).split()) != 2:
            raise ValueError('Request must not be a merge commit')
        if git('diff', '--name-only', event['before'], trigger).splitlines() != [REQUEST_PATH]:
            raise ValueError('Request commit must change only ' + REQUEST_PATH)
        request = json.loads(Path(REQUEST_PATH).read_text())
        if git('ls-tree', '--name-only', event['before'], REQUEST_PATH):
            old = json.loads(git('show', event['before'] + ':' + REQUEST_PATH))
            if request.get('request_id') == old.get('request_id'):
                raise ValueError('Use a fresh request ID')
    elif os.environ['GITHUB_EVENT_NAME'] == 'workflow_dispatch':
        request = dict(event.get('inputs', {}), schema_version=1, request_id='manual-' + os.environ['GITHUB_RUN_ID'])
    else:
        raise ValueError('Unsupported trigger')
    sha = request.get('source_sha', '')
    if not re.fullmatch(r'[a-f0-9]{40}', sha):
        raise ValueError('Invalid source SHA')
    subprocess.run(['git', 'merge-base', '--is-ancestor', sha, trigger], check=True)
    result = validate(request, git('diff', '--name-only', sha, trigger).splitlines())

    if result['mode'] == 'deploy':
        require_deploy_window(result['mode'])
        audit_daily_releases(os.environ.get('GITHUB_REPOSITORY', ''),
                             os.environ.get('GH_READ_TOKEN', ''),
                             os.environ.get('GITHUB_RUN_ID', ''))
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
        for key, value in result.items():
            output.write(key + '=' + value + '\n')
    print('Validated explicit request:', request['request_id'], result['mode'], sha)

if __name__ == '__main__':
    main()
