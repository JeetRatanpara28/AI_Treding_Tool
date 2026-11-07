# Pinned six-file candidate: acquisition pass, quality failure

Reviewed 7 November 2026. The user approved the bounded six-file acquisition.
Only those pinned Parquet files and the provider's licence were downloaded.
No repository clone, dependency installation, provider script, broker access,
market replay, notification or publication was performed.

## Acquisition evidence

- Repository/ref: `aswinv90/indian-market-historical-data` at
  `700081a35486878208da393584c32ea83d6bbabc`.
- Six file sizes and all six Git blob identities exactly match the reviewed
  [metadata snapshot](ALTERNATIVE_DATA_SOURCES_SNAPSHOT.json).
- Market-file bytes: 1,937,696. Licence: 2,668 bytes. Total: **1,940,364 bytes**.
- Actual SHA256 hashes and pinned URLs are preserved in the private acquisition
  manifest. The provider's licence/attribution remains beside the original files;
  none of its dataset or code was copied into the MIT source repository.
- Files were streamed over verified HTTPS with fixed byte limits, no redirects,
  credentials or unpinned fallback. Parquet dimensions were bounded before read.

Private originals and receipt:
`E:\AI-Trading-Data\results\nsebot\aswin-candidate-bhollqoz\acquisition.json`.

## Five-year requested-window inspection

Window: 7 November 2021 inclusive through 7 November 2026 exclusive. All six
series start this window on 8 November 2021 and end on 5 November 2026.
**Every series has a null close on its final row.** There are no duplicate dates
and rows are ordered, but those partial passes do not rescue incomplete bars.
Direct Arrow inspection independently confirmed the final stored `Close` is
null (one Arrow null in each file), rather than a normalization/parser-generated
NaN. Final SHA256 rechecks matched all seven preserved original files.

| Series | Window rows | Invalid bars identified |
| --- | ---: | ---: |
| Nifty 50 | 1,235 | 1: final close missing |
| HDFCBANK | 1,241 | 8: seven zero-volume flat bars plus final close missing |
| HINDUNILVR | 1,240 | 8: same categories |
| LT | 1,241 | 8: same categories |
| RELIANCE | 1,241 | 8: same categories |
| TCS | 1,241 | 8: same categories |

The stock zero-volume/flat-OHLC dates are 18 March 2025, 15 January 2026,
1 May, 28 May, 26 June, 14 September and 2 October 2026. Their close values were
not treated as genuine trading bars. Six of these are closed days in the already
reviewed 2026 exchange calendar. The 2025 date is still unverified against an
official historical calendar and is not automatically called a holiday.

## Calendar and cross-series failures

Against the existing reviewed 2026 calendar, through 6 November:

- All six omit the verified **1 February 2026 Sunday Budget trading session**.
- All six lack **6 November 2026**, which falls after the pinned data's end.
- HINDUNILVR additionally lacks **7 September 2026**, present in the other series.
- Each equity includes six reviewed 2026 closed-day rows absent from the index.
- A 1 February 2025 weekend row exists in these files. Weekend rows were not
  mechanically deleted; 2021-2025 special sessions/calendars remain unverified.

The repository uses Yahoo-derived history, so the observed omissions and
incomplete close are not an independent official correction to the prior vendor
failure. Existing approved official closes are for 6 November, which this source
does not contain: an overlapping official-price reconciliation could not be
performed from those approved files. No independent close PASS is claimed.

## Price basis and identity still require review

Files contain OHLCV and `Adj Close`; stocks also contain dividend/split columns.
Observed `Adj Close / Close` ratios vary by stock (approximately 0.87-1 over the
window), so the two close columns are not interchangeable. Corporate-action
columns do not establish that splits, demergers, dividends and historical share
units are correct. No adjustment or normalization was applied.

File/ticker names identify the intended symbols, but the inspected columns do
not supply an independently reviewed historical ISIN/series chain. Neither name
matching nor a valid Parquet schema certifies the instrument history.

## Disposition and verification

**REJECTED_FOR_BACKTEST.** The existing history preflight rejects the input with
`BACKTEST DATA: index: missing or non-finite OHLCV`. It was not bypassed.

Private offline diagnosis:
`E:\AI-Trading-Data\results\nsebot\aswin-candidate-bhollqoz\quality-diagnosis-gco79uhp\summary.json`.

Original bytes and prior state were preserved. No forward filling, fabricated
volume, source splicing, deletion of source rows, calendar fallback or market
performance run occurred. The helper initially emitted a pandas deprecation
warning for `dayofweek`; its inspection code now uses `day_of_week`. No warning
filter or test expectation was loosened and no unnecessary re-download was made.

The quality problem belongs to these pinned source contents; changing our
assertions would not recover missing real sessions/prices. Repairs require
authoritative missing-session records, reviewed holiday exclusions and consistent
corporate-action/identity/calendar validation, or a separately approved better
source. A shorter explicitly defined research window might remove the incomplete
last day, but cannot by itself repair the internal missing sessions. Preserve
this failed candidate and report rather than marking a reduced intersection as
a complete five-year NSE history.

Runtime/source-engine code was not changed in this acquisition task. Existing
paper-only controls and disabled workflows remain in place; the private
acquisition check verified identical upstream/local portfolio file hashes.
Maintained suite via `dailytask.bat test`: **384 passed in 44.21 seconds**.
New report UTF-8/whitespace and `git diff --check` were checked; no test was
skipped, removed or weakened. No market return/CAGR result is available from
this rejected candidate.
