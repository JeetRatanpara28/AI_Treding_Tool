# Backtest preparation and repair receipt

Latest consolidated outcome: [five-stock research result](FIVE_STOCK_RESEARCH_RESULT.md),
including supported Free MCP, complete listed child history and independent raw
entry/fill checks. Older status/counts below are preserved historical snapshots.

Newest follow-up: [corporate-action review and five-stock interval stress](CORPORATE_ACTION_REPAIR.md),
463 maintained tests. Exact raw-OHLC/child-history gates remain incomplete.

Latest: [TCS/LT historical pilot result](HISTORICAL_PILOT_RESULT.md). Source access
and calendar checks progressed beyond this earlier snapshot; the narrower market
pilot finished, while corporate-action accounting for the other three stocks is
still incomplete. Current maintained suite: 451 passed.

For the subsequent offline causality, CSV-import, benchmark and sensitivity work,
see [OFFLINE_RESEARCH.md](OFFLINE_RESEARCH.md). Counts below are the earlier
preparation snapshot, not the latest suite receipt. The user subsequently reports
sending the academic enquiry personally; provider response is still pending.

## Outcome

**Technical regression suite: 353 passed in 40.32 seconds. Market performance:
not available.** The user authorized preparation and historical backtesting, but
there is not yet a sufficient, reviewed local dataset. Do not describe the
synthetic engineering tests as a profitable market backtest or completion of all
research steps. Never tune until the result happens to be positive.

## Reproduced problems and fixes

Changes are limited to `nsebot/backtest.py` and regression coverage in
`tests/test_backtest_safety.py`:

- One-session input reproduced an `IndexError` in report generation. Preflight
  now rejects insufficient index history before simulation state is created.
  Missing columns/rows, unordered/duplicate/non-session dates, invalid OHLCV and
  an empty equity universe also fail clearly. This does not certify calendars,
  rights, historical coverage, liquidity or corporate-action correctness.
- A supplied work folder could silently reload an old swing ledger. Nonempty
  work folders are now refused without modifying their contents.
- Report code forward-filled missing benchmark prices. It now rejects missing
  benchmark sessions instead of inventing a close.
- The launcher's swing capital was ignored by `backtest.main`, which used the
  upstream INR 50,000 default. It now honors `SWING_CAPITAL` (INR 33,333.33 under
  the local launcher); direct upstream default remains unchanged. Invalid
  capital is rejected before constructing the provider or creating output.
- Main output filenames could overwrite an earlier experiment. Each main run
  now uses a new `backtest-*` child directory, including its isolated engine
  state. CSV/Markdown output explicitly uses UTF-8 and exclusive file creation.

No signal threshold, strategy selector, broker integration, risk cap or test
assertion was loosened to obtain a profitable result. Original portfolio and
upstream state are not used as replay work folders.

## Verification and honest data status

The first direct targeted test invocation failed on Windows temp-folder
permissions (8 setup errors, 1 pass). Running the existing `dailytask.bat test`
with its fresh workspace temp directory resolved that environment issue: first
351 passed, then **353 passed** after capital/output fixes. The Git Bash race
test remains part of the maintained suite. No tests were skipped or removed.

New offline checks cover short/malformed history, preserved existing files,
deterministic cash conservation in a synthetic no-signal replay, missing
benchmark rejection, isolated repeat outputs and invalid-capital failure before
provider construction. Synthetic business-day fixtures are not NSE calendars.

Actual local-data preflight was run without network or a market replay:

| Available dataset | Result |
| --- | --- |
| User-supplied official 6 November snapshot | 1 session: insufficient for the 200-session warm-up |
| Earlier approved Yahoo cached usable CSVs | 62 sessions: insufficient; these CSVs are not the raw vendor payload |
| Same cached CSVs after explicit complete-row check | 62 sessions: still insufficient |

Private receipt:
`E:\AI-Trading-Data\results\nsebot\backtest-readiness-89bt3cju\summary.json`.
The earlier receipt is preserved; its misleading "raw sample" label was corrected
in this newer receipt. Existing portfolio file hashes matched before and after
the read-only readiness check. No source files were overwritten or spliced.

## Free/student-source review

- [NSE academic access](https://www.nse.in/static/research/initiatives-data-for-research)
  is application-based; the [linked form](https://www.nse.in/research/data-seeking-form)
  requires institution and applicant details. Student status does not guarantee
  approval. A generic [application draft](NSE_ACADEMIC_DATA_REQUEST_DRAFT.md) is
  available; applicant-specific material belongs only in ignored local files.
- [Twelve Data's student offer](https://twelvedata.com/students) is a discount,
  not evidence of free NSE history. No paid service/account was started.
- [TejHQ data terms](https://tejhq.dev/data-terms) permit personal backtesting and
  bounded automated use of its own service, but explicitly state it has no
  exchange licence/clarification and cannot grant exchange rights. It does not
  publish Nifty index values. Not selected as a fully verified source; no market
  files were acquired from it. Code MIT is not a market-data licence.
- Earlier candidates/limits remain documented in [the pilot plan](HISTORICAL_DATA_PILOT.md).

## Steps still required before a meaningful result

1. Complete and review the academic access request (or establish another suitable
   free source). Submission is a separate external action requiring applicant
   confirmation/approval; no application or email was sent.
2. Acquire the bounded approved equity/index history privately on SSD, retain raw
   provenance/hashes and reconcile sample dates with official reports. Do not
   silently replace unavailable Nifty with an equity basket or fabricate bars.
3. Validate historical calendars, symbol/ISIN history, missing dates, corporate
   actions and consistent adjustment/return conventions. A five-stock sample
   selected today is an engineering pilot with survivor-selection limitations.
4. Freeze the research specification before inspecting performance. Use the
   swing sleeve's INR 33,333.33; keep the other sleeves unchanged. Daily data
   cannot establish intraday performance. The default swing strategy needs 200
   warm-up sessions, reducing the evaluated period inside a five-year acquisition.
5. Review execution timing (including same-close exit assumptions), missing bars
   and liquidity constraints, dated historical charges and slippage sensitivity.
   Existing static costs/5-bps fills are assumptions, not calibrated execution.
   [Current cost schedule](https://zerodha.com/charges) and a documented
   [2024 change](https://zerodha.com/marketintel/bulletin/391488/revision-in-transactions-charges-from-1st-october-2024)
   show why today's rates must not be claimed exact across five historical years.
6. Run isolated deterministic replay and matched buy-and-hold comparisons; check
   cash/positions/cost reconciliation, drawdown, exposure, number of trades and
   sensitivity. Audit chronological split boundaries and signal/fill causality;
   the existing report's chronological split alone is not proof of untouched
   out-of-sample evidence, and open final positions need explicit treatment.
7. Reject technically invalid results and repair the cause. Valid poor returns
   are evidence against the strategy, not permission for unlimited parameter
   searches. Any new hypothesis needs a recorded trial budget and fresh evaluation.

No validated CAGR, win rate, drawdown or profit is available yet. No market-data
download, paper-cycle order, live access, account signup, email or GitHub push
occurred during this preparation. This is a partial preparation receipt, not a
claim that the requested complete backtest has finished.
