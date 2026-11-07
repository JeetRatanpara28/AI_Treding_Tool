# Frozen historical engineering pilot

Frozen before computing strategy/benchmark performance, 7 November 2026.
This is a narrower TCS/LT pilot, not completion of the original five-stock study.
It does not authorize deployment, live orders, parameter searches or publication.

## Hypothesis and fixed scope

Use the existing `BotConfig()` swing reversion strategy without modifying any
signal, sizing or risk parameter. Test whether its descriptive net price results
survive execution costs and compare them with the same-stock buy-and-hold result.
There is no positive-return acceptance target. Keep all three fixed slippage
cases (5, 10 and 25 bps); do not select the winning case or rerun tuned settings.

- Sources: preserved Tapetide daily OHLCV, independently reviewed official NSE
  cash session calendars/amendments, provider raw-price/action receipts, primary
  company corporate-action/ISIN documents and official 6 November 2026 reports.
- Input dates: 8 November 2021 to 6 November 2026, exactly 1,241 sessions.
- First 200 sessions are warm-up; the remaining 1,041 are evaluation sessions.
- Capital: INR 33,333.33, swing sleeve only. Other sleeves/old ledgers stay separate.
- Fixed symbols: **TCS, LT**. Selection is for data/accounting tractability,
  before inspecting performance, not an assertion of representative NSE coverage.
  Both have no identified in-window automatic share-capital event; all 1,241
  adjusted closes must equal available raw closes and both daily routes must agree.
  Dividends are excluded; optional tender buybacks are declined.
- Keep original RELIANCE/HDFCBANK/HINDUNILVR inputs and failure evidence intact.
  RELIANCE's 2023 Jio demerger is absent from its factor timeline; HUL's December
  2025 demerger has no quantified factor. Neither currently has a spin-off wealth
  ledger. HDFCBANK needs bonus-aware historical quantities; additionally its API
  corporate-action ISIN `INE040A01018` disagrees with official `INE040A01034`.
  They are quarantined from this pilot, not silently declared validated.

## Execution and comparison

Close-observed signals and discretionary exits fill at the next eligible open.
Protective stops include adverse opening gaps. Use real historical price/share
units for the admitted symbols, integer shares, cash/fee affordability guards,
dated exchange + IPFT costs and reviewed monthly tick determination. No leverage.

Reviewed exchange + IPFT INR/crore/side:
345.01 through March 2023; 335 from April 2023; 332 from April 2024;
307 from October 2024 (composition changes again in March 2026, total unchanged).
DP is a conservative **fixed INR 15.93 including GST assumption**, not an exact
historical tax invoice. Held-delivery STT/stamp treatment also applies to same-day
stops, potentially overcharging them. No income/capital-gains tax is modeled.

Tick determination uses previous-month close, never a future/current-bar close;
pre-June 2024 tick INR 0.05, June 2024 sub-INR250 revision and April 2025 bands
are applied on their reviewed effective dates. Dated price bands still do not
guarantee a fill, price-band availability, liquidity, lot-size history or queue rank.

Same-stock benchmark: equal initial budgets, integer shares, identical buy charges,
slippage and dated ticks, buy at the second evaluated session's open and hold.
Strategy and benchmark initially spend one evaluated session in cash. Final
inventory is marked, not forcibly liquidated. Nifty is a separate gross price
reference, not a cost-adjusted investable fund or dividend-inclusive comparison.

## Acceptance, evidence and limits

Require data/calendar/raw-scale/identity gates, isolated fresh state, no sockets
during replay, cash/positions/P&L reconciliation and repeatable output. Save
source/config/fee/version hashes before computing performance. Report all cases,
trade count, win rate, net return, CAGR, drawdown, Sharpe, costs, exposure and
terminal inventory. Few/zero trades and valid weak returns are inconclusive or
negative evidence, not implementation errors to tune away.

Descriptive earlier/later splits are not untouched out-of-sample tests. Five
stocks were originally selected today; the two admitted stocks are an even
narrower survivor-selected engineering sample. The breadth feature needs ten
names and is inactive here. Daily bars cannot establish intraday order paths,
price-band fills or the 2024 disaster-recovery sessions' midday order resets.
No result certifies an exchange-wide strategy, total shareholder wealth, absence
of all bias, profitability or Monday/live deployment readiness.

## Primary references

- [Tapetide raw-close and adjustment metadata](https://developers.tapetide.com/api/operations/getpricehistory/)
- [Tapetide factor reconstruction caveats](https://developers.tapetide.com/api/operations/liststockcorporateadjustments/)
- [TCS investor FAQ](https://www.tcs.com/investor-relations/investor-faqs)
- [L&T investor FAQ](https://investors.larsentoubro.com/Investor-FAQ.aspx)
- [NSE April 2023 exchange/IPFT circular](https://archives.nseindia.com/content/circulars/FA56129.pdf)
- [April 2024 fee revision](https://zerodha.com/marketintel/bulletin/373933/revision-in-nse-transaction-charges-from-april-1-2024)
- [NSE October 2024 revision](https://nsearchives.nseindia.com/content/circulars/FA64232.pdf)
- [NSE March 2026 revision](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf)
- [NSE June 2024 ticks](https://nsearchives.nseindia.com/content/circulars/CMTR62385.pdf)
- [NSE April 2025 ticks](https://nsearchives.nseindia.com/content/circulars/CMTR67133.pdf)
