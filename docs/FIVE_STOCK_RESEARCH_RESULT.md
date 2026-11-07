# Latest five-stock research result - 7 November 2026

**All five original stocks have now been included in a repeated, cash-reconciled
engineering stress replay. Corporate-action benchmark quantities, raw entry
verification and complete listed child histories are implemented and checked.
The strategy still produces only one closed trade and a negative net return.
This does not establish an edge or complete strict raw-OHLC certification.**

Earlier [TCS/LT results](HISTORICAL_PILOT_RESULT.md), [interval specification](FIVE_STOCK_INTERVAL_SPEC.md)
and [first corporate follow-up](CORPORATE_ACTION_REPAIR.md) are preserved. This
page supersedes their earlier child-history/API-blocked status, not their frozen
trial identities. No strategy/risk/sizing parameter was tuned to rescue returns.

## Completed work

1. **Free data route repaired:** the actual REST response identifies the account
   as Free, with notice `api_access_not_in_plan`, REST test allowance0. The issue
   was not a malformed token or a quota parser needing relaxed validation. The
   provider explicitly leaves MCP access unchanged. Supported Free MCP works
   with the same locally stored token; no Enterprise/paid plan or REST bypass.
2. **Bounded MCP client:** fixed official host, no redirects/.netrc/proxy fallback,
   only `get_price_history`/`get_adjustment_factors` for JIOFIN/KWIL, maximum12
   tool attempts, checksum cache and decoded/nested credential-reflection checks.
   No Tapetide portfolio/watchlist tools, broker login or configuration changes.
   The remaining account quota is not independently exposed/verified here;
   server quota errors stop the client. Do not report old28 calls as current.
3. **Complete listed histories:** JIOFIN798 sessions21Aug2023-6Nov2026 across7
   price pages, KWIL179 sessions16Feb2026-6Nov2026 across2. Exact independent
   calendar match, complete raw closes, latest official closes match. Both child
   histories equal their raw price scale; no in-listed-window quantity event was
   found. MCP truncates its result body even for days=2000; top-level truncation
   metadata/cursors were respected instead of accepting the latest120 rows as
   full history. Eleven successful market-tool calls total:4 initially,7 later;
   the initial4 were reused from cache during completion.
4. **HDFCBANK identity/bonus:** provider ISIN error is preserved and explicitly
   overridden only in reviewed local event evidence with officialINE040A01034.
   NSE FAOP69840 confirms26Aug2025/1:1. Existing Bank holders do not get the
   HDFC Ltd42:25 merger ratio. Passive benchmark shares correctly double4->8.
5. **Demerger entitlements:** RELIANCE2 initially grants JIOFIN2, later parent
   bonus doubles RELIANCE2->4 without doubling JIOFIN. HUL2 grants KWIL2.
   Final holdings also contain TCS2 and LT3. All child shares stay held; no
   unlisted or uncleared share is sold and no imaginary cash dividend is booked.
6. **Independent raw verification:** five bounded official daily reports cover
   the exact benchmark entry session29Aug2022, actual LT entry2Feb2024/exit
   13Feb2024 and demerger sessions20Jul2023/5Dec2025. Nine symbol/session
   comparisons pass: raw closes equal provider raw closes and all official
   opens/highs/lows lie inside the declared stress intervals. Benchmark buys now
   use exact official opens instead of interval estimates. Actual strategy fills
   and fees reproduce independently in all three slippage cases.
7. **Daily benchmark ledger:** actual raw closes are used on every listed day;
   a missing listed quote fails rather than being filled. Before listing, an
   unlisted entitlement receivable uses an explicitly labelled fixed discovery
   mark (JIOFIN261.85, KWIL40.20), derived from previous parent raw close minus
   official ex-date discovery open. These are nontradable valuation assumptions,
   not child traded prices. A separate quoted-only equity series remains missing
   in those70 sessions; underlying price tables are never filled or modified.
8. **Accounting/repeat/causality:** full source/config/code hashes precede each
   trial, all scenario ledgers reconcile with no borrowing, repeats and feature/
   regime/benchmark prefixes agree. Original/main portfolio hashes are unchanged.
   Every capital-event date actually had zero affected strategy positions or
   pending entries. A future affected holding/order still stops the engine
   rather than pretending a general credit-date trading ledger exists.

## Preserved performance

Capital INR33,333.33 swing-only. Universe RELIANCE,TCS,HDFCBANK,HINDUNILVR,LT.
Input1,241 reviewed sessions, warm-up200. Evaluation26Aug2022-6Nov2026:
**1,041 sessions**. The other INR66,666.67 allocations are not backtested here.

| Slippage each leg | Strategy equity | Strategy net return | Net P&L | Closed trades | Benchmark terminal equity | Benchmark return |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 5bps | INR33,012.45 | -0.9626% | INR-320.88 | 1 | INR38,879.70 | +16.6391% |
| 10bps | INR33,002.40 | -0.9928% | INR-330.93 | 1 | INR38,865.83 | +16.5975% |
| 25bps | INR32,972.25 | -1.0832% | INR-361.08 | 1 | INR38,823.88 | +16.4716% |

Only LT generated complete signals (three); two failed the existing INR8,000
minimum allocation rule. The single filled/closed trade lost money. No strategy
position crossed a reviewed capital event; all scenarios finished flat. Rare
signals in a tiny survivor-selected sample give insufficient statistical evidence.
The existing breadth feature needs ten stocks and is inactive here.

Strategy5bps max drawdown1.1207%, paid costsINR38.43. Most capital remained in
cash. Benchmark exposure is much larger, so its greater return is not a matched-
risk claim. Dividends/optional tenders/terminal liquidation/income taxes are not
included. Dated exchange/IPFT and ticks are reviewed; fixed DP15.93 and held-
delivery treatment are conservative research assumptions, not exact invoices.

The full marked benchmark model has max drawdown22.6594% in the5bps case, but
this **includes70 sessions valued with indicative receivables**. It is not fully
observed traded-market risk; that metric remains null. From16Feb2026 onward,
all held names have actual quotes for179 sessions: that segment's max drawdown
is17.7126% and return-6.9914%. These segment metrics are not full-period returns.

## Evidence locations, all private

- Original five-stock stress/repeat:
  `E:\AI-Trading-Data\results\nsebot\five-stock-audit-68orv7od\AUDIT.json`.
- Complete child-history receipt:
  `E:\AI-Trading-Data\results\nsebot\entitlement-mcp-complete-6f_2szzj\acquisition.json`.
- Independent official raw snapshots:
  `E:\AI-Trading-Data\results\nsebot\targeted-raw-official-qhkdeh9a\receipt.json`.
- Final benchmark, direct fill/cost checks, prefixes and repeatability:
  `E:\AI-Trading-Data\results\nsebot\entitlement-benchmark-tmzp81bh\AUDIT.json`.
  CSV wealth curves keep marked/quoted-only values and receivable amounts separate.
- Original REST-plan-denial attempt remains at
  `E:\AI-Trading-Data\results\nsebot\entitlement-evidence-4orhdnxq\acquisition.json`;
  its zero market calls were not overwritten or reclassified as a success.

Local reproducible manual helpers are under `C:\AI-Trading-Bot`:
`run_five_stock_interval_pilot.py`, `complete_entitlement_mcp_history.py`,
`verify_targeted_raw_bhavcopies.py`, `finish_five_stock_benchmark.py`.
They are not scheduled jobs. Historical pinned audit helpers should retain their
original trial identities; a new code snapshot requires a fresh receipt.

## Verification and practical limits

Final maintained Windows suite: **473 passed in53.76 seconds**, through
`dailytask.bat test` and the exact configured Python3.12 venv. `git diff --check`
and changed/untracked UTF-8 whitespace checks pass. Final main simulation status
remains INR100,000 cash with zero open/pending/closed/processed positions/sessions.
Final secret check scanned304 publishable/new-artifact files: zero exact-token
matches; the dedicated token file is untracked. An initial transient read error
was followed by a completed read-only scan with no unreadable files.
New coverage includes raw uncertainty bounds, capital-event exposure refusal,
entitlement ordering/fractions, MCP write/host/date/budget guards, cached paging,
credential reflection and quoted-versus-indicative receivable valuation. Earlier
assertions remain intact. No paid tool, dependency install, live trade, main
portfolio cycle, account/watchlist write, email or GitHub push occurred.

Remaining limitations are explicit:

- The complete original parent raw open/high/low series has not been independently
  supplied. Sample official checks validate the observed trial, not every candle.
  The interval path is a labelled engineering stress model; strict source gates
  remain closed for an exact raw-OHLC certification. Current MCP serves adjusted
  daily/weekly prices, not a raw intraday-candle feed.
- A general strategy holding/pending-order ledger through a capital event is
  deliberately unsupported and fail-closed. This trial had no such exposure;
  its passive hold-to-end entitlement ledger does not prove active-event fills,
  cost allocations, fractional cash-in-lieu or credit/listing-date sale handling.
- Neither the one-trade result nor the marked benchmark proves profitability,
  an absence of every bias, intraday performance or readiness for automated use.
  A broader point-in-time sample and a separately frozen research trial are
  required before revising strategy rules. Valid poor returns remain evidence.

## Primary access references

- [Supported MCP token connection](https://developers.tapetide.com/agents/mcp-clients/other/)
- [Historical MCP research and its daily/weekly limits](https://tapetide.com/mcp/guides/backtest-indian-stocks-ai)
- [NSE HDFC bonus/ex-date](https://nsearchives.nseindia.com/content/circulars/FAOP69840.pdf)
- [Official HDFC ISIN](https://www.hdfc.bank.in/about-us/investor-relations/adr)
- [HUL entitlement FAQ](https://www.hul.co.in/files/faqs-on-allotment-of-kwil-shares-pursuant-to-the-scheme-of-demerger.pdf)
- [NSE JIOFIN listing/identity](https://nsearchives.nseindia.com/web/sites/default/files/2023-08/PR_list_18082023.pdf)
- [NSE KWIL listing/identity](https://nsearchives.nseindia.com/corporate/HINDUNILVR_13022026140635_SEIntimationKWIL13022026signed.pdf)

New project source in this follow-up: `corporate_replay.py`,
`benchmark_entitlements.py`, `tapetide_mcp.py`, `fetch_entitlements.py` under
`nsebot/research/`, the fixed entitlement allow-list in `tapetide_fetch.py`,
their regression tests and these research documents. Previous changes remain
preserved, uncommitted and unpublished.
