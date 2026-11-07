"""Approved read-only spin-off evidence: four maximum-size calls, no orders."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import tempfile

from .tapetide_fetch import Client, END, FetchError, dump, read_token

SPINOFFS = {'JIOFIN': '2023-08-21', 'KWIL': '2026-02-16'}


def acquire(token_file, parent, session=None):
    token = read_token(token_file)
    parent = Path(parent)
    if not parent.is_dir():
        raise FetchError('Approved SSD unavailable')
    out = Path(tempfile.mkdtemp(prefix='entitlement-evidence-', dir=parent))
    client = Client(token, parent / 'tapetide_http_cache', session=session)
    result = dict(status='STARTED', series={}, orders=False)
    try:
        result['quota'] = client.verify_free_quota()
        for symbol, listing in SPINOFFS.items():
            for route, params in (
                ('price', dict(days=2000, interval='daily', end_date=END)),
                ('corporate-actions', {'from': listing, 'to': END, 'limit': 200, 'order': 'asc'}),
            ):
                obj = client.get(f'/v1/stocks/{symbol}/{route}', params)
                meta = obj.get('meta')
                if not isinstance(meta, dict):
                    raise FetchError('Invalid spin-off metadata')
                if route == 'price':
                    if (len(obj['data']) > 2000 or not obj['data']
                            or meta.get('window', {}).get('truncated') is not False):
                        raise FetchError('Incomplete spin-off price window')
                    for row in obj['data']:
                        if not isinstance(row, dict) or not listing <= row.get('date', '') <= END:
                            raise FetchError('Spin-off price outside actual listed history')
                elif len(obj['data']) > 200 or meta.get('has_more') is not False:
                    raise FetchError('Incomplete spin-off actions')
                dump(out / f'{symbol}-{route}.json', obj)
                result['series'][f'{symbol}-{route}'] = len(obj['data'])
        result['status'] = 'EVIDENCE_READY_FOR_REVIEW'
    except FetchError as exc:
        result.update(status='STOPPED', error=str(exc))
    finally:
        result.update(market_requests=client.calls, remaining=client.remaining,
                      response_receipts=client.receipts, acquired_utc=datetime.now(timezone.utc).isoformat())
        dump(out / 'acquisition.json', result)
        client.session.close()
    return out, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-network', action='store_true')
    args = parser.parse_args()
    if not args.allow_network:
        parser.error('Actual user approval is required before --allow-network')
    repo = Path(__file__).resolve().parents[2]
    out, result = acquire(repo / 'local_research/tapetide.env', Path('E:/AI-Trading-Data/results/nsebot'))
    print(result['status'], out / 'acquisition.json')
    print('Market calls:', result['market_requests'], 'remaining:', result['remaining'])
    if result.get('error'):
        print(result['error'])
    return 0 if result['status'] == 'EVIDENCE_READY_FOR_REVIEW' else 2


if __name__ == '__main__':
    raise SystemExit(main())
