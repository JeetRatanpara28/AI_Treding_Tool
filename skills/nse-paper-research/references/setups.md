# Candles, indicators and explicit entry/exit hypotheses

Pattern labels describe data, not certain outcomes. Context, confirmation, costs
and out-of-sample evidence determine whether a research rule is useful. Sources
T1-T3 identify subject coverage and the need for objective definitions. The
candidate rules below are experimental specifications, not exchange-endorsed
thresholds or validated buying advice.

## Make chart language measurable

For valid OHLC let `range = high - low`, `body = abs(close - open)`,
`upper = high - max(open, close)`, `lower = min(open, close) - low`. Reject invalid
prices/zero-range division. Use consistent price basis, session and timeframe.

| Family | Specification needed | Context/failure case |
| --- | --- | --- |
| Doji / spinning top | Small body relative to range and both wick ratios. A candidate doji threshold might be 0.10, not a universal constant. | Indecision permits continuation or reversal, not a standalone trade. |
| Hammer / hanging man | Quantify long lower wick/body and short upper wick. | Similar geometry has different names after declines versus advances; a shape does not prove support. |
| Inverted hammer / shooting star | Quantify upper/lower wicks and body. | Confirmation, if required, is unavailable until its later bar completes. |
| Engulfing / harami | Define body containment, strict/equal edges and opposing directions. | Body engulfing is different from an outside bar's whole-range condition. |
| Piercing / dark cloud | Define gap and penetration into the prior body. | Overnight versus intraday continuity differs; do not relax definitions to improve results. |
| Morning/evening star | Define all three bars and final-close confirmation. | Recognition is possible only after the third close. |
| Marubozu / directional bar | Large body/range and bounded wicks. | It can represent exhaustion/news; extension and liquidity still matter. |
| Multi-bar charts | Double tops/bottoms, head-and-shoulders, flags, triangles and wedges need objective pivots, tolerances and triggers. | A pivot using k right-side bars is known k bars later, not on its plotted date. |

Do not retrospectively choose a visually attractive pattern and claim the entry
was known then. Fibonacci/Elliott-wave labels and discretionary lines remain
unverified annotations without reproducible detection rules.

## Indicators by role

- Moving averages lag trends and can whipsaw in ranges.
- RSI is bounded momentum, not an automatic oversold-buy/overbought-sell rule.
  Cross-sectional relative strength against a benchmark is a different quantity.
- ATR measures volatility, not direction; its stop multiplier is a test parameter.
- VWAP needs the actual session reset and available volume; never mix yesterday's
  accumulator or unfinished volume into a completed-session decision.
- MACD/MA filters share inputs; correlated indicators are not independent votes.
  Bollinger extremes do not ensure mean reversion. Specify windows, lags and
  zero-denominator behavior.
- Volume surprises require an earlier baseline; a partial bar is not comparable
  to a full-day threshold without an explicit model.

## Research hypotheses, not active recommendations

| Hypothesis | Entry specification | Invalidation/exit checks |
| --- | --- | --- |
| Trend breakout | Past-only trend, prior-bar resistance, completed breakout, liquidity/event rules and earliest eligible fill. | Initial stop, gaps, time/trailing exit, false breakouts and extended gap entries. |
| Trend-context mean reversion | Quantified decline, longer-term context, maximum holding time and earliest fill. | Continued decline, regime changes, cost-aware bounce/stop/time exit; no improvised averaging. |
| Cross-sectional momentum | Point-in-time universe, ranking/skip window, rebalance schedule and retention band. | Revisions, corporate actions, turnover, concentration and long drawdowns. |
| Opening-range study | Verified hours, complete opening range, subsequent trigger and fresh bars. | Session end, spread/slippage, failed feed; special sessions cannot inherit normal hours. |

State side, decision time, earliest fill, sizing and exit priority BEFORE testing.
A close-based signal cannot assume a guaranteed fill at that same close. If one
OHLC bar touches stop and target, the path is unknown; expose the ambiguity and
use a declared conservative convention, sensitivity range or better data.

Read `nsebot/signals/`, `nsebot/risk/exits.py`, config and research reports before
proposing variants. Upstream findings remain reported until exact code, data and
costs are reproduced. Never deploy an example just because it appears here.

## Complete illustrative rule card

This is an untested educational specification, not a proposed default or current
buy/sell call. Its numerical thresholds are arbitrary research parameters.

- Scope: approved liquid NSE cash-equity universe, LONG daily study. Obtain at
  least the feature warm-up required by the selected EMA/ATR implementation,
  plus evaluation history. A three-month smoke test is not enough to establish edge.
- Information clock: decide only after session t is complete and data validated.
  Define `prior_high = max(high[t-20:t])` and the median prior-20 volume, excluding
  the current bar. Compute EMA20, EMA50 and ATR14 using information through t only.
- Candidate trigger: EMA20 > EMA50; close_t > prior_high; volume_t exceeds 1.5
  times that prior median; close_t is no more than 2 ATR14 above EMA20. This is a
  testable breakout rule, not a general truth that those settings are profitable.
- Entry plan: earliest next eligible session's open, adverse slippage/tick/cost
  assumptions included. Before entering, cancel for invalid data, no liquidity,
  a newly known event exclusion, or a gap more than a specified 2% above signal
  close. The calendar determines the next session; it may be Sunday.
- Invalidation/size: a candidate fixed initial stop is entry minus 2 ATR14_t.
  Verify positive prices, gap/tick restrictions and a supplied risk budget B.
  Apply full cash, fee, portfolio and integer-lot constraints; zero quantity is valid.
- Exit priority: if a later open gaps through the stop, model that adverse open;
  otherwise use the declared stop-fill convention. A completed close below EMA20
  schedules the earliest later eligible exit; a ten-session time exit is another
  specified candidate. Never award a same-close fill merely because the exit
  was discovered at that close.
- News must have its own availability clock. An event learned after signal
  creation may cancel a still-pending entry at its later execution gate; it must
  not be retrospectively used as a feature known at signal creation.
- Evaluation: compare net, matched-window results with buy-and-hold, track every
  variant and expose cost/gap sensitivity. Sparse or negative evidence means reject
  or inconclusive, not parameter changes until a favorable curve appears.

Use the rule card to explain when a hypothetical entry/exit would become eligible.
Do not alter the bot or run this experiment without its separate authorized scope.
