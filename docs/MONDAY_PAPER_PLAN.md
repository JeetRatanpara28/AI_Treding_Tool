# Monday 9 November 2026: proposed paper observation plan

Prepared 7 November 2026, Europe/Paris. This is a reviewable plan, not an
activation or a claim that five-year validation is complete. Real capital INR 0.

Updated after [the five-stock engineering research](FIVE_STOCK_RESEARCH_RESULT.md).
Current maintained suite:473 passed. The single observed trade lost money; this
does not support strategy deployment. Monday's feasible scope is manual paper
observation, timestamp/data validation and an isolated research journal.

## Practical decision

Separate Monday's manual market-observation exercise from validation of the
Python strategy. Native TradingView chart strategies and its Paper Trading
simulator are documented platform features; exporting/scraping TradingView
data into our Python engine is a different use and is not part of this plan.

Sources reviewed:

- [TradingView native strategies/backtesting/forward testing](https://www.tradingview.com/support/solutions/43000562362-what-are-strategies-backtesting-and-forward-testing/)
- [TradingView Paper Trading](https://www.tradingview.com/support/solutions/43000516466-paper-trading-main-functionality/)
- [NSE market timings and holidays](https://www.nseindia.com/resources/exchange-communication-holidays?apiversion=v2)

Do not present a Pine prototype or manual simulator as the fully validated
Python portfolio engine. Simulator results are hypothetical, not actual fills
or proof of profit. Do not copy TradingView's marketing claim of identical
execution into our research conclusions.

## Schedule and data constraints

The reviewed local NSE cash calendar marks Monday 9 November as a normal
session, 09:15-15:30 IST, corresponding to **04:45-11:00 Paris CET**.
Recheck official notices before the session. Tuesday 10 November is a reviewed
trading holiday. The local calendar review expires after that date.

Sunday 8 November has a verified special Muhurat session. A Monday daily
Python cycle would need the completed Sunday bar; Friday-only data is not a
valid freshness substitute. Local daily readiness policy is 16:15 IST / 11:45
Paris CET, not a promise that a vendor will have finalized its data.

For Sunday8November, continuous trading starts14:20IST /09:50Paris. Non-CAS
securities close15:30IST /11:00Paris; CAS continuous trading closes15:15IST,
with auction matching through15:35IST /11:05Paris. These special-session times
were rechecked against [NSE CMTR76941](https://nsearchives.nseindia.com/content/circulars/CMTR76941.pdf).
Monday's normal observation window is04:45-11:00Paris; allow for any applicable
closing auction and recheck exchange notices. The after-close research slot is
11:45Paris or later, only after required bars pass freshness/completeness checks.

Do not wake or run an unattended bot just to meet these times. If the user is
unavailable at04:45, an after-close review is a valid start. No automatic order,
webhook, background news job or trading schedule is enabled by the GitHub push.

## Bounded manual paper exercise

1. Keep real brokers disconnected, live transports disabled and existing local
   portfolio unchanged. Use a separate virtual experiment/journal; do not reset
   an existing simulator account or its history. Nominal experiment capital is
   INR 100,000, with the established sleeve allocation recorded separately.
2. Inspect a small fixed NSE cash-equity watchlist in the normal chart UI.
   Check exchange identity, timezone, session, quote timestamp, entitlement and
   delay. No subscription or real-time coverage is assumed. If the necessary
   view is paid/unavailable, stop that route without upgrading.
3. Use native simulated/manual actions only, with rules written before any
   entry. Otherwise remain in observation mode. No broker login, credentials,
   webhook, automatic order route or transfer to the Python runner.
4. Record the decision time, available information, hypothetical entry/exit,
   invalidation, size, fees/slippage assumptions and any missing/stale data.
   Do not invent fills or treat a displayed close as a historically executable
   same-close decision.
5. Review process correctness and gaps after the session. A successful first
   day means the observation/recording process worked, not that a strategy has
   a demonstrated positive edge. No setup or no paper trade is a valid outcome.

## Python research track

- Current maintained suite:473 passed; actual five-stock interval stress and
  corporate-action benchmark evidence are in [FIVE_STOCK_RESEARCH_RESULT.md](FIVE_STOCK_RESEARCH_RESULT.md).
  Synthetic/causality contracts remain in [OFFLINE_RESEARCH.md](OFFLINE_RESEARCH.md).
- The historical Free MCP path works for bounded JIOFIN/KWIL research acquisition.
  The Free REST API currently returns `api_access_not_in_plan`; no upgrade. The
  MCP client is not yet a general five-stock live/daily provider for the bot.
- The production daily data class is still YahooProvider. Its earlier missing
  final bar remains a failed source check, not repaired by a successful historical
  MCP download. Keep daily cycles blocked when the required session is stale.
- Before any separately approved Python forward-paper cycle: implement/review
  a read-only daily provider with source, symbol, calendar, price-unit, bar-finality
  and quota checks; validate the Sunday8November bar and all required previous
  history; use fresh isolated forward-research state, never the existing ledger.
- Historical discretionary exits are causal next-open. The older daily runtime
  retains a same-close convention; align and regression-test decision/queue/fill
  timing before claiming it matches the audited replay. Intraday is not validated
  by daily/weekly MCP data. Do not start swing/intraday/momentum commands by default.
- General held/pending capital-event execution still fails closed. Independent
  full parent raw-OHLC verification, source revisions, historical cost assumptions,
  and broader point-in-time sample/statistical evidence remain incomplete.
- The downloaded six-file candidate remains rejected; see
  [ASWIN_DATA_REVIEW.md](ASWIN_DATA_REVIEW.md). It lacks verified sessions,
  contains holiday/zero-volume rows and has a missing final close.
- An explicit source licence can authorize its stated personal research uses;
  a separate direct NSE letter is not a universal prerequisite for every
  provider. Provider rights/conditions and data quality still need assessment.
- A narrower historical window is possible only after its calendars, identities,
  adjustments and actual gaps are reviewed. Changing the end date does not
  repair internal omissions. A shorter study must be labelled as such.
- Legitimate market-data APIs are another documented route: for example,
  [Upstox historical data](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data/)
  requires an access token. This explains an available developer route; it is
  not a proposal to violate this project's no-broker-credentials rule.
- No paid source, new download scope, application submission, account login,
  production paper order or GitHub push is authorized by this document.

Monday's complete validated Python market backtest is **not promised**. The
feasible fallback is a bounded manual/native paper observation exercise while
the source-validation track continues. No account or session was started here.

## Owner inputs and later sequence

The owner selected **04:45-05:15Paris on Monday9November2026** (09:15-09:45IST).
This is a manual paper-observation window, not an order-execution appointment.
At04:30-04:45: connect the SSD, inspect offline portfolio status, recheck official
session notices and the free chart's exchange/timezone/delay labels. During the
selected slot: observe the same five symbols, record source/timestamp/delay and
any missing data in a separate private journal; no automatic order/runner dispatch.
At05:15: record gaps and stop the observation; do not create unattended exposure.
Completed daily-bar research can be reviewed after11:45Paris or when available.

Still useful: confirmation the external SSD will be connected and a free
timestamped NSE chart view is available. No broker account or credentials.
Any NSE academic-data reply can be placed privately in `local_research/`; its
absence does not prevent the existing permitted Free MCP research.

Next engineering order: current-bar/source validation and causal forward-paper
timing; capital-event holdings/receivables/credit-date handling; fuller raw-price
and point-in-time-universe checks; a separately frozen broader baseline study;
then a local results dashboard. AI/ML comes after a robust baseline, not before.
Weak returns are retained, not fixed by unlimited tuning. Dataset downloads,
paper-cycle execution and any later GitHub publication retain their own scope
and approval requirements; Monday planning alone does not activate them.
