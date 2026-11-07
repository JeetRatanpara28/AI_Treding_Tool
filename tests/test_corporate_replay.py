"""Synthetic evidence only; no credentials, market downloads or real ledgers."""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from conftest import daily_frame
from nsebot.config import BotConfig
from nsebot.research.corporate_replay import (
    IntervalPaperBroker, RawShareMarket, guard_capital_event, raw_intervals, run, terminal_holdings,
)


def test_raw_rounding_bounds_enclose_true_unrounded_bar_without_asserting_exact_open():
    # A 1:1 bonus halves price. Rounding a half-cent loses exact raw OHLC.
    frame = pd.DataFrame(dict(open=[50.01], high=[51.01], low=[49.01], close=[50.01], volume=[100.]))
    bounds = raw_intervals(frame, [100.01])
    assert bounds['open'].iloc[0] <= 100.01 <= bounds['raw_open_upper'].iloc[0]
    assert bounds['low'].iloc[0] <= 98.01
    assert bounds['high'].iloc[0] <= 102.01
    assert bounds['close'].iloc[0] == 100.01
    exact = raw_intervals(frame, frame['close'])
    assert exact['open'].iloc[0] == exact['raw_open_upper'].iloc[0] == 50.01


@pytest.mark.parametrize('value', [np.nan, np.inf, 0., -1.])
def test_missing_or_invalid_raw_close_blocks_interval_reconstruction(value):
    with pytest.raises(ValueError, match='RAW SCALE'):
        raw_intervals(daily_frame([100.]), [value])


def test_parent_bonus_does_not_double_previously_separated_child():
    events = [dict(parent='P',child='C',type='demerger',ex_date='2023-07-20',numerator=1,denominator=1),
              dict(parent='P',type='bonus',ex_date='2024-10-28',numerator=1,denominator=1)]
    qty, audit = terminal_holdings({'P':dict(qty=3)}, events, '2022-01-01', '2026-11-06')
    assert qty == {'P':6, 'C':3}
    assert [a['added_qty'] for a in audit] == [3,3]
    qty, _ = terminal_holdings({'P':dict(qty=3)}, events, '2023-07-20', '2026-11-06')
    assert qty == {'P':6}  # Ex-date purchase has no child entitlement.
    events[0].update(numerator=1,denominator=2)
    with pytest.raises(ValueError, match='fractional entitlement'):
        terminal_holdings({'P':dict(qty=3)}, events, '2022-01-01','2026-11-06')


@pytest.mark.parametrize('exposure', ['position', 'pending'])
def test_unsupported_corporate_exposure_fails_without_changing_state(exposure):
    event = dict(parent='P', ex_date='2023-07-20')
    pos = SimpleNamespace(symbol='P')
    pending = {'spec':{'symbol':'P','qty':3}}
    ledger = SimpleNamespace(positions=[pos] if exposure=='position' else [],
                             state={'pending':[pending] if exposure=='pending' else []})
    with pytest.raises(ValueError, match='full entitlement ledger'):
        guard_capital_event(ledger,event,'2023-07-20')
    assert (ledger.positions == [pos]) if exposure=='position' else (ledger.state['pending'] == [pending])


def test_interval_broker_cancels_ambiguous_stop_then_buys_at_upper_open():
    raw = {'S':pd.DataFrame(dict(datetime=pd.to_datetime(['2024-02-01']),close=[100.]))}
    broker = IntervalPaperBroker(raw, slippage_bps=0.)
    pending = dict(spec=dict(symbol='S',side='LONG',product='CNC',qty=10,stop=100.))
    bar = dict(datetime='2024-02-02',open=99.99,raw_open_upper=100.02)
    assert broker.resolve_entry(pending,bar).status == 'CANCELLED'
    pending['spec']['stop'] = 90.
    fill = broker.resolve_entry(pending,bar).fill
    assert fill.price == 100.05  # Adverse upper-bound open rounded up to historical tick.


def test_raw_market_prefix_and_absolute_units_remain_consistent():
    stock = daily_frame(np.linspace(100.,150.,460),start='2022-01-03',volume=1_000_000.)
    raw = pd.DataFrame(dict(datetime=stock['datetime'],raw_close=stock['close']*2))
    cfg = BotConfig()
    full = RawShareMarket({'S':stock},stock,{'S':raw},cfg)
    prefix = RawShareMarket({'S':stock.iloc[:300]},stock.iloc[:300],{'S':raw.iloc[:300]},cfg)
    pd.testing.assert_frame_equal(full.feats['S'].iloc[:300],prefix.feats['S'])
    assert full.feats['S']['close'].iloc[-1] == 300.
    assert full.feats['S']['ema_trend'].iloc[-1] > 200.


def test_synthetic_interval_run_uses_no_sockets_and_no_fake_benchmark_curve(tmp_path,monkeypatch):
    import socket
    def forbidden(*args,**kwargs):
        pytest.fail('offline interval replay must not open a socket')
    monkeypatch.setattr(socket,'socket',forbidden)
    stock = daily_frame(np.linspace(100.,150.,452),start='2022-01-03',volume=1_000_000.)
    raw = pd.DataFrame(dict(datetime=stock['datetime'],raw_close=stock['close']))
    out,result = run({'S':stock},stock,{'S':raw},[],{'S':150.},tmp_path,
                     {'data_kind':'synthetic','source':'synthetic fixture'})
    assert result['strict_raw_ohlc_backtest_ready'] is False
    for case in result['scenarios']:
        assert case['accounting']=='PASS'
        assert case['closed_trades']==0
        assert case['benchmark']['daily_curve'] is None
        assert case['benchmark']['maxdd'] is None
    assert (out/'frozen_spec.json').is_file()
