# Tapetide five-year acquisition receipt

Latest access/results: [five-stock research result](FIVE_STOCK_RESEARCH_RESULT.md).
Current Free REST access is denied by the provider; supported Free MCP was used
successfully for child histories. Do not assume earlier REST access/quota persists.

Subsequent result: a narrower TCS/LT historical pilot and repeat audit are now
complete. See [HISTORICAL_PILOT_RESULT.md](HISTORICAL_PILOT_RESULT.md). The receipt
below preserves the earlier acquisition stage; the full five-stock study is pending.

Date: 7 November 2026. **Free API access confirmed; preliminary data checks
passed. No market backtest or order was run.** The user saved a data-service
token locally and explicitly authorized careful use, preferring the largest
documented useful history per request. This superseded the earlier one-day-only
smoke-test proposal for the same five equities and Nifty 50.

## Scope and efficiency

- User-approved universe: RELIANCE, TCS, HDFCBANK, HINDUNILVR, LT and Nifty 50.
  Window: 7 November 2021 through 6 November 2026 inclusive.
- Verified account plan: `free`; 50 available calls before acquisition.
- Stock requests used the documented five-year maximum window and 5,000-row
  page limit. Each returned 1,241 sessions in one page. Nifty used 1,000-row
  pages and required two pages. No weekly-series substitution.
- **7 market requests**, plus the read-only uncharged quota check, acquired
  **7,446 total daily rows**, 1,241 per series. Actual dates are 8 November 2021
  through 6 November 2026. The daily counter afterward showed 43 remaining.
- Full raw response fields are retained: stock delivery percentages and index
  turnover/valuation fields remain available for later research, alongside OHLCV.
  Maximum page size does not invent more sessions than exist in the date window.
- No unrelated symbols or news were pulled simply to exhaust quota. There is a
  local ceiling of 20 market calls, four pages/series and 2 MiB/response. No
  automatic retry, paid/trial fallback, endpoint substitution or redirect.

Private first-run receipt:
`E:\AI-Trading-Data\results\nsebot\tapetide-history-ge4j6bog\acquisition.json`.
Raw HTTP cache with SHA256 sidecars:
`E:\AI-Trading-Data\results\nsebot\tapetide_http_cache`.

A second acquisition verified all seven market pages came from the checked
cache: **zero additional market requests**. It only refreshed the uncharged
quota check. Its receipt is
`E:\AI-Trading-Data\results\nsebot\tapetide-history-u4ihgr2z\acquisition.json`.
This is a frozen historical cache; later source corrections require separately
reviewed refresh logic, not silent overwriting or repeated download attempts.

## Actual preliminary quality result

**PRELIMINARY_QUALITY_PASS** in the offline receipt:
`E:\AI-Trading-Data\results\nsebot\tapetide-history-ge4j6bog\quality-rukkju60\summary.json`.
Candidate CSVs alongside it preserve missing values and do not assert completed
corporate-action or source-rights certification.

- All six have identical, ordered, unique session dates and complete OHLC prices.
- Each equity has finite, positive volume and valid OHLC bounds throughout the
  requested window. No equity bar was filled, fabricated or removed.
- All six exactly match the **210** reviewed 2026 sessions through 6 November,
  including Sunday 1 February Budget trading. HINDUNILVR's 7 September is present.
  There are no rows on reviewed 2026 closed days.
- The 6 November OHLC **and volume** for all five equities and Nifty match the
  already supplied official NSE cash/index reports on the compared current-day
  basis. No extra API calls were needed for this comparison. Latest official
  ISINs were recorded; this does not establish the full historical identity chain.

Nifty has unavailable volume on 6/10/11 April 2023, 12 November 2023,
18 May 2024 and 1 February 2026; its OHLC is complete on those dates. The initial
generic preflight rejected those six optional values. Inspection of the swing
replay's consumers confirmed the index is used for prices/regime/benchmark, not
volume. The **research-only** validator now permits absent index volume while
keeping every OHLC price and equity volume mandatory. Negative/infinite index
volume remains rejected. Missing index volume is retained as missing, not zero.
The original failed receipt (`quality-67yr8f8x`) is preserved as evidence.
Runtime freshness checks and other volume-dependent consumers were not relaxed.

## Token and request handling

- Dedicated ignored file: `local_research/tapetide.env`; it is not tracked.
  No broker credential file, account login or order transport was accessed.
- Token is read into process memory and sent only as the authentication header
  to the fixed `https://api.tapetide.com` read-only route allow-list. No redirects,
  arbitrary next-page URLs, proxy/.netrc fallback, token prints or header logs.
- HTTP errors are sanitized. Literal and JSON-escaped credential reflection is
  rejected before response caching or normalized output. Nonfinite JSON numbers,
  oversized responses, bad pagination and damaged cache hashes stop the fetch.
- Final local scans found the actual token absent from publishable project files
  and downloaded receipts/cache. No token value or prefix fragment was shown.
- Independent read-only code review found no blocking secret-handling issue.
  The reviewer did not read the real token or make authenticated requests.

## Verification and remaining work

Maintained suite: **407 passed in 44.58 seconds**, using the configured Python
3.12 venv and existing `dailytask.bat test`. New fake-transport tests cover cache,
quota, redirect, error/secret and pagination guards. Additional tests establish
that absent unused index volume leaves replay results unchanged while missing
index prices, invalid volumes and missing equity volume still fail. No existing
test assertion was bypassed, skipped or removed.

Private simulation remains INR 100,000.00 cash with zero positions, pending
entries or processed sessions. Existing upstream/local state and earlier failed
datasets were preserved. No paid service, dependency installation, account or
watchlist update, notification, trade, commit or GitHub push occurred.

Before a meaningful market-performance conclusion, still review official
2021-2025 sessions, historical symbol/ISIN chains, split/bonus/demerger/rights
factors and historical share/volume units, dated costs/ticks and the price-only
benchmark convention. A five-year download includes 200 warm-up sessions, so
the eventual evaluated period is shorter. Preliminary acquisition/price checks
must not be presented as a completed bias-controlled or profitable backtest.

Implementation: `nsebot/research/tapetide_fetch.py`; fake transport coverage:
`tests/test_tapetide_fetch.py`. Research index-volume contract and regression
cases changed in `nsebot/backtest.py` / `tests/test_backtest_safety.py`.
