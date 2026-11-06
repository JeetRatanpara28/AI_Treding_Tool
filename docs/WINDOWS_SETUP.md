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
