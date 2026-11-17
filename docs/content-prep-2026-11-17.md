# BH-0046–0051 publication preparation — 2026-11-17

This is a preparation-only snapshot, not publication approval. Base main: `375519234eff0616b4166bcd176920a3ec858caa` (all 181 Git blobs downloaded and SHA-verified). No deployment, PR, main update, release request, workflow or guard change is included.

## Scope
Latest ledger review found six publication-waiting entries: BH-0046 Amazon warehouse, BH-0047 Sagawa Express, BH-0048 Bikkuri Donkey, BH-0049 Denny's, BH-0050 Royal Host, BH-0051 Joyfull. BH-0052/0053 still lacked images and BH-0054 remained in editing; re-read the ledger before the next release.

Six Google Docs manuscripts were converted to site Markdown with provenance, 12 FAQs each, official references, and related links. Six actual approved Drive WebP images were retrieved, inspected against the BH-0001 reference, and verified as 1200 × 630. Production/editing handoff notes were removed from reader-facing text. Existing 54 article approvals are preserved and six content/image hash approvals added.

## Editorial corrections and source checks
Main job terms and public references rechecked on November 17. Direct current official HTML confirmed Denny's Nogata early shift 1,280 yen and 05:30–09:00 (search crawl showed older terms); Royal Host Shinjuku high-school shift limit was confirmed as 21:00. Historical Denny's weekend figures are explicitly dated rather than represented as current. Royal Host Higashi-Shinjuku detailed numerical comparison and its unverified reference were removed because its old job endpoint returned HTTP 500. Amazon historical Fresh wages/job closures retain clear historical limitations. No employee reviews were fabricated.

Source endpoint check: 75 URLs, 68 HTTP 200. Three old Royal endpoints returned 500, three Joyfull hiring URLs returned 405 to direct retrieval (web extraction worked), and a competitor-research review site returned 403 and was not included in the articles. Job availability and rates can change; verify the actual store listing at application time. This check is not a guarantee that every referenced vacancy remains open.

## Passed local checks
- npm ci completed using the committed lockfile.
- npm test: 41 tests passed.
- Production build: 76 pages generated.
- Pre/post-build content gate: 60 approved articles passed.
- Editorial QA: FAQ count, table columns, references and image/title/ID alignment checked; leaked internal handoff text removed.
- Related live routes /guide/labor-conditions-notice/, /guide/part-time-job-choosing/ and /company/gusto/ returned HTTP 200.
- Protected BH-0001 source and image unchanged. Build preserved protected live HTML; server plan must still verify the remote disk match.

## Remaining mandatory release work
**Four-width browser/responsive QA has NOT been completed.** Playwright browser download failed with a corrupt archive; installed Chromium failed at process-singleton socket creation with EPERM, including the reviewed retry. Do not infer visual-layout approval from a successful build. Run the repository's full-article QA in a working browser environment, inspect the six new pages, and resolve failures before release.

Recheck main and the latest ledger, incorporate separately reviewed guard work if authorized, rerun all tests/build/content gates and release preflight/plan, verify remote backup/restore and protected BH-0001 disk equality. Confirm no duplicate release or running deployment. Production is allowed only in the designated JST 03:00 window, one batch/day; no daytime publication. Do not mark ledger rows published until the production result is verified.

## Persistence and CI
This snapshot is stored on a dedicated prep branch with `[skip ci]` in the commit message. It changes only six article files, six images, the approval registry and this audit document. No PR is created. Workflow inspection found main-only production triggers; remaining unrestricted push triggers are limited to their workflow files. The skip directive also prevents an initial-branch push from launching path-filtered jobs. The later release must deliberately run its own validation; skipped CI is not a passing check.

## Follow-up: production-note leakage audit

All six source articles and rendered HTML were additionally checked for internal-link candidate lists, ID-only instructions, editorial handoff text and production annotations. The reported exact internal-link candidate wording was absent. Two Denny's reference-number consolidation instructions remained and were removed. Sagawa manuscript wording, Royal Host comparative writing-process phrasing, Bikkuri Donkey manuscript-date wording, and Joyfull/Royal source-retrieval annotations were also revised for readers. Factual/source limitations and clearly labeled editorial analysis are retained. Approval hashes were refreshed and tests/build/content gates rerun. Four-width visual QA remains pending.
