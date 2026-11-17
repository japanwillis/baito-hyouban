# 2026-11-18 JST release audit handoff

PRs #23 (daily deployment safety) and #21 (nine approved articles BH-0046–BH-0054) were merged. Reviewed source: `6f9a11aed3629d12606f1aaf2442d6e78fa21d32`.

- Integrated build: 78 tests passed; responsive QA at four widths passed.
- Nonpublishing plan `44148930895-1`: succeeded, diff/real-site backup/isolated recovery all verified. Plan digest `3e701461bf7cf84179396e0176b7b2fd3d959309bc17fa4bf043083deecbf00a`. Adds nine HTML pages and nine images; 42 changed pages reflect reviewed removal of visible internal IDs and listing/search/sitemap updates. Protected BH-0001 bytes unchanged.
- Explicit deploy request commit `cac4db1336676be7a7b2d873bd153899a2bffbd6`, run `44149386514`, FAILED before release: request job rejected `Actions run history changed during audit`; release job SKIPPED. No SSH or production release from this run.
- Open PR #14 has head `main` against an old QA base, so main request pushes also enqueue three PR QA workflows. These unrelated new run IDs changed the total count between history pages. PR #14 remains open; do not close it as part of this fix.
- Read-only server check at 03:35:49 JST: prior active release `44036085532-1` still verified, source `77b77bd7fbc78d769329ea2266d17bdeadf17313`; 23 release records; zero daily reservations; no pending blocker; `NO_FILES_CHANGED=yes`.

## Narrow correction
Only the explicit pagination count-change exception may restart the entire history scan from page one, at most three scans, with two- and four-second delays. Partial snapshots are discarded. New parallel publishers and same-day deploys found on retry still block. Persistent churn, incomplete/duplicate histories, API/auth failures, reruns, and unknown request modes still fail closed. This is not an automatic workflow/deployment retry.

## Next operation
No further deploy or deploy rerun on 2026-11-18 JST. This failed request remains ambiguous to the conservative history policy for that day, even though the operator separately verified release was skipped. Do not exempt it or clear server records.
Review this change and CI before any merge. On the next authorized JST 03:00–03:59 window, recheck current main, approvals, concurrent work, full Actions history and server pending/daily/legacy evidence. Create a NEW exact-source plan after any code change and verify its diff, real backup and isolated recovery; do not reuse the old plan digest with new source. Submit at most one deploy only if every gate passes. Confirm final server state plus HTTPS hashes and responsive public pages before recording publication.

## Review and canonical manuscript follow-up

Independent review of PR #24 found no safety regression from bounded snapshot retries; partial/duplicate histories after retry still fail closed. Exact-head CI at `29991ca6` passed 84 tests and build. Real-history QA `44149919992` failed with `Historical request mode could not be proven`, the intended refusal of today's failed request. Do not report all CI green or bypass this condition.

BH-0048 canonical v3: https://docs.google.com/document/d/15uzcXGcIleP8i--6cUlWvkHE6OQ4BHnzMLbVGbOM4gA/edit. Ledger row 58 re-read: manuscript/review links both v3, editorial approved, image inspected, publication pending/unpublished. Native-document roundtrip was independently delivered and source SHA256 verified against this branch: `065360cb247cd3c46d40124491cabdf3493b72ee3a6498d62c85f91d9ec6ab53`. Image bytes/blob verified unchanged, SHA256 `09db6ce3fecae98982f0496d4d6db77a269f033e2b8d0653c4b7fccae7be5aa2`. Only BH-0048 manuscriptUrl, reviewUrl and note change in approvals; no source/image/hash or publication-status change. Fresh exact-head CI and next-window plan are still required.
