"""Fake transport only. Never reads the user's token or calls any service."""
import json

import pytest
import requests

from nsebot.research.tapetide_fetch import Client, FetchError, MAX_BYTES, acquire, read_token

TOKEN = 'tpt_rt_SYNTHETIC_TEST_ONLY_0123456789'
ROUTE = '/v1/stocks/RELIANCE/prices/daily'


class Response:
    def __init__(self, payload=None, status=200, raw=None, headers=None):
        self.status_code = status
        self.raw = raw if raw is not None else json.dumps(payload).encode()
        self.headers = headers or {}
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def iter_content(self, size):
        for i in range(0, len(self.raw), size):
            yield self.raw[i:i + size]


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
    def get(self, url, **kw):
        self.requests.append((url, kw))
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value
    def close(self):
        pass


def page(more=False, cursor=None):
    return dict(data=[dict(date='2026-11-06', open=1., high=2., low=.5, close=1., volume=100)],
                meta=dict(has_more=more, next_cursor=cursor))


def quota(plan='free', remaining=50):
    return dict(data=dict(plan=plan, day=dict(remaining=remaining)))


def client(tmp_path, responses):
    session = Session([Response(quota()), *responses])
    c = Client(TOKEN, tmp_path / 'cache', session)
    c.verify_free_quota()
    return c, session


def test_only_dedicated_token_entry_is_parsed_without_echo(tmp_path):
    path = tmp_path / 'fake.env'
    path.write_text('# synthetic\nTAPETIDE_TOKEN=' + TOKEN, encoding='utf-8')
    assert read_token(path) == TOKEN
    path.write_text('BROKER_TOKEN=DO_NOT_USE', encoding='utf-8')
    with pytest.raises(FetchError) as exc:
        read_token(path)
    assert 'DO_NOT_USE' not in str(exc.value)


@pytest.mark.parametrize('plan,remaining', [('paid', 50), ('trial', 50), ('free', 6), ('unknown', 50)])
def test_not_free_or_insufficient_quota_stops_before_market_request(tmp_path, plan, remaining):
    session = Session([Response(quota(plan, remaining))])
    c = Client(TOKEN, tmp_path, session)
    with pytest.raises(FetchError):
        c.verify_free_quota()
    assert len(session.requests) == 1


def test_maximum_documented_page_and_cursor_stay_on_same_host(tmp_path):
    first = page(True, 'opaque-page-2')
    first['links'] = dict(next='https://evil.invalid/steal')
    c, s = client(tmp_path, [Response(first), Response(page())])
    assert len(c.history(ROUTE, 5000)) == 2
    calls = s.requests[1:]
    assert all(url == 'https://api.tapetide.com' + ROUTE for url, _ in calls)
    assert calls[0][1]['params']['limit'] == 5000
    assert calls[1][1]['params']['cursor'] == 'opaque-page-2'
    assert all(kw['allow_redirects'] is False and kw['stream'] is True for _, kw in calls)
    assert s.trust_env is False


@pytest.mark.parametrize('status', [301, 302, 401, 403, 429, 500])
def test_errors_do_not_follow_retry_or_save_response_body(tmp_path, status):
    c, s = client(tmp_path, [Response(dict(error=TOKEN), status=status)])
    with pytest.raises(FetchError) as exc:
        c.get(ROUTE)
    assert TOKEN not in str(exc.value)
    assert len(s.requests) == 2
    assert not list((tmp_path / 'cache').glob('*.json'))


def test_escaped_token_reflection_is_not_saved(tmp_path):
    raw = json.dumps(dict(data=[], detail=TOKEN)).replace('tpt_rt_', '\\u0074pt_rt_').encode()
    c, _ = client(tmp_path, [Response(raw=raw)])
    with pytest.raises(FetchError, match='Decoded response'):
        c.get(ROUTE)
    assert not list((tmp_path / 'cache').iterdir())


def test_oversized_and_nonfinite_json_are_rejected(tmp_path):
    c, _ = client(tmp_path, [Response(raw=b'x' * (MAX_BYTES + 1)),
                             Response(raw=b'{"data": [NaN]}'), Response(raw=b'{"data": [1e999]}')])
    with pytest.raises(FetchError, match='byte limit'):
        c.get(ROUTE)
    with pytest.raises(FetchError, match='non-finite'):
        c.get(ROUTE)
    with pytest.raises(FetchError, match='non-finite'):
        c.get(ROUTE)


def test_network_errors_are_sanitized(tmp_path):
    c, _ = client(tmp_path, [requests.ConnectionError('secret=' + TOKEN)])
    with pytest.raises(FetchError) as exc:
        c.get(ROUTE)
    assert TOKEN not in str(exc.value)


def test_cache_reuse_costs_no_second_market_call_and_tampering_fails(tmp_path):
    c, s = client(tmp_path, [Response(page())])
    c.get(ROUTE)
    c.get(ROUTE)
    assert len(s.requests) == 2
    assert c.calls == 1
    assert c.receipts[-1]['cache_hit'] is True
    path = next((tmp_path / 'cache').glob('*.json'))
    path.write_text('{"data": []}', encoding='utf-8')
    with pytest.raises(FetchError, match='checksum'):
        c.get(ROUTE)
    assert len(s.requests) == 2


def test_disallowed_endpoint_is_rejected_before_transport(tmp_path):
    c = Client(TOKEN, tmp_path, Session([]))
    with pytest.raises(FetchError, match='allow-list'):
        c.get('/v1/orders')
    assert not c.session.requests


def test_null_pagination_meta_stops_with_sanitized_receipt(tmp_path):
    env = tmp_path / 'fake.env'
    env.write_text('TAPETIDE_TOKEN=' + TOKEN, encoding='utf-8')
    s = Session([Response(quota()), Response(dict(data=[], meta=None))])
    out, receipt = acquire(env, tmp_path, session=s)
    assert receipt['status'] == 'STOPPED'
    assert 'pagination' in receipt['error']
    assert TOKEN not in (out / 'acquisition.json').read_text(encoding='utf-8')


def test_evidence_review_uses_bounded_maximum_pages_without_certifying_data(tmp_path):
    from nsebot.research.tapetide_review import acquire_review
    env = tmp_path / 'fake.env'
    env.write_text('TAPETIDE_TOKEN=' + TOKEN, encoding='utf-8')
    events = dict(data=[dict(ex_date='2024-10-28', factor=.5)], meta=dict(has_more=False))
    raw = page()
    raw['data'][0]['raw_close'] = None  # Preserve missing raw evidence; never fill from close.
    raw['meta'] = dict(window=dict(truncated=False, has_more=True))
    s = Session([Response(quota()), *[Response(p) for _ in range(5) for p in (events, events, raw)]])
    out, receipt = acquire_review(env, tmp_path, session=s)
    assert receipt['status'] == 'EVIDENCE_DOWNLOADED_REVIEW_PENDING'
    assert receipt['market_requests'] == 15
    assert receipt['review_declaration'] is False
    assert len(s.requests) == 16
    assert s.requests[1][1]['params']['limit'] == 500
    assert s.requests[2][1]['params']['limit'] == 200
    assert s.requests[3][1]['params']['days'] == 2000
    assert json.loads((out / 'RELIANCE-price.json').read_text())['data'][0]['raw_close'] is None


def test_incomplete_corporate_evidence_stops_before_further_calls(tmp_path):
    from nsebot.research.tapetide_review import acquire_review
    env = tmp_path / 'fake.env'
    env.write_text('TAPETIDE_TOKEN=' + TOKEN, encoding='utf-8')
    s = Session([Response(quota()), Response(dict(data=[], meta=dict(has_more=True)))])
    _, receipt = acquire_review(env, tmp_path, session=s)
    assert receipt['status'] == 'STOPPED'
    assert receipt['market_requests'] == 1
    assert receipt['review_declaration'] is False
    assert 'secret' not in receipt


def test_null_quota_stops_entitlement_download_before_any_market_calls(tmp_path):
    from nsebot.research.fetch_entitlements import acquire
    env = tmp_path/'fake.env'
    env.write_text('TAPETIDE_TOKEN='+TOKEN,encoding='utf-8')
    session = Session([Response(dict(data=None))])
    out,receipt = acquire(env,tmp_path,session=session)
    assert receipt['status']=='STOPPED'
    assert receipt['market_requests']==0
    assert len(session.requests)==1
    assert TOKEN not in (out/'acquisition.json').read_text()
