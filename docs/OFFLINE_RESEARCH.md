# Offline research contract and audit

Latest evidence: [the TCS/LT market pilot](HISTORICAL_PILOT_RESULT.md) completed
with dated fee/tick context, preserved weak results and 451 maintained tests.
The original five-stock study remains incomplete. Earlier counts/status below
are historical snapshots, not the latest result.

Date: 7 November 2026. Scope: daily swing research engineering while historical
data access is pending. No market download, broker connection, notification,
scheduled job or GitHub publication is part of this work.

## Frozen baseline and evidence rules

- Use existing `BotConfig()` swing reversion signal/risk parameters; no parameter
  search or selection of the most profitable scenario. Each run saves its actual
  config, static charge assumptions, all `nsebot` Python source hashes, Python /
  pandas / numpy versions, source commit and input hashes in `frozen_spec.json`
  **before** computing performance. Commit alone cannot identify uncommitted fixes.
- Swing capital INR 33,333.33; intraday and momentum allocations remain separate.
  Current swing caps include 1x leverage, 3% risk cap, 40% position cap, 15% heat
  cap, five positions and INR 8,000 minimum notional, with existing lift-to-floor
  logic. This records defaults, not a claim those risk levels are appropriate.
- Fixed small engineering universe: the five reviewed input equities, not today's
  stock selection presented as a historically investable universe. A five-name
  sample also leaves the existing breadth component inactive (minimum ten names).
- Require 200 warm-up sessions plus at least 252 evaluated sessions in the strict
  local pilot importer. This is an engineering minimum, not statistical evidence
  of an edge. A five-year acquisition includes warm-up, shortening evaluation.
- Entry signal uses completed close data and fills at the next eligible open.
  In historical replay, discretionary close-observed exits now wait until the
  next available open. Gap/standing protective stops remain immediate; a queued
  exit cannot escape an adverse opening gap. A final queued exit remains open,
  rather than receiving an invented last-day fill.
- Fix three adverse slippage scenarios before testing: 5, 10 and 25 bps on entries,
  market exits and stop/gap exits, with adverse tick rounding. These are sensitivity
  assumptions, not calibrated fill estimates. Lower net returns or changed trade
  counts are not automatically bugs; execution changes can alter the whole path.
- Static CNC costs include buy/sell STT, buy stamp duty, exchange/SEBI/GST and the
  sell DP charge. They are software assumptions, **not exact dated historical
  tariffs**, and do not include income/capital-gains tax. Tick bands are also
  software defaults, not independently reviewed historical instrument rules.
- Same-stock buy-and-hold: equal initial budgets, integer shares, buy costs and
  adverse rounding; decide before the second evaluated session's open and hold.
  First evaluated close stays in cash, matching the strategy's initial no-position
  session. Nifty remains a separately labelled gross price-index reference, not
  an investable fund with simulated fees.
- All terminal positions are marked, not forcibly liquidated, in strategy and
  same-stock benchmark. Dividends are excluded from these price-only results.
  Open inventory, queued exits, pending entries and closed trade costs are reported.
- Earlier 60% / later 40% descriptive splits assign each trade to exactly one
  segment. The prior close anchors later-segment returns, so the boundary return
  is not lost. Positions carry across the boundary. This is not an independent
  untouched out-of-sample experiment, and upstream performance is not reproduced
  evidence for the changed execution convention.
- Report net price return, CAGR, max drawdown, Sharpe (zero risk-free assumption,
  252-session annualization), exposure/holdings and trade counts with limitations.
  Zero or few trades mean inconclusive evidence. No pass threshold guarantees
  positive profit, benchmark outperformance or readiness to trade.

## Import a reviewed local dataset

`nsebot.research.offline_data.load_dataset` only reads local files. All files
must be distinct CSVs contained inside the manifest folder, including after
resolving paths/symlinks. It rejects duplicate headers, malformed OHLCV, invalid
dates, duplicates, reordered rows, calendar mismatches and insufficient history.
It does not silently fill, sort, deduplicate, adjust or splice data.

Each equity and index CSV has `datetime,open,high,low,close,volume`; naive
midnight dates mean Asia/Kolkata **session labels**, not UTC instants. Equity
volume must be positive; index volume can be zero or unavailable because this
swing replay uses index prices only. Unavailable index volume stays missing;
OHLC and equity volume remain mandatory. See [the verified contract update](TAPETIDE_ACQUISITION.md).
The calendar CSV has `datetime`, including verified special
sessions. Every pilot series must exactly cover that calendar; this strict pilot
does not model suspensions, IPOs, delistings or a changing investable universe.

Example manifest structure (example only; not a market-data rights declaration):

```json
{
  "format_version": 1,
  "data_kind": "market",
  "source": "REPLACE with reviewed provider, retrieval date and adjustment method",
  "source_permission": "REPLACE with applicable terms or approval reference",
  "calendar_source": "REPLACE with reviewed official historical calendars",
  "price_basis": "split_adjusted_price",
  "corporate_actions_reviewed": true,
  "sessions": "sessions.csv",
  "index": "NIFTY50.csv",
  "stocks": {
    "RELIANCE": "RELIANCE.csv",
    "TCS": "TCS.csv",
    "HDFCBANK": "HDFCBANK.csv",
    "HINDUNILVR": "HINDUNILVR.csv",
    "LT": "LT.csv"
  }
}
```

Synthetic fixtures must say `"data_kind": "synthetic"`. Do not relabel them as
market data. A review boolean or provenance string is only a declaration; it
does not establish rights, identity/ISIN history, official calendar completeness,
corporate-action accuracy or dividend treatment. Review those against originals
before market performance is accepted. Unsupported raw/total-return price bases
are rejected; never set `split_adjusted_price` just to bypass that gate.

After real reviewed files are available, the existing launcher supports this
offline-only form (paths below are placeholders):

```powershell
.\dailytask.bat offline-backtest --manifest "E:\AI-Trading-Data\processed\reviewed-pilot\manifest.json"
```

No `--allow-network` flag is needed or used by this command. Missing files fail;
there is no automatic vendor fallback. The older `backtest --allow-network`
route remains a separate Yahoo fetch and is not how to run this local pilot.
Default outputs are new `offline-backtest-*` folders beneath the SSD results
directory; each slippage case has its own isolated engine state. Existing
portfolios and previous trials are preserved. Never publish generated data.

## Verified engineering evidence

Targeted prefix tests compare full-history and truncated-history features,
signals, regime and equity, exercising an actual synthetic round trip. Changing
future stock prices leaves prior features/signals unchanged. Execution tests
cover next-open exit timing across ledger reload, queued gap stops, adverse long
and short stop slippage, invalid slippage, and independently hand-calculated CNC
charges. Import/launcher tests exercise invalid inputs and Windows paths with spaces.
All older assertions and safety tests are retained.

The initial prefix test uncovered an empty-ledger CSV dtype distinction, not a
price/decision mismatch. The fixture cutoff was moved past a closed trade so
both sides actually exercise matching nonempty trade history, keeping strict
frame/dtype equality rather than weakening that assertion.

A full offline synthetic audit generated five artificial symbols over 520
synthetic business days (320 evaluated), ran all three slippage cases twice,
and verified byte-identical equity/trade/benchmark artifacts and matching summary
JSON. All cases exercised round trips (24/25/25), cash/position/P&L reconciliation
passed, and private old/local portfolio hashes stayed unchanged. These fabricated
price paths are deliberately constructed to exercise code, not estimate returns.

Private receipt:
`E:\AI-Trading-Data\results\nsebot\synthetic-offline-audit-llqx8qfj\AUDIT.json`.
This receipt identifies its exact hashed implementation; later code changes
require a fresh receipt rather than overwriting this evidence.

Final maintained suite via the existing Windows launcher and configured Python
3.12 virtual environment: **384 passed in 44.65 seconds**, no warnings. This
includes the Git Bash temporary-bare-origin race test and unchanged live-order
guards. A new gap-affordability test also exposed a pandas row-assignment warning;
using a bar dictionary instead of adding a timestamp to a float Series fixed
that cause rather than suppressing the warning. Swing fills now reject opening
notional plus costs above available paper cash; the replay additionally rejects
any negative-cash session. `git diff --check` passes. Earlier receipts and trials
remain preserved.

The actual `dailytask.bat offline-backtest` invocation also returned
`TECHNICAL_CHECKS_PASS (synthetic)`. Its summary matched the direct audited run
byte for byte. Integration receipt:
`E:\AI-Trading-Data\results\nsebot\synthetic-offline-audit-llqx8qfj\launcher-verification\offline-backtest-2swiz8tn\summary.json`.
Final read-only portfolio check confirmed INR 100,000.00 cash with no positions,
pending entries or processed sessions across the three local sleeves.

Files in this offline preparation change:

- `nsebot/backtest.py`: causal replay, explicit stop slippage, descriptive split
  boundaries/return anchors and accurate execution/benchmark limitations.
- `nsebot/engine/swing.py`: opt-in persisted next-open close exits, gap priority,
  opening-fill cash guard and pandas-compatible bar mapping.
- `nsebot/broker/paper.py`: explicit stop-slippage option and invalid-value checks,
  preserving legacy defaults when the option is not supplied.
- `nsebot/research/offline_data.py`: strict local CSV/manifest/calendar import.
- `nsebot/research/offline_backtest.py`: fixed scenarios, equal-budget buy-and-hold,
  frozen source/config/version provenance, paid costs, invested/time exposure,
  terminal inventory and cash/P&L reconciliation.
- `scripts/research.py`: offline command through the existing `dailytask.bat`;
  existing network-command permission gate remains in place.
- `tests/test_replay_causality.py`, `tests/test_offline_data.py`,
  `tests/test_offline_launcher.py`, `tests/test_backtest_safety.py`: regression
  coverage; the last file also contains earlier preparation tests.
- This report and the link in `docs/BACKTEST_READINESS.md`.

The ignored private application record was updated only to reflect the user's
report that they sent the enquiry. Earlier uncommitted skills/docs/AGENTS changes
were preserved. No commit/push was made.

## Remaining research gates

Real history and permission/eligibility response are pending. The user reports
having emailed the academic enquiry; the assistant did not send it. No student
details or application material belongs in tracked documentation.

Same-close timing remains in the legacy daily runtime and other archived research
simulators; they are not certified by this causal swing replay audit. Existing
trading workflows remain disabled. Intraday execution cannot be validated from
daily data. Independent source/ISIN/calendar/corporate-action review, dated fees,
auction/band/liquidity constraints, price-versus-total-return comparison and
universe-selection bias remain material before accepting market conclusions.
No whole-bot absence-of-bias or profitability claim follows from these tests.
