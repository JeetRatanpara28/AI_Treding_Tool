"""Bounded read-only corporate-action/raw-price evidence for the five-stock pilot.

Requires actual user approval, in addition to the CLI flag. No orders, retries,
paid fallback, raw-price substitution or automatic corporate-action certification.
"""
import argparse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import tempfile

from .tapetide_fetch import Client, END, START, SYMBOLS, FetchError, dump, read_token


def acquire_review(token_file, parent, session=None):
    token = read_token(token_file)
    parent = Path(parent)
    if not parent.is_dir():
        raise FetchError('Approved SSD results directory is unavailable; no fallback')
    out = Path(tempfile.mkdtemp(prefix='tapetide-review-', dir=parent))
    client = Client(token, parent / 'tapetide_http_cache', session=session)
    receipt = dict(status='STARTED', market_backtest_run=False, series={},
                   review_declaration=False, required_market_calls=15)
    try:
        receipt['quota'] = client.verify_free_quota()
        if client.remaining < 15:
            raise FetchError('Need fifteen Free calls for the bounded evidence review')
        for symbol in SYMBOLS:
            base = f'/v1/stocks/{symbol}/'
            queries = [
                ('corporate-adjustments', dict(order='asc', limit=500)),
                ('corporate-actions', {'from': START, 'to': END, 'order': 'asc', 'limit': 200}),
                ('price', dict(days=2000, interval='daily', end_date=END)),
            ]
            receipt['series'][symbol] = {}
            for route, params in queries:
                obj = client.get(base + route, params)
                rows, meta = obj['data'], obj.get('meta')
                if (not isinstance(meta, dict) or not all(isinstance(row, dict) for row in rows)
                        or len(rows) > (2000 if route == 'price' else params['limit'])):
                    raise FetchError('Invalid evidence page shape or row count; cache retained')
                if route != 'price':
                    if meta.get('has_more') is not False:
                        raise FetchError('Corporate-action evidence exceeds one maximum-size page; stop')
                    for row in rows:
                        day = row.get('ex_date')
                        try:
                            parsed = date.fromisoformat(day)
                        except (TypeError, ValueError):
                            raise FetchError('Invalid corporate-action date') from None
                        if route == 'corporate-actions' and not START <= parsed.isoformat() <= END:
                            raise FetchError('Corporate action outside the reviewed window')
                else:
                    lower = (date.fromisoformat(END) - timedelta(days=2000)).isoformat()
                    window = meta.get('window')
                    if not isinstance(window, dict) or window.get('truncated') is not False:
                        raise FetchError('Raw-price evidence window is missing or truncated')
                    for row in rows:
                        try:
                            parsed = date.fromisoformat(row.get('date'))
                        except (TypeError, ValueError):
                            raise FetchError('Invalid raw-price date') from None
                        if not lower <= parsed.isoformat() <= END:
                            raise FetchError('Raw-price evidence outside maximum requested window')
                dump(out / f'{symbol}-{route}.json', obj)
                receipt['series'][symbol][route] = dict(rows=len(rows))
        receipt['status'] = 'EVIDENCE_DOWNLOADED_REVIEW_PENDING'
    except FetchError as exc:
        receipt.update(status='STOPPED', error=str(exc))
    except (OSError, ValueError, UnicodeError):
        receipt.update(status='STOPPED', error='Local evidence file or encoding failure; no overwrite')
    finally:
        receipt.update(market_requests=client.calls, remaining_estimate=client.remaining,
                       response_receipts=client.receipts,
                       acquired_utc=datetime.now(timezone.utc).isoformat())
        dump(out / 'acquisition.json', receipt)
        client.session.close()
    return out, receipt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-network', action='store_true')
    args = parser.parse_args(argv)
    if not args.allow_network:
        parser.error('User approval is required before --allow-network')
    repo = Path(__file__).resolve().parents[2]
    try:
        out, receipt = acquire_review(repo / 'local_research/tapetide.env',
                                     Path('E:/AI-Trading-Data/results/nsebot'))
    except FetchError as exc:
        print('Tapetide review stopped:', str(exc))
        return 2
    print(f"{receipt['status']}: {out / 'acquisition.json'}")
    print(f"Market requests: {receipt['market_requests']}; remaining: {receipt['remaining_estimate']}")
    if receipt.get('error'):
        print('Reason:', receipt['error'])
    return 0 if receipt['status'] == 'EVIDENCE_DOWNLOADED_REVIEW_PENDING' else 2


if __name__ == '__main__':
    raise SystemExit(main())
