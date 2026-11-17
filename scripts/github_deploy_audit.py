"""Conservative read-only GitHub Actions audit before a production publish.

The server-side daily reservation is the authoritative cross-workflow lock.
This independent API audit fails closed on missing, ambiguous, or inaccessible
historical release evidence. It never authorizes a deploy on its own.
"""
from datetime import datetime, timedelta, timezone
import json
import re
import urllib.parse
import urllib.request

from scripts.deploy_window import JST

RELEASE_WORKFLOW = "continuous-release.yml"
MODE_PATTERN = re.compile(r"Validated explicit request:\s+[A-Za-z0-9_-]+\s+(plan|deploy|rollback)\b")
UTC = timezone.utc


def _parse_time(value):
    if not isinstance(value, str):
        raise ValueError("Missing GitHub Actions timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Naive GitHub Actions timestamp")
    return parsed.astimezone(JST)


def _candidate(run):
    path = str(run.get("path") or "").lower()
    name = str(run.get("name") or "").lower()
    # Other workflow files capable of publishing must also be audited.
    return RELEASE_WORKFLOW in path or any(word in name for word in ("deploy", "production release", "publish"))


def _get_json(path, repository, token):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository + path,
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "baito-hyouban-deploy-audit"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("Oversized GitHub audit response")
    return json.loads(raw)


def _get_log(job_id, repository, token):
    request = urllib.request.Request(
        "https://api.github.com/repos/" + repository + "/actions/jobs/" + str(job_id) + "/logs",
        headers={"Authorization": "Bearer " + token,
                 "Accept": "application/vnd.github+json",
                 "User-Agent": "baito-hyouban-deploy-audit"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(3_000_001)
    if len(raw) > 3_000_000:
        raise ValueError("Oversized GitHub request log")
    return raw.decode("utf-8", errors="replace")


def _scan(repository, token, current_run_id, now, get_json, get_log):
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Timezone-aware audit clock required")
    today = now.astimezone(JST).date()
    # Search adjacent UTC dates to include runs queued before JST midnight.
    start = (today - timedelta(days=2)).isoformat()
    end = (today + timedelta(days=1)).isoformat()
    created = urllib.parse.quote(start + ".." + end)
    all_runs = []
    expected_count = None
    seen_run_ids = set()
    for page in range(1, 11):
        data = get_json("/actions/runs?per_page=100&page=" + str(page) + "&created=" + created,
                        repository, token)
        runs = data.get("workflow_runs")
        count = data.get("total_count")
        if type(count) is not int or count < 0:
            raise ValueError("Missing Actions run count")
        if expected_count is not None and count != expected_count:
            raise ValueError("Actions run history changed during audit")
        expected_count = count
        if not isinstance(runs, list):
            raise ValueError("Incomplete Actions run history")
        for run in runs:
            if not isinstance(run, dict) or type(run.get("id")) is not int or run["id"] in seen_run_ids:
                raise ValueError("Malformed or duplicated Actions run history")
            seen_run_ids.add(run["id"])
        all_runs.extend(runs)
        if len(all_runs) == expected_count:
            break
        if len(all_runs) > expected_count or len(runs) < 100:
            raise ValueError("Incomplete Actions run history")
    else:
        raise ValueError("Actions run history exceeds audit bounds")
    inspected = 0
    for run in all_runs:
        if not isinstance(run, dict) or not _candidate(run):
            continue
        run_id = run.get("id")
        if not isinstance(run_id, int):
            raise ValueError("Invalid historical run ID")
        if str(run_id) == str(current_run_id):
            if run.get("run_attempt") != 1:
                raise ValueError("Publisher rerun or missing attempt evidence refused")
            continue
        created_date = _parse_time(run.get("created_at")).date()
        if run.get("status") != "completed":
            # Even another plan might later become deploy; never race it.
            raise ValueError("Another production-capable workflow is still active")
        data = get_json("/actions/runs/" + str(run_id) + "/jobs?per_page=100",
                        repository, token)
        jobs = data.get("jobs")
        if not isinstance(jobs, list) or not jobs:
            raise ValueError("Missing historical release job evidence")
        request_jobs = [job for job in jobs if str(job.get("name", "")).split(" / ")[-1] == "request"]
        if len(request_jobs) != 1 or not isinstance(request_jobs[0].get("id"), int):
            raise ValueError("Ambiguous historical release request job")
        log = get_log(request_jobs[0]["id"], repository, token)
        modes = set(MODE_PATTERN.findall(log))
        if len(modes) != 1:
            # A failed/missing log is NOT proof that an attempted deploy was harmless.
            raise ValueError("Historical request mode could not be proven")
        mode = modes.pop()
        if mode != "deploy":
            inspected += 1
            continue
        release_jobs = [job for job in jobs if str(job.get("name", "")).split(" / ")[-1] == "release"]
        if len(release_jobs) != 1:
            raise ValueError("Missing historical deploy job")
        release = release_jobs[0]
        # A deploy job started yesterday can publish after JST midnight.
        stamps = [release.get("started_at"), release.get("completed_at")]
        may_touch_today = created_date == today
        for stamp in stamps:
            if not stamp:
                raise ValueError("Missing deploy completion proof")
            may_touch_today = may_touch_today or _parse_time(stamp).date() == today
        if may_touch_today:
            raise ValueError("Another deploy attempt exists on this JST date")
        inspected += 1
    return inspected


def audit_daily_releases(repository, token, current_run_id, now=None,
                         get_json=None, get_log=None):
    """Fail closed on every audit failure; only for a validated deploy request."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository or ""):
        raise ValueError("Invalid GitHub repository")
    if not token or not re.fullmatch(r"[0-9]+", str(current_run_id)):
        raise ValueError("GitHub Actions read permission and run ID required")
    clock = now if now is not None else datetime.now(UTC)
    try:
        inspected = _scan(repository, token, current_run_id, clock,
                          get_json or _get_json, get_log or _get_log)
    except Exception as exc:
        raise ValueError("GitHub historical deploy audit failed closed: " + str(exc)) from exc
    print("GitHub production workflow audit passed; historical runs inspected:", inspected)
    return inspected

