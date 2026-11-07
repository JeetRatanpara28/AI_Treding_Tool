# Corporate-action follow-up - 7 November 2026

Latest: [five-stock research completion](FIVE_STOCK_RESEARCH_RESULT.md). The
REST issue was identified as Free-plan access denial; supported Free MCP supplied
complete listed child histories. Official raw entry/fill snapshots and the daily
benchmark ledger now exist. This page preserves the earlier endpoint-only stage.

**Completed: explicit identity review, terminal bonus/spin-off accounting, all-five
raw-share interval stress replay and repeat audit. Still incomplete: strict
observed-raw-OHLC replay, child daily benchmark history and general trading
across capital events. Do not describe this as a fully validated five-stock bot.**

## Concrete changes and actual outcomes

`nsebot/research/corporate_replay.py` adds a separate, explicitly labelled research
path. The [frozen specification](FIVE_STOCK_INTERVAL_SPEC.md) precedes its results.
It does not loosen the original strict CSV importer or change strategy thresholds.

- Parent quantities use raw share units rather than today's adjusted integer
  shares. Raw closes and unadjusted volume come from preserved provider receipts.
- The provider supplies adjusted OHLC rounded to cents, plus raw close, not exact
  raw open/high/low. The separate path computes conservative intervals under an
  explicit uniform-adjustment/nearest-cent assumption. Buy opens use the upper
  bound; sell/gap opens and stop lows use the lower bound. This is stress testing,
  not proof of an exact executable historical path or worst possible portfolio.
- Absolute price/liquidity checks use raw prices/volumes. Continuous indicators
  translate into decision-close raw units. All-five prefix features and regime
  agree through31Dec2024 after later rows are removed from the same vendor snapshot.
- Any affected position or pending order on a capital-event date stops the run.
  All four dates in each of three cases actually had **zero affected exposure**.
  There was no silently cancelled order, altered holding or ignored entitlement.
  This proves this trial did not cross an unsupported event; it does not implement
  a general strategy entitlement/credit-date ledger.
- Benchmark quantity changes are chronological. Initial quantities:
  HDFCBANK4, HUL2, LT3, RELIANCE2, TCS2. Terminal quantities:
  HDFCBANK8, HUL2, LT3, RELIANCE4, TCS2, **JIOFIN2 and KWIL2**.
  RELIANCE's later bonus correctly does not multiply its already-separated JIOFIN.
  All shares remain held, so no unlisted/uncleared shares are sold.
- The official user-supplied6Nov2026 EQ bhavcopy confirms terminal ISIN/date/close
  for all seven names. JIOFIN closes at INR231.20, KWIL at INR38.28. These are
  observed terminal marks, not inferred daily prices or fabricated cash proceeds.
- HDFCBANK's provider action ISIN INE040A01018 remains unchanged in original files.
  The local reviewed mapping explicitly uses official INE040A01034, with symbol,
  face value and primary bonus circular evidence. Existing Bank holdings do not
  receive the42:25 HDFC Ltd merger exchange ratio.

### Preserved results: 26Aug2022 through6Nov2026, 1,041 evaluated sessions

Capital INR33,333.33, unchanged swing configuration, all five original names.

| Slippage each leg | Strategy final equity | Strategy net return | Closed trades | Endpoint buy-and-hold wealth | Endpoint return |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5bps | INR33,012.45 | -0.9626% | 1 | INR38,879.60 | +16.6388% |
| 10bps | INR33,002.40 | -0.9928% | 1 | INR38,865.43 | +16.5963% |
| 25bps | INR32,972.25 | -1.0832% | 1 | INR38,823.68 | +16.4710% |

The only closed trade remains LT, so its unchanged-unit result matches the
earlier TCS/LT trial. No new closed-trade sample or reliable strategy edge was
established. Returns and risk differ from the two-stock benchmark because the
universe/allocations differ; do not compare them as a strategy improvement.

Endpoint benchmark wealth includes remaining cash, parent shares and spin-offs;
it excludes dividends, optional tenders and final liquidation costs. **Benchmark
daily curve/drawdown/Sharpe are null**, because daily child prices are unavailable.
No child prelisting mark, forward fill, zero price or invented return was used.
The strategy's5bps max drawdown is1.1207%; most capital remained in cash, so its
risk/exposure is not comparable with continuous buy-and-hold investment.

## API failure handled safely

The bounded child-evidence downloader uses only fixed JIOFIN/KWIL read-only
price/action routes, with maximum documented pages and the existing protected
transport/cache. Its prerequisite quota response returned `data:null`. A second
uncharged schema diagnosis confirmed null, not a recognized Free-plan allowance.
It stopped with **zero market requests**. No retry loop, paid upgrade, alternate
credential or quota bypass was used. The previously reported28 remaining calls
are a historical receipt, not the currently verified quota.

User dashboard status was requested without asking for a token/password. A
working verified Free quota response is needed before requesting child history.
Do not change `null` into assumed quota or continue authenticated downloads blind.

Failure receipt:
`E:\AI-Trading-Data\results\nsebot\entitlement-evidence-4orhdnxq\acquisition.json`.

## Verification

- Maintained Windows suite: **463 passed in51.64s**, exact configured Python3.12
  venv via `dailytask.bat test`; Git Bash race/live-order guards retained.
- New tests check uncertainty bounds, invalid raw closes, ex-date entitlement,
  parent/child bonus ordering, fractional-entitlement failure, no-mutation event
  guards, adverse fills, prefix equality, offline replay and null-quota refusal.
- A new synthetic end-to-end test caught JSON serialization of configuration
  times; serialization now preserves the time strings, matching existing research
  receipts. The test was not weakened or removed; rerun passed.
- Actual all-five run/repeat blocked Python sockets, reconciled cash/position/net
  P&L in all cases, and produced byte-identical summaries/specs and nine curve/
  trade/trace files. All12 event-exposure checks passed. Ended flat, no borrowing.
- Original/main private portfolio hashes matched before/after. No token or broker
  credential was printed, no live transport/automatic schedule enabled, no paid
  service installed, no commit or GitHub push made.

Private audit:
`E:\AI-Trading-Data\results\nsebot\five-stock-audit-68orv7od\AUDIT.json`.
This identifies the two result folders and hashed local source review. Reproducible
local helper: `C:\AI-Trading-Bot\run_five_stock_interval_pilot.py`; it is an
explicit manual offline audit, not a scheduled trading job.

## What remains and why

1. **External data gate:** exact independently observed raw OHLC and child daily
   history. Cached adjusted OHLC plus raw close cannot establish exact raw opens/
   highs/lows across unquantified demergers. The new interval model does not remove
   that limitation; the original strict gate remains closed for those inputs.
2. **General event execution:** before testing a different run that actually holds
   parent positions/pending orders across an event, implement/review cost allocation,
   receivables, allotment/credit/listing restrictions, pending-order treatment,
   protective-stop changes and fractional cash-in-lieu. Current run fails closed
   there; do not call the terminal passive benchmark a trading ledger.
3. **Research evidence:** more than one realized trade and a predeclared broader
   point-in-time sample are needed before a statistical conclusion. Do not tune
   the current sample until the result becomes positive.

## Primary identity/event references

- [NSE HDFCBANK1:1 bonus/ex-date26Aug2025](https://nsearchives.nseindia.com/content/circulars/FAOP69840.pdf)
- [HDFC official ordinary-share ISIN](https://www.hdfc.bank.in/about-us/investor-relations/adr)
- [HUL1:1 KWIL entitlement FAQ](https://www.hul.co.in/files/faqs-on-allotment-of-kwil-shares-pursuant-to-the-scheme-of-demerger.pdf)
- [NSE KWIL listing16Feb2026 and identity](https://nsearchives.nseindia.com/corporate/HINDUNILVR_13022026140635_SEIntimationKWIL13022026signed.pdf)
- [NSE JIOFIN listing21Aug2023 and ISIN](https://nsearchives.nseindia.com/web/sites/default/files/2023-08/PR_list_18082023.pdf)
- [RIL2023-24 report: Jio entitlement](https://www.ril.com/sites/default/files/2024-08/RIL_ANNUALREPORT_2023-24.pdf)
- [RIL2024-25 results:1:1 bonus28Oct2024](https://rilstaticasset.akamaized.net/sites/default/files/2025-04/25042025_Media_Release_RIL_Q4_FY2024_25_Financial_and_Operational_Performance.pdf)
