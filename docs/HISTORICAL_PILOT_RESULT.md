# Historical pilot result - 7 November 2026

Subsequent [corporate-action follow-up](CORPORATE_ACTION_REPAIR.md) adds an all-five
interval stress experiment and endpoint entitlement benchmark. It is separate
from this stricter TCS/LT snapshot; full strict-source validation remains pending.

**A real-data TCS/LT engineering pilot finished; the full five-stock study is
not complete. Technical checks pass. Strategy evidence is insufficient and the
observed net result is negative. No deployment or profitability claim follows.**

The [specification](HISTORICAL_PILOT_SPEC.md) was recorded before performance.
No signal/risk/sizing threshold was changed, no variant was selected for profit,
and the three predetermined slippage cases all remain in the report.

## Actual result

Capital INR 33,333.33, swing sleeve only. Input: 1,241 reviewed sessions from
8 November 2021 through 6 November 2026. Warm-up: 200 sessions. Evaluation:
**26 August 2022 through 6 November 2026, 1,041 sessions**.

| Adverse slippage, each leg | Final virtual equity | Net price return | Net P&L | Max drawdown | Closed trades | Same-stock buy-and-hold return |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 bps (0.05%) | INR 33,012.45 | -0.9626% | INR -320.88 | -1.1207% | 1 | +44.3911% |
| 10 bps (0.10%) | INR 33,002.40 | -0.9928% | INR -330.93 | -1.1209% | 1 | +44.3450% |
| 25 bps (0.25%) | INR 32,972.25 | -1.0832% | INR -361.08 | -1.1627% | 1 | +44.2071% |

The 5-bps case has CAGR -0.2341%, Sharpe -0.4402 (zero risk-free,
252-session annualization), paid costs INR 38.43 and win rate 0/1. These are
descriptions of one trade, not stable estimates. Average invested fraction was
only 0.2041%; seven sessions had a position (0.6724% of evaluated sessions).
Buy-and-hold maintained much higher exposure and had roughly 26.85% drawdown.
It is a price-return comparison with different exposure/risk, not proof of a
universal superior strategy. Nifty's separately labelled gross price reference
returned +42.5508%; it is not an investable net/dividend-inclusive fund result.

All scenarios end flat: no inventory, pending entries or queued exits. There
was no artificial last-day liquidation. Dividends/optional tender buybacks are
excluded/declined consistently for the admitted equities.

## Why only one trade?

An observed repeat captured every session without changing engine decisions:

- TCS: all 1,041 sessions met liquidity requirements. Four had a three-session
  drop of at least 8%, but none also passed the long-term uptrend requirement.
  Complete entry signals: zero.
- LT: all 1,041 sessions passed liquidity; six deep dips, three also in uptrend.
  One was placed, filled and closed. Two were correctly rejected because the
  existing allocation produced about INR 3,483 / 3,883, below the INR 8,000 floor.
- All three scenarios have the same signal/placement/fill counts. No unexplained
  order cancellation or hidden live transport was found.

This small universe is unsuitable for estimating the rare-signal strategy's
edge. Lowering the dip threshold, removing the minimum size or enlarging a risk
cap after seeing this result would be a new experiment. None was done. Valid
weak results are retained; tests were not weakened to turn them positive.

## Completed preparation and verification

- Independently constructed NSE cash calendars from annual official circulars
  and amendments: all six acquired series exactly match 1,241 session labels,
  including special live weekends; zero missing/extra dates. Sources/original
  PDF hashes are archived. Runtime freshness/calendar expiry was not relaxed.
- TCS/LT historical primary ISIN anchors match current official identities.
  Full adjustment and corporate-action timelines were inspected. Their 1,241
  adjusted closes equal available raw closes; both daily API routes agree on
  every OHLCV field. Raw volume convention is explicit in the price receipt.
- The source/manifest/calendar/corporate-action/raw-scale review is separate
  from engine preflight; review booleans are not asserted for quarantined stocks.
- Dated exchange plus IPFT fees replace the old static assumption in this
  opt-in research path. Historical monthly raw-close tick anchors are used,
  including the first April 2025 determination. Strategy and benchmark share
  the same reviewed fee/tick convention. Runtime defaults remain separate.
- DP INR 15.93 is a conservative fixed assumption, not verified historical
  invoices. Held-delivery tax/DP treatment may overcharge same-day stops.
- Frozen input/evidence/config/source/version hashes precede performance. The
  importer rejects changed evidence, path escape and inconsistent raw-unit
  declarations. Original datasets, failed receipts and portfolios are preserved.
- Actual market features and regime pass prefix equality through 31 December
  2024 when later input rows are removed. The repeat blocked Python network
  sockets, and all 12 equity/trade/benchmark/Markdown artifacts plus summary and
  frozen specification are byte-identical. This is causal/repeatability evidence,
  not a proof of every possible bias being absent.
- All scenarios pass cash/position/net-P&L reconciliation, with no borrowing.
- Maintained Windows suite: **451 passed in 49.58 seconds**, using the configured
  Python 3.12 venv through `dailytask.bat test`. Git Bash race/live-order guards
  remain covered; no existing test was skipped or removed. Diff whitespace checks pass.
- Original and main private portfolio file hashes are unchanged. The main
  INR 100,000 simulation remains flat and unprocessed. No broker credentials,
  live orders, trading workflow, paid service, dependency install or GitHub push.

## Private receipts and repeat command

Prepared local manifest:
`E:\AI-Trading-Data\processed\reviewed-tcs-lt-aihpclgh\manifest.json`.
First actual launcher result:
`E:\AI-Trading-Data\results\nsebot\offline-backtest-hd7byn8a\summary.json`.
Repeat/trace/causality/state audit:
`E:\AI-Trading-Data\results\nsebot\market-pilot-audit-vd7k251d\AUDIT.json`.
Additional provider evidence:
`E:\AI-Trading-Data\results\nsebot\tapetide-review-d3f_ykr_\acquisition.json`.

The evidence review used 15 additional Free read-only requests (maximum pages),
leaving 28 calls at that receipt. Neither market replay needed API calls or the
token. The dedicated token file remains ignored/untracked and was not printed.

From the project directory, the already-approved local replay can be repeated:

```powershell
.\dailytask.bat offline-backtest --manifest "E:\AI-Trading-Data\processed\reviewed-tcs-lt-aihpclgh\manifest.json"
```

It creates a fresh SSD result directory. The preparation/audit helpers are saved
outside the repository at `C:\AI-Trading-Bot\prepare_reviewed_tcs_lt_pilot.py`
and `C:\AI-Trading-Bot\audit_reviewed_tcs_lt_pilot.py`. They are local receipts,
not automatic jobs; the audit helper is pinned to this original trial identity.

## Remaining work before a broader claim

RELIANCE's Jio demerger and HUL's KWIL demerger require reviewed spin-off
entitlements/valuation and appropriate holdings/cash accounting. HDFCBANK needs
bonus-aware historical quantities and resolution of the provider action ISIN
`INE040A01018` versus official `INE040A01034`. Do not repair those source records
by assertion or run their current-adjusted integer-share series as historically
executable holdings. Their original data remains quarantined, not erased.

A broader representative, point-in-time universe, more realized signals and a
predeclared evaluation budget are needed before statistical strategy conclusions.
Daily data cannot establish intraday fills, auctions, queue rank, price bands or
the 2024 disaster-recovery sessions' midday order resets. Descriptive chronological
splits are not untouched out-of-sample proof. No Monday/live-use readiness follows.

Implementation changed in this phase: `nsebot/research/historical_execution.py`,
`tapetide_review.py`, the fixed allow-list in `tapetide_fetch.py`, opt-in replay
context in `nsebot/backtest.py`, evidence/raw-scale metadata validation in
`offline_data.py`, dated benchmark/reporting in `offline_backtest.py`, and related
`test_historical_execution.py`, `test_tapetide_fetch.py`, `test_offline_data.py`.
Previous local modifications are retained and uncommitted.
