# Five-stock raw-share interval stress specification

Recorded before this experiment's performance, 7 November 2026. This is a new
disclosed engineering experiment, not promotion of quarantined data to the strict
raw-OHLC backtest contract. Existing TCS/LT evidence remains unchanged.

Use unchanged BotConfig, INR33,333.33 swing capital, the same 1,241 sessions and
200-session warm-up, all five original stocks, and all 5/10/25bps cases. No tuning.
Existing strict importer gates remain intact. Inputs and sources are hashed.

Raw closes exist for all five parents, but raw opens/highs/lows are not supplied
by the cached daily API routes. Infer **intervals**, not exact prices, assuming
the documented uniform bar adjustment and nearest-cent rounding of adjusted
OHLC. Raw-close divided by adjusted-close plus/minus INR0.005 bounds the scale.
Use upper open for buys, lower open for gap/next-open exits, lower low for stops,
and lower high (at least the observed close) for trailing. Apply adverse slippage
and dated raw-price ticks. These are stress assumptions; they do not establish
an observed executable raw-OHLC path or globally worst portfolio outcome.

Signals use continuous adjusted indicators translated into completed-close raw
units. Absolute price/turnover gates use raw prices and unadjusted volume. Prefix
tests check later-row removal, not historical vendor-revision availability.

Any held position or pending order crossing a reviewed capital-event date MUST
stop the run; do not silently drop positions, cancel genuine trades, skip the
date or claim unsupported entitlement/credit-date execution is implemented.
An actual run may complete only if it proves zero affected exposure at every
such date. This guard is not a general corporate-action trading ledger.

Buy-and-hold uses initial integer raw-share quantities and actual chronological
entitlements: RELIANCE->JIOFIN1:1 on20Jul2023, RELIANCEbonus1:1 on28Oct2024,
HDFCBANKbonus1:1 on26Aug2025, HUL->KWIL1:1 on5Dec2025. A later parent bonus
does not multiply a previously separated child. No entitlement on an ex-date buy.
All resulting shares remain held; the official6Nov2026 bhavcopy supplies all7
terminal marks. No sale before allotment/listing or artificial cash receipt.
Dividends, optional tender participation and terminal liquidation are excluded.

Only endpoint benchmark wealth/return is available. The API quota endpoint now
returns data:null, so free quota cannot be verified and the attempted child-history
acquisition stopped before any market requests. Do not invent a daily child curve,
use zero/forward fills as prices, or report benchmark drawdown/Sharpe as measured.

HDFCBANK's provider action ISIN INE040A01018 is preserved as an error. Reviewed
event identity is separately tied to official symbolHDFCBANK, facevalueRe1 and
ISIN INE040A01034; this is an explicit local mapping, not a repaired provider.
NSE FAOP69840 confirms26Aug2025/1:1; HDFC's official shareholder/ADR page
confirms currentISIN. Existing Bank holders receive no HDFCLtd42:25 merger ratio.

Report every outcome including losses, trade count, accounting, event-exposure
checks, repeatability and missing evidence. No strict-source-certified result,
statistical edge, total-return, live readiness or full entitlement-engine claim.

Primary references:
- https://nsearchives.nseindia.com/content/circulars/FAOP69840.pdf
- https://www.hdfc.bank.in/about-us/investor-relations/adr
- https://www.niftyindices.com/Press_Release/ind_prs28112025.pdf
- https://www.hul.co.in/files/faqs-on-allotment-of-kwil-shares-pursuant-to-the-scheme-of-demerger.pdf
- https://nsearchives.nseindia.com/web/sites/default/files/2023-08/PR_list_18082023.pdf
- https://www.ril.com/sites/default/files/2024-08/RIL_ANNUALREPORT_2023-24.pdf
- https://developers.tapetide.com/api/operations/getpricehistory/
