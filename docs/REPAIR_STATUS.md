# Repair status - 7 November 2026

New strategy research, larger downloads, backtests, dashboard work and AI/ML remain
on hold while the user reviews these fixes. Source-only publication requires separate user approval; private data is never
included in that publication.

| Previously incomplete or failing item | Current result |
| --- | --- |
| NSE PDFs/daily-report downloads timed out | Repaired default `curl_cffi` transport downloaded all 5 approved PDFs and 2 approved daily reports successfully; hashes and manifests saved. No impersonation/proxy/login. |
| Muhurat exact timing unverified | Both supplied PDF pages reviewed; direct download matches its SHA256. |
| Mock session could be mistaken for trading | Official 7 November notice verified as mock; excluded from trading calendar. |
| Weekday freshness logic missed real Sunday sessions | Shared reviewed calendar now handles holidays and verified Sunday sessions, with fail-closed coverage/expiry checks before downloads. |
| 15:45/15:50 cutoff conflict | Daily CLI and gate share 16:15 local readiness policy, after post-close end. |
| Intraday stale feed/synthetic final fill | Runtime now rejects stale/incomplete finished bars and missing held/pending data. Missing final data cannot use entry price as a made-up close. Special intraday sessions are blocked. |
| Missing Yahoo 6 November close | Root cause confirmed in raw chart payload for all 3 symbols. Incomplete Yahoo data remains rejected; the upstream vendor's response is not claimed repaired. |
| Authoritative close comparison unavailable | Supplied official reports validated and direct downloads recovered; independent official snapshot PASS for RELIANCE, TCS and Nifty 50. No silent history splice. |
| Existing portfolio protection | Original files preserved; local INR 100,000 simulation must remain flat and unchanged. |

## Data evidence

Approved window: 7 August through 6 November 2026; only RELIANCE.NS, TCS.NS and
Nifty index were requested from Yahoo. The initial adjusted download had 63 rows
per symbol; each had an incomplete 6 November row. The sanitizer retained 62
valid rows through 5 November. A direct raw-chart recheck confirmed null `close`
fields on 6 November, establishing that this was not a sanitizer assertion bug.

Local official-report validation returned these 6 November closing values:
RELIANCE 1320.00, TCS 2498.50, and Nifty 50 25030.35. These come from `ClsPric`
and the index closing field, not from last-traded prices or inferred values.
They are source-verification results, not investment advice or backtest returns.

Source delivery was independently checked: recovered direct bhavcopy/index bytes
match the user's files. The official one-day snapshot is unadjusted and separate
from Yahoo's adjusted series. The research tools do not feed it to an execution
engine. The Yahoo feed is not approved for a current-session run while its
required close is missing; there is no override to turn that failure into a pass.

Evidence paths on the private SSD:

- Raw vendor recheck: `results/nsebot/smoke-raw-close-recheck-20261107-ve07lpqi/summary.json`.
- Supplied-source verification: `results/nsebot/official-source-recovery-20261106-b1ca2968/comparison.json`.
- Repaired direct downloads: `results/nsebot/nse-fixed-downloads-20261107-2r1fu5de/run.json`.

## Verification and operating limits

Run the maintained suite using `dailytask.bat test`. New coverage includes calendar
expiry/coverage, verified special-session dates, invalid schemas and timing
conflicts, pre-network failure, intraday stale bars, missing values, official
report dates/identities, duplicate rows, HTML/block-page rejection, source hashes
and overwrite refusal. Tests use isolated synthetic/local fixtures, not network
requests, broker credentials or private portfolio files.

The calendar review expires after 10 November 2026 IST; update from reviewed
sources before extending it. Intraday special sessions are deliberately unsupported
and blocked. Historical replay remains separate from runtime freshness checks.
A one-day official-source PASS does not establish a sufficient history for a
strategy backtest. These constraints must not be hidden or weakened to proceed.

## Final verification receipt

- Maintained suite: **342 passed in 41.47 seconds**, using the configured Python
  3.12 virtual environment on a clean source export containing no private state,
  source PDFs, downloaded CSVs/ZIPs or datasets. This also exercised the Git Bash
  local-bare-repository race test with spaces in the export path.
- `pip check`: no broken requirements. No package installation was needed.
- `git diff --check` and new-file whitespace checks: passed.
- Local simulation: exact total INR 100,000.00, no positions, pending orders,
  trades, equity-history rows or processed sessions.
- Direct-source downloader: calendar group PASS (5 PDFs), closing group PASS
  (2 reports). The downloaded CSV bytes matched user-provided originals.
- Supplied PDF and CSV files, earlier failed attempts and private upstream state
  were preserved. All generated data/results remain outside the repository on SSD.
- No live access, trading automation or real/paper engine run occurred during
  repair verification. Source-only publication is a separate approved action.

The externally incomplete Yahoo source is rejected, not declared repaired.
Official-source verification is complete for the approved files and one date;
future data/history still needs its own scope and approval. No new project phase
has begun. The reviewed calendar must be refreshed after 10 November 2026 IST.
