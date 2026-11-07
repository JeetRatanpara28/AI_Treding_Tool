"""Daily paper cycles must not use stale or incomplete data or change state."""

import logging

import numpy as np
import pandas as pd
import pytest

import nsebot.data
import nsebot.listing
import nsebot.market
import nsebot.universe
from nsebot.__main__ import main
from nsebot.freshness import DataFreshnessError, expected_daily_session, require_daily_session
from nsebot.freshness import require_intraday_bar
from nsebot.ledger import Ledger
from conftest import daily_frame


@pytest.mark.parametrize('now, expected', [
    ('2026-11-06 16:14:59+05:30', '2026-11-05'),
    ('2026-11-06 16:15:00+05:30', '2026-11-06'),
    ('2026-11-07 10:00:00+05:30', '2026-11-06'),
    ('2026-11-08 18:00:00+05:30', '2026-11-08'),
    ('2026-11-09 10:00:00+05:30', '2026-11-08'),
    ('2026-11-09 18:00:00+05:30', '2026-11-09'),
    ('2026-11-06 10:45:00+00:00', '2026-11-06'),
    ('2026-11-06 10:44:59+00:00', '2026-11-05'),
    ('2026-11-06 18:00:00', '2026-11-06'),  # naive clock means IST
])
def test_expected_reviewed_session_in_ist(now, expected):
    assert expected_daily_session(now) == pd.Timestamp(expected)


@pytest.mark.parametrize('problem', ['close_missing', 'infinite', 'bad_ohlc', 'zero_volume',
                                    'duplicate', 'missing_date', 'unsorted', 'invalid_date'])
def test_latest_bar_must_be_unique_complete_and_valid(problem):
    frame = daily_frame([100., 101.], start='2026-11-05')
    if problem == 'close_missing':
        frame.loc[1, 'close'] = np.nan
    elif problem == 'infinite':
        frame.loc[1, 'high'] = np.inf
    elif problem == 'bad_ohlc':
        frame.loc[1, 'high'] = 1.
    elif problem == 'zero_volume':
        frame.loc[1, 'volume'] = 0.
    elif problem == 'duplicate':
        frame = pd.concat([frame, frame.iloc[[-1]]], ignore_index=True)
    elif problem == 'missing_date':
        frame = frame.iloc[:-1]
    elif problem == 'unsorted':
        frame = frame.iloc[::-1]
    elif problem == 'invalid_date':
        frame.loc[1, 'datetime'] = pd.NaT
    with pytest.raises(DataFreshnessError, match='2026-11-06'):
        require_daily_session(frame, '2026-11-06', 'TCS')


def test_index_can_have_zero_volume_and_forming_today_is_ignored():
    frame = daily_frame([100., 101.], volume=0, start='2026-11-05')
    frame.loc[1, 'close'] = np.nan
    expected = expected_daily_session('2026-11-06 11:00')
    require_daily_session(frame, expected, 'index', is_index=True)


@pytest.mark.parametrize('command', ['swing', 'momentum'])
@pytest.mark.parametrize('problem', ['stale_index', 'incomplete_index', 'stale_stock',
                                    'incomplete_stock', 'missing_pending_symbol'])
def test_cli_stops_before_engine_orders_or_state_writes(command, problem, tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(nsebot.market, 'now_ist', lambda: pd.Timestamp('2026-11-07 10:00', tz='Asia/Kolkata'))
    start = str(pd.bdate_range(end='2026-11-06', periods=80)[0].date())
    fresh = daily_frame(np.arange(80, dtype=float) + 100, start=start)

    class Provider:
        def __init__(self, *args, **kwargs):
            pass

        def daily(self, symbols, **kwargs):
            out = {}
            for symbol in symbols:
                if symbol == 'HELD':
                    continue
                frame = fresh.copy()
                target = symbol == '^NSEI' if problem.endswith('index') else symbol == 'TCS'
                if target and problem.startswith('stale'):
                    # Match production: sanitizer drops the latest incomplete bar.
                    frame = frame.iloc[:-1].copy()
                elif target and problem.startswith('incomplete'):
                    frame.loc[frame.index[-1], 'close'] = np.nan
                out[symbol] = frame
            return out

    monkeypatch.setattr(nsebot.data, 'YahooProvider', Provider)
    monkeypatch.setattr(nsebot.universe, 'SWING_UNIVERSE', ['RELIANCE', 'TCS', 'INFY'])
    monkeypatch.setattr(nsebot.listing, 'nse_equities', lambda *args, **kwargs: (['RELIANCE', 'TCS', 'INFY'], 'fake'))
    monkeypatch.chdir(tmp_path)
    root = tmp_path / 'state'
    ledger = Ledger(str(root), command, 100_000)
    if problem == 'missing_pending_symbol':
        ledger.state['pending'] = [{'spec': {'symbol': 'HELD'}}]
    ledger.save()
    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def forbidden(*args, **kwargs):
        pytest.fail('stale inputs must stop before engine execution, orders, or cash sweeps')

    monkeypatch.setattr('nsebot.engine.swing.SwingEngine.run', forbidden)
    monkeypatch.setattr('nsebot.engine.momentum.MomentumEngine.run', forbidden)
    monkeypatch.setattr('nsebot.engine.momentum.MomentumEngine.receive', forbidden)
    monkeypatch.setattr('nsebot.broker.paper.PaperBroker.place_entry', forbidden)
    monkeypatch.setattr('nsebot.__main__._sweeps', forbidden)
    with caplog.at_level(logging.ERROR, logger='nsebot'):
        assert main([command, '--state', str(root)]) == 3
    assert 'DATA FRESHNESS' in caplog.text and 'state left untouched' in caplog.text
    assert {p: p.read_bytes() for p in root.rglob('*') if p.is_file()} == before


def test_weekday_holiday_is_not_assumed_when_data_is_missing():
    # Without an exchange calendar, even a possible holiday must fail closed.
    previous = daily_frame([100.], start='2026-11-05')
    with pytest.raises(DataFreshnessError):
        require_daily_session(previous, expected_daily_session('2026-11-06 18:00'), 'index', is_index=True)


@pytest.mark.parametrize('problem', ['stale', 'missing_close', 'duplicate', 'forming_only'])
def test_intraday_requires_latest_completed_bar(problem):
    from conftest import intraday_sessions
    frame = intraday_sessions(n_sessions=1, start='2026-11-06')
    latest = pd.Timestamp('2026-11-06 10:10', tz='Asia/Kolkata')
    if problem == 'stale':
        frame = frame[frame.datetime < latest]
    elif problem == 'missing_close':
        frame.loc[frame.datetime == latest, 'close'] = np.nan
    elif problem == 'duplicate':
        frame = pd.concat([frame[frame.datetime <= latest], frame[frame.datetime == latest]])
    elif problem == 'forming_only':
        frame = frame[frame.datetime > latest]
    with pytest.raises(DataFreshnessError):
        require_intraday_bar(frame, '2026-11-06 10:15:25+05:30', 'TCS')


def test_intraday_ignores_forming_and_future_bars():
    from conftest import intraday_sessions
    frame = intraday_sessions(n_sessions=1, start='2026-11-06')
    frame.loc[frame.datetime >= pd.Timestamp('2026-11-06 10:15', tz='Asia/Kolkata'), 'close'] = np.nan
    require_intraday_bar(frame, '2026-11-06 10:15:25+05:30', 'TCS')


def test_intraday_runtime_blocks_stale_feed_before_ledger_write(tmp_path):
    from conftest import intraday_sessions
    from nsebot.config import BotConfig
    from nsebot.engine.intraday import IntradayEngine
    from nsebot.broker.paper import PaperBroker
    frame = intraday_sessions(n_sessions=1, start='2026-11-06')
    stale = frame[frame.datetime < pd.Timestamp('2026-11-06 10:10', tz='Asia/Kolkata')]

    class Feed:
        def daily(self, *args, **kwargs):
            return {}

        def intraday(self, symbols, *args, **kwargs):
            return {symbol: stale for symbol in symbols}

    ledger = Ledger(str(tmp_path), 'intraday', 100_000)
    ledger.save()
    before = {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    engine = IntradayEngine(BotConfig(), PaperBroker(), ledger, universe=['TCS'])
    with pytest.raises(DataFreshnessError, match='intraday bar'):
        engine.run_session(Feed(), clock=lambda: pd.Timestamp('2026-11-06 10:15:25', tz='Asia/Kolkata'))
    assert {p: p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()} == before
