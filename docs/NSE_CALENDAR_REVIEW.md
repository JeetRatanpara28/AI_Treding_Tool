# NSE calendar verification - 7 November 2026

## Verified sources

The following official cash-equity circulars were downloaded successfully using
the installed `curl_cffi` default client. Standard `requests` and Windows curl
had timed out; this isolated the transport compatibility issue. No impersonation,
custom proxy, login, dependency installation, or access-control bypass was used.

| Source | Verified effect |
| --- | --- |
| [CMTR71775](https://nsearchives.nseindia.com/content/circulars/CMTR71775.pdf) | Annual 2026 cash-equity holiday schedule. |
| [CMTR72260](https://nsearchives.nseindia.com/content/circulars/CMTR72260.pdf) | Adds 15 January 2026 as a trading holiday. |
| [CMTR72349](https://nsearchives.nseindia.com/content/circulars/CMTR72349.pdf) | Sunday 1 February Union Budget session, normal market 09:15-15:30 IST, post-close through 16:00. |
| [CMTR76941](https://nsearchives.nseindia.com/content/circulars/CMTR76941.pdf) | Sunday 8 November Muhurat session; both pages of the user-supplied PDF were visually reviewed. Downloaded bytes match that PDF. |
| [CMTR77334](https://nsearchives.nseindia.com/content/circulars/CMTR77334.pdf) | 7 November is a mock session. The downloaded first page was visually reviewed; this is not added as a cash-equity historical trading session. |

Muhurat timings from the supplied/read circular: continuous trading opens 14:20;
CAS continuous trading ends 15:15; non-CAS trading ends 15:30; CAS matching ends
15:35; post-close is 15:50-16:00. These are exchange-session times, not instructions
to run the paper bot or to place real orders.

The calendar includes the annual weekday holidays plus the January amendment and
the two verified Sunday sessions. Source URLs and SHA256 hashes are stored with
`nsebot/calendars/nse_cash_2026.json`.

## Current fail-closed implementation

- `nsebot/session_calendar.py` is standard-library-only and shared by daily CLI
  freshness checks and `scripts/should_run.py`. Their conflicting cutoffs are removed.
- The reviewed snapshot covers 2026 dates, with a short review expiry after
  **10 November 2026 IST**. Beyond expiry, outside coverage, or with malformed/
  missing calendar input, execution stops. A review refresh is required before
  extending validity; annual coverage alone is not a promise about future changes.
- Daily data readiness is 16:15 IST: a local buffer after the reviewed 16:00
  post-close end. This is not an official Yahoo-data-finality guarantee.
- The latest finished exchange session is selected, including Sundays, holidays,
  consecutive closed days and timezone conversion. Missing required price bars
  still fail; calendar correctness never permits price fabrication.
- Special-session conflicts, missing hours, unsourced entries, duplicate dates/
  JSON keys, bad metadata, invalid sources and mock-session entries are rejected.
- An explicitly configured bad calendar never falls back to weekday inference.
- Intraday special sessions stop before downloads because normal strategy times
  are not appropriate. Normal-session polling requires fresh, complete finished
  bars and does not invent entry-price square-off fills on a lost feed.
- Trading workflows stay disabled. No calendar work enables scheduling, live
  transport, broker login, credentials or automatic orders.

## Source archives and historical failure evidence

Successful direct-download manifests:
`E:\AI-Trading-Data\results\nsebot\nse-fixed-downloads-20261107-2r1fu5de\calendar\manifest.json`
and the adjacent `closes/manifest.json`. All five PDFs and both approved daily
reports passed the repaired downloader's validation; the closing reports also
passed date/symbol/price checks. The downloaded bhavcopy and index report match
the user-supplied files byte-for-byte.

The original user PDF is preserved at `C:\AI-Trading-Bot\CMTR76941.pdf`.
A separate verified copy/manifest is under
`E:\AI-Trading-Data\results\nsebot\nse-calendar-verified-20261107-psxhoh5f`.
Its SHA256 is `ce94ee1c54d98eccdf3c30fa0673ae2b6a49ea4ed4a72fb83d826f4359f71d58`.

Earlier timeout attempts remain recorded under
`E:\AI-Trading-Data\results\nsebot\nse-calendar-sources-20261107-c96wbebq`;
those failed attempts were not relabeled successful or overwritten.

The original offline review found no installed calendar packages. None were
installed; the reviewed JSON and standard-library loader avoid that dependency.
The sources above are a reviewed snapshot, not an exhaustive guarantee about
future amendments. See [repair status](REPAIR_STATUS.md) before further work.
