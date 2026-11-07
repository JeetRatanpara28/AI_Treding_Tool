# Alternative data sources: bounded review

Subsequent approved six-file inspection: **download/hash checks PASS, backtest
quality FAIL**. See [ASWIN_DATA_REVIEW.md](ASWIN_DATA_REVIEW.md). The metadata
review below is the pre-acquisition snapshot, not a current quality approval.

Reviewed 7 November 2026. **Research and repository metadata only**: no market
files, repositories, dependencies or services were downloaded/installed, no code
from these projects was executed, and no RTI/PIL/request/payment was submitted.
Web documents and repository source text were read for this review.

## Decision

There are useful alternatives to waiting indefinitely for NSE's academic reply.
The strongest small engineering candidate found is
[aswinv90/indian-market-historical-data](https://github.com/aswinv90/indian-market-historical-data).
It has the five pilot equities and Nifty file in the repository and a licence
expressly covering personal, non-commercial educational research. This is a
candidate for **bounded acquisition and validation**, not an independently
verified exchange-licensed or backtest-ready dataset.

Its stock/index scripts use Yahoo Finance via `yfinance`, so it is not an
independent exchange source and does not magically repair our earlier missing
Yahoo close. The last reviewed commit was dated 5 November 2026. Actual date
coverage, missing bars, OHLCV, adjustments and official-close reconciliation
remain untested. Never substitute `Adj Close` for raw close while leaving OHLC
on another basis or relabel a total-return adjustment as split-only.

## GitHub / public dataset shortlist

| Candidate | Verified evidence | Limitation / decision |
| --- | --- | --- |
| [Aswin historical data](https://github.com/aswinv90/indian-market-historical-data) | README, [licence](https://github.com/aswinv90/indian-market-historical-data/blob/main/LICENSE), full file tree, updater and `scripts/utils.py` inspected. Per-symbol Parquet plus index/action catalogues are listed. | Best small-file candidate for private academic validation. Preserve its attribution/licence; no republication into our MIT source repository. Upstream data-use rights are separate; no new exchange licence inferred. No actual price files inspected. |
| [Finance-broski/pit-data-sample](https://github.com/Finance-broski/pit-data-sample) | README declares CC-BY 4.0 for sample data: 99 names of adjusted/total-return closes, a historical universe and some timestamped fundamentals. File listing confirms samples, including an index-named file. | Useful bias/fundamental teaching candidate. Full required OHLCV and exact six-series/date coverage not established. The price CSV is 21,130,115 bytes; not fetched. Do not treat a reconstructed/index-named sample as official Nifty without verification. |
| [abhij1306/NSE-noodles](https://github.com/abhij1306/NSE-noodles) | README explicitly says method/code, **no dataset**. MIT applies to code; market data stays with the source. | Useful adjustment/lineage/review methodology, not a source that supplies history without NSE access. No installation, script execution or term-bypassing scrape. |
| [keyurbhojak1992/eod2-Historical-dataset-nse](https://github.com/keyurbhojak1992/eod2-Historical-dataset-nse) | README advertises historical EOD OHLCV and split/bonus adjustment, points to EOD2 upstream; GPLv3 licence text inspected. | Secondary candidate only: source/data-rights scope, actual usable files, latest date and demerger/dividend treatment not established. Do not import GPL code into this MIT project or equate a code licence with cleared market-data rights. |
| [TejHQ data service](https://tejhq.dev/data-terms) | Previously reviewed terms permit personal backtesting on its service but disclaim exchange licences/clarification; no Nifty index series. | Not a complete independently verified six-series replacement. Existing limitations remain; do not clone a mirror and call it an official exchange source. |

Repository metadata, README statements and dataset marketing are not measured
completeness or quality. This shortlist is not an endorsement or an exhaustive
catalogue of every public dataset. No arbitrary notebook, dependency installer,
scheduled workflow or broker integration was run.

## Concrete bounded candidate, without a full clone

GitHub ref reviewed: `700081a35486878208da393584c32ea83d6bbabc`.
Metadata snapshot and Git blob identifiers are in
[ALTERNATIVE_DATA_SOURCES_SNAPSHOT.json](ALTERNATIVE_DATA_SOURCES_SNAPSHOT.json).

| File in the Aswin repository | Metadata size (bytes) |
| --- | ---: |
| `data/NSE/RELIANCE_NS.parquet` | 388,265 |
| `data/NSE/TCS_NS.parquet` | 286,176 |
| `data/NSE/HDFCBANK_NS.parquet` | 370,088 |
| `data/NSE/HINDUNILVR_NS.parquet` | 356,666 |
| `data/NSE/LT_NS.parquet` | 303,987 |
| `data/INDICES/NIFTY_50.parquet` | 232,514 |
| Total, six files | 1,937,696 |

These are file sizes at the reviewed ref, **not downloaded-byte measurements**
or assurance of exact date coverage. The files contain longer histories; filter
the requested five-year window locally only after inspection. Do not clone the
whole multi-asset repository. `pyarrow` is already available in the project venv;
no new Parquet dependency is needed for an initial read.

Proposed next acquisition: only these six pinned files plus licence/provenance,
in a new private SSD folder, with per-file/total bounds, actual SHA256 and Git
blob verification. No repo workflows or update scripts. First check schema,
date ranges, nulls, identity/series mapping, OHLC consistency and raw official
overlap. A short or incomplete file is reported as such. Preserve failures.
Corporate-action and historical-calendar review still precede market backtesting.
Acquisition is not activated by this report and needs its concrete scope approved.

## Government and regulatory routes

| Route | What this review established | Fit for the requested bot data |
| --- | --- | --- |
| [SEBI equity cash-market data directory](https://www.sebi.gov.in/curation/equity_cash_market.html) | Security-wise price/volume entries link to NSE/BSE reports rather than an independent SEBI-hosted OHLCV dump. | Official navigation/verification source; not an independent replacement when exchange access is unavailable. |
| [Open Government Data portal](https://www.data.gov.in/) | Search surfaced aggregate trading/category/FPI records, not a verified five-stock five-year daily OHLCV resource. The retrieved main page showed maintenance/demo content; the catalogue and some licence links could not be fully retrieved. | No suitable dataset confirmed. This is an incomplete catalogue check, **not a claim that no relevant dataset exists**. Do not use demo rows, a 1970 default timestamp, or a search snippet as market evidence. |
| [RBI DBIE / Handbook](https://rbi.org.in/Scripts/AnnualPublications.aspx?head=Handbook+of+Statistics+on+Indian+Economy) | Official handbook contains aggregate index/market/economic series. An older [DBIE release calendar](https://dbieold.rbi.org.in/DBIE/doc/Release_Calender.pdf) lists daily NSE/BSE indices and market turnover. | Potential macro/reference support, not a verified per-company daily OHLCV source. The old calendar is not proof of current API coverage or accessible exports. |
| Government reports/annual filings | Filings can support corporate-action/fundamental/event checks; a report mentioning a company or price is not a continuous daily bar dataset. | Supporting evidence only; no invented daily open/high/low/volume from sparse closing/high-low tables. |

[GODL-India's official gazette](https://www.meity.gov.in/static/uploads/2024/02/Gazette-Notification_OpenDataLicense_13.02.2017.pdf)
permits reuse of covered government open data subject to conditions/exclusions,
including attribution and excluded rights/data. It is not a blanket licence for
every linked exchange dataset. Verify the particular resource/provider first.

## RTI and the possible PIL reference

[SEBI's RTI page](https://www.sebi.gov.in/rti-act-2005.html) describes access to
records held/controlled by public authorities, subject to exemptions, and lists
a normal INR 10 application fee. The [central RTI portal FAQ](https://rtionline.gov.in/faq.php?pageid=c9f0f895fb98ab9159f51fd0297e236d)
also explains that additional costs can apply and the portal covers listed
central public authorities. No fee was paid or application filed.

RTI could seek existing policy/circular records on academic/personal historical
data access and the applicable public resource/request process. It is not a
guaranteed route to a newly assembled, adjusted five-year market dataset or an
automatic market-data reuse licence. NSE's current direct RTI/public-authority
status was not established here; do not infer it from SEBI being an RTI authority.

If "PLI" meant **PIL (Public Interest Litigation)**, that is a separate court
process concerning public interest, not a data-download API. The Supreme Court
publishes [PIL guidelines](https://www.sci.gov.in/document/public-interest-litigation-pil-guidelines/)
and explains its [jurisdiction](https://www.sci.gov.in/jurisdiction/).
Recommendation for this project: pursue published data or academic clarification,
not litigation merely to obtain backtest files. No legal filing/representation
or decision on anyone's entitlement is made in this review.

## What changes now

Keep the NSE enquiry pending, but do not present waiting as the only path. A
small GitHub data candidate now has verified filenames, sizes and explicit
provider-level personal-research terms. Actual rights/coverage/quality validation
and dataset acquisition remain separate from this metadata review. Runtime code,
portfolio state, disabled workflows and paper-only guards were not changed.
