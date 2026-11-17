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

## BH-0052 added after formal image delivery

The latest ledger now places BH-0052 in publication waiting with editorial v2 approval. BH-0053 and BH-0054 are both image-waiting, not publication-waiting (supersedes the earlier BH-0054 editing status above). Prepared `/job/100-yen-shop-part-time/` using the JobArticle layout. Existing six articles/images are unchanged by this addition.

Source: https://docs.google.com/document/d/19l4Yaz7bzSMVM8Kqg5RqtcPqnGlkapgO0LBSAlOxMIA/edit . Image: https://drive.google.com/file/d/1e-EpvBSgnAR0aL0ip-E2O-MRC1puVcEy/view . Drive bytes independently retrieved: 219592 bytes, 1200×630 WebP, SHA256 `dd47642583057681b282acee94872568ed7df50c0fadbb748f38e6dab3170722`, matches ledger. Watercolor style, natural people, no readable logos/text visually inspected.

All nine cited official/public sources checked. S01 originally incorrectly linked to DAISO recorded-interview instructions; replaced with https://recruit-daiso.com/jobfind-pc/ whose job-description section supports the manuscript. Seria official current HTML for Aeon Tobata 14478 confirms high-school graduation and 15:00–21:30 among shifts; Meets Kokubunji 17088 confirms 12:00–18:00 and 16:00–21:30. Search-cached versions showed older/closed state, so current direct HTML was checked instead of treating the cache as current. No salary or continuing vacancy guarantee added. Cando current FAQ supports fixed shifts, store-specific conditions and beginner training. Ministry pages support the general employment-condition/minimum-wage statements.

Removed internal link-setting instructions, SEO production metadata, image brief, editorial handoff/history and pre-publication instructions from reader-facing text. DAISO related live URL returned HTTP 200. Verified source and rendered HTML contain no production-note markers; 12 FAQs, two rendered tables, matching table columns, all S01–S09 references defined. Tests: 41 passed. Build: 77 pages. Pre/post content gates: 61 approved articles. Updated approval hashes.

Seven prepared articles now await mandatory four-width browser QA and the release plan/restore/protected-page checks. This addition is not publication approval. Same JST 03:00-only and one-batch/day restrictions apply. No main update, PR or deployment. Commit uses `[skip ci]`.

## Reconciliation after the 18:00 report and main cleanup

The 18:00 report's BH-0046 wage discrepancy is already correctly represented in the prepared article: Amazon's old Fresh page displays zero vacancies and 1,250 yen, whereas the official Kanagawa notice states 1,279 yen effective October 1, 2026. Both were directly retrieved again. The 29-yen comparison remains valid; it is not presented as current hiring pay or proof of unlawful payment. No wage-number correction was needed. Production `/company/amazon-warehouse/` returned HTTP 404, consistent with an unpublished article. Report: https://docs.google.com/document/d/1r8DPI5ntPJL9h6ZJx-S72j0OBfcr9TnzyUhf-tRg_Hc/edit . Evidence: https://www.amazon.jobs/pl/landing_pages/jp_gsf_parttime and https://jsite.mhlw.go.jp/kanagawa-roudoukyoku/home/houdou/20260827_00001.html .

Main advanced from 3755192 to `19ac78802dc27d3de3891de88a5c918fa638d605`, with 35 existing article cleanups, editorial-note rejection/tests, and that cleanup's plan/deploy history. All 39 changed main blobs were SHA-verified and integrated without reverting any existing article or approval. The approval registry preserves all 54 latest-main records verbatim as objects and appends the seven prepared records. New editorial-note gates pass all 61 articles. Test suite now passes 42 tests; build generates 77 pages, pre/post-build gates pass 61 approved articles.

The merged tree retains main's existing release-request file byte-for-byte as history. **Do not execute/replay that old request for this new batch.** A future authorized release must prepare its own reviewed request and run fresh plan/backup/restore/protected-page checks, four-width QA, latest-ledger and duplicate-deployment checks. No main update, workflow dispatch, PR or production deployment was performed by this reconciliation. The merge is preparation-only with `[skip ci]`.
