# Historical daily-data pilot: source review and proposed scope

Review date: 7 November 2026. Status: **specification only; no new market-data
download, backtest, order, source activation or publication**.

## Existing failure remains visible

The earlier Yahoo payload lacked the 6 November close for RELIANCE, TCS and
Nifty 50. The independent official one-day comparison passed, but does not repair
the vendor series or establish five-year coverage. See [repair status](REPAIR_STATUS.md).
Do not forward-fill or splice raw official closes into adjusted vendor history.

## Source decision

| Candidate | Evidence and limit | Decision for this pilot |
| --- | --- | --- |
| NSE official archives / security-wise history | Copyright policy allows personal/non-commercial/educational viewing and downloads, preserving content and acknowledgement; third-party content is excluded. Website terms section 9 prohibits systematic or automated collection. Complete five-year coverage and adjustment history remain untested. | Ordinary personal download has published permission subject to conditions. Do not treat it as authorization for automated historical collection or modified-data use. |
| NSE free research programme | Disclaimer describes a 2 GB aggregate threshold and eligibility restricted to accredited academic institutions, recognized research organizations and think tanks. Personal project eligibility is not established. This programme is not proof that every public CSV requires institutional membership. | Do not assume eligibility or treat the size threshold as blanket permission. |
| TradingView | Section 3 licenses display use and restricts non-display processing, including algorithmic uses; a chart export feature does not itself authorize this bot workflow. | No scraping, unofficial API or backtest ingestion without applicable permission. Human chart inspection is separate. |
| Yahoo through existing provider | Latest approved source check failed completeness. Official terms prohibit automated collection without express prior permission; official CSV download help describes a Gold subscription. A client library license does not license underlying data. | No new automated collection without applicable permission; no paid subscription. Earlier incomplete payload remains rejected. |
| Alpha Vantage | Official daily endpoint documentation marks full output as premium. NSE symbol coverage and suitable free five-year access have not been established. | No paid plan, account or API-key request; not selected. |
| Twelve Data | Official exchange table lists XNSE under individual Grow / business Venture, rather than free Basic. | No paid plan or account creation; not selected. |
| EODHD | Official plan help limits free end-of-day history to one year, with 20 requests/day. | Free tier does not meet this five-year scope; not selected. |

Official sources reviewed (terms can change; recheck before acquisition):

- [NSE historical reports](https://www.nseindia.com/static/resources/historical-reports-capital-market-daily-monthly-archives)
- [NSE security-wise history](https://www.nseindia.com/historical/price-and-volume-data-per-security)
- [NSE disclaimer and research eligibility](https://www.nseindia.com/static/nse-disclaimer)
- [NSE terms](https://www.nseindia.com/static/nse-terms-of-use)
- [NSE copyright: personal-download permission and conditions](https://www.nseindia.com/static/nse-copyright)
- [TradingView terms, section 3](https://www.tradingview.com/policies/)
- [Alpha Vantage documentation](https://www.alphavantage.co/documentation/)
- [Yahoo terms, automated-collection clause](https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html?ncid=mbr_idnedulnk00000001)
- [Yahoo official historical CSV download help](https://in.help.yahoo.com/kb/finance/download-historical-data-yahoo-finance-sln2311.html)
- [Twelve Data exchange tiers](https://twelvedata.com/exchanges?level=overview)
- [EODHD free-plan limits](https://eodhd.com/help/plans)

This is an acquisition decision with unresolved permissions, not a legal opinion
or a claim that no free source exists. Do not substitute an unverified mirror.

## Clarification after the published-terms check

An individual personal download does **not automatically need a separate approval
letter**: NSE's copyright policy expressly permits certain personal downloads.
The earlier institutional-programme discussion alone was incomplete. However,
that exception is conditional, and the same site's terms prohibit systematic or
automated collection. Its broader research/data policies do not clearly establish
our separate local automated-backtesting use rights. Read these together rather
than declaring all personal access prohibited or all automated access permitted.

Practical next options:

1. Use the normal official security-wise/history page's personal-download feature,
   subject to its applicable conditions, for human inspection and source checks.
   Retain original files unchanged with acknowledgement. Do not turn this into
   browser automation, repeated whole-market collection or an unapproved backtest.
2. For the five-year automated acquisition/processing workflow, clarify permitted
   access and use with the provider using the draft below or review an actual
   applicable permission supplied by the user. No enquiry was sent.

No examined provider has yet established a free, permitted, complete five-year
automated NSE pipeline for this project. This is a bounded finding about the
sources above, not an exhaustive claim about all providers. Source research is
complete for this review; data acquisition remains a separate pending step.

## Proposed bounded pilot, not an active download configuration

- Five cash-equity symbols: RELIANCE, TCS, HDFCBANK, HINDUNILVR, LT; EQ series.
  Verify historical identities/ISINs, listing dates, symbol changes and corporate
  actions before ingestion. These are engineering samples, not recommendations
  or a historical investable universe. Today's selection has survivorship bias.
- Nifty 50 as a separate daily price-index series. Do not invent index volume or
  compare price-index returns against dividend-inclusive equity returns silently.
- Requested interval: 7 November 2021 inclusive to 7 November 2026 exclusive.
  Last candidate date is 6 November 2026. Exact first/last sessions and gaps require
  reviewed historical calendars for all years; the runtime 2026 calendar is not
  sufficient. Strategy warm-up, if needed, requires a separate earlier interval.
- Required equity fields: session date, identity/series, open, high, low, close,
  traded volume; currency INR and timezone Asia/Kolkata. Retain source schema,
  raw bytes, retrieval time, source URL, adjustment basis and SHA256 manifest.
- Approximately 1,250 daily rows per series / 7,500 total, purely a sizing estimate.
  Normalized CSV should be roughly 1-3 MB, not a measured source download size.
  Raw whole-market daily archives could be much larger. Do not fetch thousands
  of whole-market files under the assumption this is a small six-series download.
- Store raw/normalized data and reports only in a new directory under
  `E:\AI-Trading-Data`; never overwrite prior trials or upload generated data.

## Acquisition gates and acceptance checks

1. Establish applicable no-cost rights for local, private automated backtesting;
   separately establish whether later ML use is permitted. No broker credentials.
2. Once established, present concrete source URLs/method, sample dates, maximum
   requests/bytes and destination for approval before downloading market files.
   Begin with a bounded sample spanning old/new schemas, not five years at once.
3. Validate source status/type, report dates, identity/series, duplicates, finite
   prices, OHLC consistency, nonnegative volume and documented missing sessions.
   Quarantine failures; do not synthesize prices. Preserve failed attempts.
4. Check corporate actions against official records. Keep raw and consistently
   adjusted datasets separate; record adjustment method and availability dates.
   Until resolved, price jumps cannot be interpreted as strategy returns.
5. Reconcile overlapping sample dates with independent official closes on the
   same raw basis. Verify historical session/calendar coverage, including special
   sessions, and schema transitions before extending the sample.
6. Report actual coverage, gaps, identity changes, bytes and checks. Only then
   propose the larger approved acquisition and baseline backtest specification.

## Optional permission enquiry draft (not sent)

We are an individual, non-commercial NSE cash-equity paper-research project,
with no broker connection or real orders. May we retrieve daily OHLCV for five
equities and the Nifty 50 price index for 7 November 2021 through 6 November 2026,
store it privately, and run local automated historical backtests? Which free
official access route, limits, attribution and retention conditions apply? Does
that permission also cover later local ML experiments? We will not redistribute
raw data. Please clarify eligibility if the institutional research programme is
the only applicable route.

No enquiry has been sent. Sending it requires the user's separate instruction;
do not imply accredited affiliation or disclose private files/account details.

## Personal sample inspection receipt

The user confirmed permission to proceed with the small personal-sample step.
This records the user's confirmation, not independently verified provider approval
for unrestricted automated collection, ML or redistribution.

Inspected the existing user-supplied 6 November 2026 cash bhavcopy and index
report offline. No replacement download was necessary. Result: **PASS** for
RELIANCE, TCS, HDFCBANK, HINDUNILVR, LT (one CM/NSE/STK/EQ row each), plus
one Nifty 50 row. Checks covered report date, duplicate identity, finite OHLCV,
price ordering, positive equity volume and source SHA256 hashes. Source ISINs
were recorded but have not been independently mapped across five years.

Private receipt and extracted one-session CSVs:
`E:\AI-Trading-Data\results\nsebot\personal-sample-inspection-i1sbbf7s\summary.json`.
Original inputs were read only; old and local portfolio file hashes were identical
before and after. Network requests: zero. No strategy/backtest/order was run.

This expands the engineering sample from two to five equities without changing
the production loader or weakening its tests. It does not establish historical
coverage, corporate-action adjustment correctness, investment suitability or
source permissions beyond the applicable terms. Next acquisition needs concrete
historical sample dates/method and applicable access rights; the existing one-day
PASS must not be presented as a five-year dataset.
