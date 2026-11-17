"""Fail-closed historical GitHub Actions audit regression tests (no network)."""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from scripts.github_deploy_audit import audit_daily_releases

JST = ZoneInfo("Asia/Tokyo")
NOW = datetime(2026, 11, 18, 3, 5, tzinfo=JST)
REPO = "japanwillis/baito-hyouban"
TOKEN = "test-token"


def make_run(path=".github/workflows/continuous-release.yml", name="Continuous release (connector request)",
             status="completed", created_at="2026-11-17T20:00:00Z"):
    return {"id": 101, "path": path, "name": name,
            "created_at": created_at, "updated_at": created_at, "run_started_at": created_at,
            "status": status, "run_attempt": 1}


def make_api(run, jobs=None, fail=False):
    jobs = jobs if jobs is not None else [
        {"id": 200, "name": "request", "status": "completed"},
        {"id": 201, "name": "release", "status": "completed",
         "started_at": "2026-11-17T20:01:00Z",
         "completed_at": "2026-11-17T20:04:00Z"}]

    def get_json(path, repo, token):
        if fail:
            raise ConnectionError("Actions API unavailable")
        if path.startswith("/actions/runs?"):
            return {"total_count": 1, "workflow_runs": [run]}
        if path == "/actions/runs/101/jobs?per_page=100":
            return {"jobs": jobs}
        raise AssertionError("Unexpected API path: " + path)
    return get_json


def log(mode="plan"):
    return lambda job_id, repo, token: (
        "2026-11-17T20:01Z Validated explicit request: bh-20261117-request " + mode +
        " " + "a"*40 + "\n"
    )


class AuditTests(unittest.TestCase):
    def audit(self, run=None, mode="plan", jobs=None, get_json=None, get_log=None, now=NOW):
        run = run if run is not None else make_run()
        return audit_daily_releases(REPO, TOKEN, "999", now=now,
                                    get_json=get_json or make_api(run, jobs),
                                    get_log=get_log or log(mode))

    def test_read_only_plan_can_precede_deploy(self):
        self.assertEqual(self.audit(), 1)

    def test_prior_deploy_same_jst_day_rejected(self):
        with self.assertRaisesRegex(ValueError, "Another deploy attempt"):
            self.audit(mode="deploy")

    def test_cross_workflow_named_publish_rejected(self):
        run = make_run(path=".github/workflows/emergency.yml", name="Production publish")
        with self.assertRaisesRegex(ValueError, "Another deploy attempt"):
            self.audit(run, mode="deploy")

    def test_previous_day_deploy_without_overlap_allowed(self):
        prior = make_run(created_at="2026-11-16T20:00:00Z")
        jobs = [
            {"id": 200, "name": "request", "status": "completed"},
            {"id": 201, "name": "release", "status": "completed",
             "started_at": "2026-11-16T20:01:00Z",
             "completed_at": "2026-11-16T20:04:00Z"}]
        self.assertEqual(self.audit(prior, mode="deploy", jobs=jobs), 1)

    def test_queued_release_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "still active"):
            self.audit(make_run(status="in_progress"))

    def test_missing_request_mode_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "could not be proven"):
            self.audit(get_log=lambda *_: "request failed before validation")

    def test_api_error_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "audit failed closed"):
            self.audit(get_json=make_api(make_run(), fail=True))

    def test_unrelated_qa_run_not_a_publish_candidate(self):
        run = make_run(path=".github/workflows/qa.yml", name="Verify Astro build")
        self.assertEqual(self.audit(run), 0)

    def test_missing_token_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "read permission"):
            audit_daily_releases(REPO, "", "999", now=NOW)

    def test_current_run_is_excluded(self):
        run = make_run(status="in_progress")
        self.assertEqual(audit_daily_releases(REPO, TOKEN, "101", now=NOW,
                                            get_json=make_api(run), get_log=log("deploy")), 0)


if __name__ == "__main__":
    unittest.main()

