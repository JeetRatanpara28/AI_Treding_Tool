# Free API candidate: Tapetide

Subsequent user-authorized result: Free access confirmed, all six five-year
series acquired in seven market calls, preliminary quality PASS. See
[TAPETIDE_ACQUISITION.md](TAPETIDE_ACQUISITION.md). The proposal below records
the earlier documentation-only stage; it is not the latest acquisition status.

Reviewed 7 November 2026. Documentation research only: no signup, token creation,
market request, download, account/portfolio modification or new connector setup.

## Concrete positive finding

Tapetide's official [pricing](https://tapetide.com/pricing?source=unodirectory)
lists a permanent INR 0 plan with no card. Its FAQ and
[quota documentation](https://developers.tapetide.com/rate-limits/) describe 50
successful REST/MCP requests per IST day, no monthly cap and a 60/minute burst
cap. The paid trial is separate; do not enroll in it.

The official [Python guide](https://developers.tapetide.com/guides/python/)
expressly includes stock daily OHLCV in the free plan and describes caching
history locally. A free provider account/personal bearer token is required.
This is a data-service token, not a broker account or order credential. Do not
paste it into chat, commit it, log headers or read unrelated credential files.

## Exact required routes

| Requirement | Documented route | History / request limits |
| --- | --- | --- |
| Stock daily OHLCV | `/v1/stocks/{symbol}/prices/daily` | Oldest listings from 1996; max five years/request; max 5,000 rows/page; cursor pagination |
| Nifty 50 daily OHLC/volume | `/v1/indices/nifty-50/levels` | Oldest indices from 1996; max 1,000 rows/page; cursor pagination |

Sources: [stock endpoint](https://developers.tapetide.com/api/operations/liststockdailyprices/),
[index endpoint](https://developers.tapetide.com/api/operations/listindexlevels/).
Do not use the older index `/history?interval=max` path for this daily pilot:
its long windows use weekly bars.

If actual coverage matches the documents, the five pilot stocks could each fit
in one large page and Nifty in roughly two pages. This is a request-count
estimate, not measured coverage or an entitlement guarantee.

## Use conditions and source limitations

[Terms](https://tapetide.com/terms) describe educational/informational use and
permit the provided API/MCP interface while prohibiting outside scraping,
redistribution/commercial exploitation, rate-limit evasion and token sharing.
Official [backtest](https://developers.tapetide.com/guides/backtest-point-in-time/)
and [CSV-export](https://developers.tapetide.com/recipes/price-history-csv/)
guides support a private research/cache workflow. A separate NSE letter should
not be invented as a universal prerequisite for that described API pilot. This
is not a claim of unrestricted data rights or exchange-authorised vendor status.

The [price documentation](https://developers.tapetide.com/data/prices/) says
daily bars adjust splits/bonuses, not dividends; rights/demerger factors can be
unresolved. Some copied/unverified sessions are omitted. NSE EOD completeness
can lag until the next afternoon. These are significant limitations for same-day
signals and historical returns; free access does not establish quality.

Direct developer-page opens returned 401 in this review, while the search tool
returned their indexed official documentation. Pricing and terms pages were
retrievable. No authenticated request was made: current endpoint availability,
free-token entitlement, exact symbol history, calendar coverage and price
accuracy remain untested. Neither HTTP 401 nor an indexed example is proof that
an authenticated market-data request succeeds.

## Bounded first test, before a five-year acquisition

After the user chooses the free account and authorizes the market requests:

1. Verify the token's account quota using the documented read-only usage route.
2. Request one-day RELIANCE, TCS and Nifty data for 6 November 2026 (3 calls).
   Reconcile on the same price basis with the already approved official reports.
3. Request RELIANCE and Nifty for the verified Sunday 1 February 2026 Budget
   session (2 calls), and HINDUNILVR for 7 September 2026 (1 call). These probe
   omissions observed in the rejected GitHub source, not full coverage.
4. Cap the test at six market calls, ten rows and 256 KiB per response, no
   automatic pagination/retry/backfill. Save raw responses/hashes in a new
   private SSD directory. A missing bar, wrong date or null value fails clearly.
5. Only after reporting sample results, propose the five-year equity/index
   acquisition and independent calendar/adjustment/identity review. Keep all
   former failed datasets and production portfolio state unchanged.

No provider account, stored token or request is activated by this document.
No trading, watchlist/portfolio API, webhook or broker connection is needed.
Current 384-test receipt concerns the local engine; it does not validate this API.

## Other findings

- [TejHQ](https://tejhq.dev/docs) remains a free/keyless stock raw-data/actions
  fallback; it does not supply Nifty and its exchange-rights disclaimer remains.
- [Indian API](https://indianapi.in/documentation/indian-stock-market) documents
  long history, but the example price/volume series alone does not establish
  complete daily OHLCV and applicable free endpoint entitlement for this pilot.
- [Marketstack free](https://marketstack.com/pricing/) is limited to one year;
  it does not meet the five-year requirement.
- Other previously reviewed premium/full-history limits remain documented in
  [HISTORICAL_DATA_PILOT.md](HISTORICAL_DATA_PILOT.md).

This is a stronger new API candidate, not a reversal of the rejected GitHub
file's measured failures and not a claim that all free providers were exhausted.
