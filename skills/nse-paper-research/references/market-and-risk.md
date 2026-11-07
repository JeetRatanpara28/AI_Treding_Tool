# Market mechanics and risk decisions

## Check context

NSE's public syllabus covers charts, indicators, strategy and risk/psychology;
it does not validate a profitable rule here (T1 and R1-R3 in `sources.md`).
Establish symbol/ISIN, equity series, liquidity, horizon and timestamps. Verify
sessions: weekends are not always closed and mock sessions are not settled trades.
Check current instrument tick/lot/band restrictions with exchange information.

Order concepts grant no access: market orders prioritize execution without a
chosen-price guarantee; limits restrict price without ensuring fill. A stop is
a trigger/exit plan, not a guaranteed loss cap. Gaps, locked bands and illiquidity
can prevent or worsen fills. Never invent a close at entry price. Recheck actual
segment/session order availability rather than relying on old education (M1-M2).

## Size from explicit inputs

For integer shares `q`, planned prices `entry`/`stop` and supplied paper loss budget
`B`, an unlevered LONG requires `0 < stop < entry`. Reduce `q` until
`q * (entry - stop) + estimated_round_trip_cost(q) <= B` and cash/notional limits
both hold. Include adverse slippage and quantity-dependent fees. If no legal lot
fits, size is zero; never increase risk just to force a setup. The helper's
fixed-plus-linear estimate is illustrative, not the engine's full fee model.

Synthetic example, not a recommended budget: virtual sleeve cash INR 33,333.33;
entry 500, stop 490, supplied risk budget 500, fixed estimated cost 20 and variable
cost 2/share. Forty shares imply nominal stop loss 400 plus costs 100. A gap exit
at 480 would instead lose 900 under this cost estimate. Planned loss is not a cap.

The virtual portfolio starts at INR 100,000 divided across three sleeves; each
sleeve cannot independently spend the total. Check reserved cash, pending/open
risk, sectors, correlated gaps and portfolio heat. Educational examples do not
authorize borrowing, leverage, risk-floor/cap changes or new instruments.

## Evaluate in money and risk units

`expectancy = p_win * avg_win - (1 - p_win) * avg_loss - costs`, with consistent
units and costs counted once. Synthetic 60% winners averaging 1R against 2R
losers produce -0.2R BEFORE costs. Win rate alone is not edge. Cost-free break-even
win rate is `avg_loss / (avg_win + avg_loss)`; costs raise it. Measure drawdown
depth/duration from equity peaks as well as return.

Separate trade fees from income-tax assumptions. Verify side, basis, cap,
effective date and product using current sources (C1), then inspect
`nsebot/costs.py`. Its stored rates are not proof of current law or personal tax
treatment. News excitement cannot remove a cost or risk constraint.

## Discipline and stops

FOMO, revenge trades, doubling after losses, hindsight rule changes and hiding
failed trials undermine research. Scaling/averaging must be specified and capped
before testing, not improvised to rescue losses. Insufficient edge/liquidity,
calendar, data or evidence should yield `NO PAPER ENTRY` or `RESEARCH BLOCKED`.
NISM explains that diversification reduces some risks but not market-wide risk
(R1-R2). SEBI's intraday study (R3) is historical context, not this user's future
success probability. Never guarantee returns.
