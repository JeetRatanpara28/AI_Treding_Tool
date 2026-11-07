# Windows 11 paper-only setup

Derived from https://github.com/tanmaykaper/Paper-Trading-Bot (MIT, copyright
2026 Tanmay). The original license and source attribution are preserved.

## Python and dependencies

Use Python 3.12 and Git for Windows (including Git Bash). The configured project
interpreter is `C:\AI-Trading-Bot\.venv\Scripts\python.exe`.
The batch launcher uses that interpreter without shell activation or PowerShell
execution-policy changes. For another directory, adjust its interpreter path.

If the virtual environment does not already exist, create it:

```powershell
py -3.12 -m venv C:\AI-Trading-Bot\.venv
```

Dependency installation requires approved internet access. Runtime and offline
test dependencies are free; do not install `requirements-kite.txt` or configure
broker credentials. Once approved:

```powershell
& C:\AI-Trading-Bot\.venv\Scripts\python.exe -m pip install -r requirements-test.txt
```

## Initialize and inspect a private simulation

From `C:\AI-Trading-Bot\open-source-bot`:

```powershell
.\dailytask.bat init
.\dailytask.bat status
.\dailytask.bat test
```

`init` refuses an existing state directory. The current workstation is already
initialized; use `status` here. Capital totals INR 100,000 across three sleeves:
33,333.33 swing, 33,333.33 intraday, and 33,333.34 momentum. This is virtual money.
The ignored `local_research/state/` holds all private ledgers. Upstream `state/`
files retained on the original workstation are not part of the published source.
Do not choose `--state state` or upload any ledgers, journals, or cached market data.

## SSD and optional research

Use `E:\AI-Trading-Data` for datasets and results. The launcher configures
`cache/yfinance` and `results/nsebot` beneath that root. Create missing directories
only; preserve earlier datasets and reports. For directly invoked research modules,
pass a unique SSD `--out` directory. The launcher disables outbound email.

After explicit approval for public data downloads:

```powershell
.\dailytask.bat backtest --allow-network
```

Paper commands still access public data; the flag records that this was explicitly
chosen. No broker login, real order transport, or live-mode override is available.

## Session calendar and data-quality safety

Daily `swing` and `momentum` commands require the reviewed offline NSE cash-equity
calendar in `nsebot/calendars/nse_cash_2026.json`. Holidays and genuine weekend
sessions are included. Both the CLI and the inactive scheduling gate use this
single calendar. Missing/corrupt/expired coverage stops before a download or
portfolio access; there is no fallback to an assumed weekday.

The current source review is dated 7 November 2026 and expires after **10 November
2026 IST**. Annual date coverage is 2026, but this does not extend the review
expiry. Review official amendments before extending the expiry; do not merely
change the date to bypass a stop. `NSEBOT_CALENDAR` can select a separately reviewed
local calendar; invalid configured files fail closed.

Daily data readiness is **16:15 IST**, after the reviewed post-close session end
plus a local safety buffer. This is a policy, not a promise that Yahoo has finalized
its data. The required session's index, each fetched stock, and every held/pending
symbol must have one complete, valid OHLCV bar. Missing values, duplicates, invalid
prices or stale dates stop the cycle with `DATA FRESHNESS` and exit code 3.

The intraday CLI refuses special sessions rather than applying regular-session
strategy hours to them, and skips closed days without downloads. During normal
sessions its runtime checks the latest completed interval before processing a
poll. A lost feed does not manufacture a final close at the entry price. Earlier
successfully saved polls remain saved; a later failure does not roll them back.
Historical replay/engine `step()` APIs retain their historical-data behavior.

## Official-source recovery tools

`nsebot.research.fetch_official` provides a bounded, manual downloader for the
reviewed calendar circulars or the approved 6 November 2026 closing reports.
It uses the already-installed `curl_cffi` default transport, which succeeded where
standard `requests` and Windows curl timed out. It uses no impersonation, custom
proxy or login. It requires explicit user approval before `--allow-network`,
refuses existing output folders, and rejects HTTP block/HTML pages and changed
Muhurat PDF bytes. Calendar/date validation still applies after downloading.

`nsebot.research.source_check` validates local official NSE cash bhavcopy and Nifty
closing CSVs. It checks the trade date, NSE CM/EQ identity, duplicate/missing rows,
OHLC bounds and finite prices. It uses `ClsPric`, not `LastPric`, for the official
cash close. Outputs are a separate, **unadjusted one-session verification snapshot**;
they are not silently spliced into Yahoo's adjusted historical prices or passed
to an engine. No new dataset is sufficient for a strategy backtest merely because
this one-day source check passes.

Keep downloaded PDFs, ZIPs, CSVs and results on `E:\AI-Trading-Data` and preserve
originals. These artifacts are ignored by Git. Source hashes/provenance are recorded
in the SSD manifests. See [calendar verification](NSE_CALENDAR_REVIEW.md) and
[repair status](REPAIR_STATUS.md) for current evidence and remaining source limits.

## GitHub Actions and publication

All workflows are manual-only. The swing, intraday, and momentum jobs are
unconditionally disabled and have read-only permissions; there are no schedules,
state-pushing steps, or secret references. Manual research runs only offline tests
on Windows and Ubuntu. Original workflows are archived under
`docs/archived-workflows/*.disabled`; these are documentation, not active Actions.
Explicit approval and reviewed changes are required before enabling automation.

The maintained suite is `python -X utf8 -m pytest tests diagnostics -q`.
Archived `legacy/test_*.py` scripts can make network calls during import and are
not part of the maintained CI suite. Review them separately before any execution.

The new repository starts with a source-only root commit so old portfolio blobs
are not reachable from main. Original Git history stays on a local backup branch
and the upstream remote. Push only main; do not mirror or push all branches/tags.
