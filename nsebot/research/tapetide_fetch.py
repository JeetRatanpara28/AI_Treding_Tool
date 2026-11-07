"""Bounded read-only Tapetide history acquisition. Never trade or print tokens."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile

import requests

BASE = 'https://api.tapetide.com'
SYMBOLS = ('RELIANCE', 'TCS', 'HDFCBANK', 'HINDUNILVR', 'LT')
START, END = '2021-11-07', '2026-11-06'
MAX_BYTES = 2 * 1024 * 1024
MAX_CALLS = 20
ALLOWED = {'/v1/me/usage', '/v1/indices/nifty-50/levels',
           *(f'/v1/stocks/{s}/{route}' for s in ('JIOFIN', 'KWIL')
             for route in ('price', 'corporate-actions')),
           *(f'/v1/stocks/{s}/{route}' for s in SYMBOLS
             for route in ('prices/daily', 'corporate-adjustments', 'corporate-actions', 'price'))}


class FetchError(ValueError):
    """Messages contain no credential, response body or authentication headers."""


def read_token(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 4096:
        raise FetchError('Dedicated local token file missing or unexpectedly large')
    try:
        lines = [s.strip() for s in path.read_text(encoding='utf-8').splitlines()
                 if s.strip() and not s.lstrip().startswith('#')]
    except (OSError, UnicodeError):
        raise FetchError('Cannot read the dedicated UTF-8 token file') from None
    if len(lines) != 1 or not lines[0].startswith('TAPETIDE_TOKEN='):
        raise FetchError('Expected exactly one TAPETIDE_TOKEN entry')
    token = lines[0].split('=', 1)[1].strip()
    if not re.fullmatch(r'tpt_rt_[A-Za-z0-9_.-]{8,512}', token):
        raise FetchError('Token format invalid; do not paste a token into chat or logs')
    return token


def dump(path, obj):
    with Path(path).open('x', encoding='utf-8') as fh:
        json.dump(obj, fh, indent=2, allow_nan=False)


class Client:
    def __init__(self, token, cache, session=None):
        self._token = token
        self.session = session or requests.Session()
        self.session.trust_env = False  # No proxy/.netrc/account credential fallback.
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.calls = 0
        self.remaining = 0
        self.budget = 0
        self.receipts = []

    def get(self, path, params=None, quota=False):
        if path not in ALLOWED or quota != (path == '/v1/me/usage'):
            raise FetchError('Endpoint is outside the approved read-only allow-list')
        params = params or {}
        key = hashlib.sha256(json.dumps([path, params], sort_keys=True).encode()).hexdigest()
        cached = self.cache / (key + '.json')
        checksum = self.cache / (key + '.sha256')
        body = None
        if not quota and cached.is_file():
            if cached.stat().st_size > MAX_BYTES:
                raise FetchError('Cached response exceeds size limit')
            body = cached.read_bytes()
            if (not checksum.is_file() or checksum.read_text(encoding='ascii').strip()
                    != hashlib.sha256(body).hexdigest()):
                raise FetchError('Cached response checksum failed; no silent re-download')
        if body is None:
            if not quota and (self.calls >= self.budget or self.remaining <= 0):
                raise FetchError('Free quota or local request budget exhausted; no paid fallback')
            if not quota:
                self.calls += 1
                self.remaining -= 1
            try:
                response = self.session.get(BASE + path, params=params,
                    headers={'Authorization': 'Bearer ' + self._token, 'Accept': 'application/json'},
                    stream=True, allow_redirects=False, timeout=(10, 30))
                with response:
                    if response.status_code != 200:
                        raise FetchError(f'API HTTP {response.status_code}; no retry, redirect or plan upgrade')
                    chunks, size = [], 0
                    for chunk in response.iter_content(65536):
                        size += len(chunk)
                        if size > MAX_BYTES:
                            raise FetchError('Response exceeds the approved byte limit')
                        chunks.append(chunk)
                    body = b''.join(chunks)
                    remaining = response.headers.get('X-RateLimit-Remaining')
                    if not quota and remaining and str(remaining).isdigit():
                        self.remaining = min(self.remaining, int(remaining))
            except FetchError:
                raise
            except requests.RequestException:
                raise FetchError('Network/TLS request failed; details withheld to protect credentials') from None
        if self._token.encode() in body:
            raise FetchError('Response contains credential material; not saved')
        try:
            def nonfinite(value):
                raise FetchError('API JSON contains a non-finite numeric constant')
            def finite_float(value):
                result = float(value)
                if not math.isfinite(result):
                    nonfinite(value)
                return result
            obj = json.loads(body, parse_constant=nonfinite, parse_float=finite_float)
        except FetchError:
            raise
        except (ValueError, UnicodeError):
            raise FetchError('API response is not valid JSON') from None
        if not isinstance(obj, dict) or 'data' not in obj:
            raise FetchError('API response envelope is invalid')
        if self._token in json.dumps(obj, ensure_ascii=False):
            raise FetchError('Decoded response contains credential material; not saved')
        if not quota and not isinstance(obj['data'], list):
            raise FetchError('Market-data response is not a row collection')
        hit = not quota and cached.exists()
        if not quota and not hit:
            with cached.open('xb') as fh:
                fh.write(body)
            with checksum.open('x', encoding='ascii') as fh:
                fh.write(hashlib.sha256(body).hexdigest() + '\n')
        self.receipts.append(dict(endpoint=path, cache_key=key, cache_hit=hit,
                                  bytes=len(body), sha256=hashlib.sha256(body).hexdigest()))
        return obj

    def verify_free_quota(self):
        obj = self.get('/v1/me/usage', quota=True)
        try:
            data = obj['data']
            plan, remaining = data['plan'], data['day']['remaining']
            if plan != 'free' or type(remaining) is not int or remaining < 7:
                raise FetchError('Need verified Free plan and at least seven calls; no paid/trial fallback')
            self.remaining = remaining
            self.budget = min(MAX_CALLS, remaining)
        except (KeyError, TypeError):
            raise FetchError('Unrecognized quota schema; stop before market requests') from None
        return dict(plan='free', remaining_before=remaining, max_market_calls=self.budget)

    def history(self, path, limit):
        rows, seen = [], set()
        params = {'from': START, 'to': END, 'order': 'asc', 'limit': limit}
        for _ in range(4):
            obj = self.get(path, params)
            page, meta = obj['data'], obj.get('meta', {})
            if not isinstance(meta, dict):
                raise FetchError('Invalid history pagination metadata')
            if len(page) > limit or any(not isinstance(r, dict) for r in page):
                raise FetchError('Invalid history page shape or row count')
            for row in page:
                day = row.get('date')
                if not isinstance(day, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', day) or not START <= day <= END:
                    raise FetchError('History contains a wrong/missing date; raw cache preserved')
            rows.extend(page)
            more = meta.get('has_more')
            if type(more) is not bool:
                raise FetchError('Missing pagination completeness flag')
            if not more:
                return rows
            cursor = meta.get('next_cursor')
            if not isinstance(cursor, str) or not cursor or len(cursor) > 2048 or cursor in seen:
                raise FetchError('Invalid/repeated pagination cursor')
            seen.add(cursor)
            params = {**params, 'cursor': cursor}  # Never follow a server-supplied URL.
        raise FetchError('Pagination exceeds the approved four-page bound')


def acquire(token_file, parent, session=None):
    token = read_token(token_file)
    parent = Path(parent)
    if not parent.is_dir():
        raise FetchError('Approved SSD results directory is unavailable; no fallback')
    out = Path(tempfile.mkdtemp(prefix='tapetide-history-', dir=parent))
    client = Client(token, parent / 'tapetide_http_cache', session=session)
    receipt = dict(status='STARTED', window=dict(start=START, end_inclusive=END),
                    limits=dict(stock_page=5000, index_page=1000, max_bytes_per_response=MAX_BYTES,
                                max_market_calls=MAX_CALLS), series={}, market_backtest_run=False)
    try:
        receipt['quota'] = client.verify_free_quota()
        routes = [(s, f'/v1/stocks/{s}/prices/daily', 5000) for s in SYMBOLS]
        routes.append(('NIFTY_50', '/v1/indices/nifty-50/levels', 1000))
        for symbol, route, limit in routes:
            rows = client.history(route, limit)
            dump(out / (symbol + '.json'), rows)
            dates = [r['date'] for r in rows]
            receipt['series'][symbol] = dict(rows=len(rows), first=min(dates) if dates else None,
                                             last=max(dates) if dates else None)
        receipt['status'] = 'DOWNLOADED_QUALITY_REVIEW_PENDING'
    except FetchError as exc:
        receipt.update(status='STOPPED', error=str(exc))
    except (OSError, ValueError, UnicodeError):
        receipt.update(status='STOPPED', error='Local file or data encoding failure; no retry or overwrite')
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
        out, result = acquire(repo / 'local_research/tapetide.env',
                              Path('E:/AI-Trading-Data/results/nsebot'))
    except FetchError as exc:
        print('Tapetide stopped:', str(exc))
        return 2
    print(f"{result['status']}: {out / 'acquisition.json'}")
    print(f"Market requests: {result['market_requests']}; series received: {len(result['series'])}")
    if result.get('error'):
        print('Reason:', result['error'])
    return 0 if result['status'] == 'DOWNLOADED_QUALITY_REVIEW_PENDING' else 2


if __name__ == '__main__':
    raise SystemExit(main())
