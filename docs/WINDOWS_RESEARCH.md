# Windows paper research audit ? 6 November 2026

This records the initial local preparation. For subsequent publication changes,
see [PUBLICATION.md](PUBLICATION.md) and [Windows setup](WINDOWS_SETUP.md).

## Result

The maintained CI suite (`tests` plus `diagnostics`) passes: **247 passed**
in 38.69 seconds using `C:\AI-Trading-Bot\.venv\Scripts\python.exe -X utf8`.
No test assertion was weakened, and no test was removed or skipped by these changes.
`pip check` reports no broken requirements; `git diff --check` passes.

## Audit

- `nsebot/`: current engine, three strategy sleeves, ledger, risk controls,
  free Yahoo data provider, paper broker, and historical Kite adapter.
- `python -m nsebot`: swing, intraday, momentum, backtest, status entry points.
  Swing/intraday previously accepted Kite. Momentum already used paper execution.
- `scripts/commit_state.sh`: CI persistence and README redraw; pushes its origin.
  Tests exercise this only against freshly created local bare repositories.
  Do not run this script against the project remote without approval.
- `.github/workflows/`: scheduled bot cycles plus research; the maintained test
  command is `python -m pytest tests diagnostics -q`.
- `legacy/`: archived V2 code and manual scripts named `test_*.py`. Several make
  public network calls at module import and some use historical notification/state
  machinery. Unqualified pytest discovery was interrupted after this was found.
  **Repository-wide discovery including these archived scripts was not completed.**
  No pytest exclusions or skip configuration were added to hide them.
- Runtime dependencies: pandas, numpy, yfinance, requests. `requirements-kite.txt`
  adds the optional paid broker SDK; it was not installed or used. Legacy has a
  separate dependency list. No package installation was performed.
- Installed versions: pandas 3.1.1, numpy 2.5.4, yfinance 1.8.0, requests 2.34.2,
  pytest 9.2.0, Python 3.12.10. Dependencies have lower bounds but no lockfile.

## Race-test root cause and changes

On this machine `bash` resolves to `C:\Windows\System32\bash.exe` (WSL),
which returned a UTF-16 access-denied error before the state script ran. The test
now locates Git Bash relative to the Git installation. Its nested race hook and
all original history/README assertions remain intact.

The state script also relied on `python3`, which resolves to a Windows App
Execution Alias here. It now honors `PYTHON` (the test passes `sys.executable`),
falls back to `python`, and explicitly enables UTF-8. Progress file I/O now
specifies UTF-8. The actual local bare-origin push/rebase/race test passes,
including with spaces in pytest's temporary directory. There is no evidence
from this reproduction that Git's local bare repository transport needs changing.
The initial working tree already marked `scripts/commit_state.sh` modified;
its existing script content was retained apart from interpreter invocation.

## Paper-only safeguards

- CLI and broker factory reject every non-paper selection before runner dispatch.
  CLI failures happen before market downloads, notifications, or state writes.
- KiteSession refuses real transports before reading credentials or importing
  the SDK. KiteBroker rejects arbitrary session injection. Its historical logic
  remains tested using explicit in-memory `OfflineKiteClient` doubles and dummy
  tokens. These test doubles are not live broker transports.
- Broker login is disabled. There is no environment switch to enable live access.
- CLI state defaults to ignored `local_research/state`, preserving upstream state.
  Explicitly selecting upstream `--state state` is still possible; avoid doing so.

## Fresh simulation and SSD

`local_research/state/` contains freshly initialized ledgers:

| Sleeve | Virtual cash |
| --- | ---: |
| Swing | INR 33,333.33 |
| Intraday | INR 33,333.33 |
| Momentum | INR 33,333.34 |
| Total | INR 100,000.00 |

No positions, pending orders, trades, or processed sessions. This equal split is
an initialization choice, not a strategy recommendation. Existing `state/` and
README trading history were not changed. Original shared capital defaults remain
unchanged; the local launcher sets its own allocation. Initial ledger creation
refused an existing destination rather than overwriting it.

Approved SSD directories were created without replacing data:
`E:\AI-Trading-Data\cache\yfinance` and
`E:\AI-Trading-Data\results\nsebot`.
The research launcher routes yfinance metadata cache and backtest results there.
Existing `raw`, `historical`, `processed`, `checkpoints`, and `backups` remain.
For research modules run directly, explicitly pass an SSD `--out` directory;
those modules retain their upstream defaults. No datasets were intentionally
downloaded or simulations run against external data in this task.

## Commands and remaining work

From the repository in PowerShell:

```powershell
.\dailytask.bat status
.\dailytask.bat test
```

Both use the exact project virtual environment and UTF-8. Test runs use fresh,
unique temporary directories under `C:\AI-Trading-Bot\test-runs`.
The launcher requires no PowerShell execution-policy change.

After separately approving public market-data downloads, use, for example:

```powershell
.\dailytask.bat backtest --allow-network
```

The launcher disables outbound email. It defaults to offline status and rejects
network commands unless the explicit flag is supplied. It never commits or pushes.

Remaining risks: archived import-time integration scripts need a separate review
before approved execution; the maintained suite does not validate real external
feeds. Dependency versions are not pinned. Paper fills cannot establish live
execution quality. Use a separate SSD result subdirectory per research experiment
to preserve earlier reports. Next: approve a small public-data smoke test and
inspect its data quality before running a long backtest. No GitHub push occurred.

## Files changed

`.gitignore`, `dailytask.bat`, `nsebot/__main__.py`, `nsebot/broker/kite.py`,
`nsebot/kite_login.py`, `nsebot/data.py`, `scripts/commit_state.sh`,
`scripts/progress.py`, `scripts/research.py`, `tests/test_progress.py`,
`tests/test_kite.py`, `tests/test_paper_only.py`, and this report.
Fresh ignored ledgers live under `local_research/state/`.
