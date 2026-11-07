"""Synthetic prefix and execution tests; not historical performance evidence."""
import numpy as np
import pandas as pd
import pytest

from conftest import daily_frame
from nsebot.backtest import run_backtest
from nsebot.broker.paper import PaperBroker
from nsebot.config import BotConfig
from nsebot.costs import DEFAULT_CHARGES
from nsebot.engine.market_view import DailyMarket
from nsebot.engine.swing import SwingEngine
from nsebot.ledger import Ledger
from nsebot.risk.exits import Position


def dip_history():
    trend = np.linspace(500., 1500., 260)
    close = np.r_[trend, [1447.5, 1395., 1350., 1357.5, 1395., 1440., 1477.5, 1500., 1515.]]
    stock = daily_frame(close, 300_000.)
    stock['open'] = stock['close'].shift(1).fillna(stock['close'])
    stock['high'] = stock[['open', 'close']].max(axis=1) * 1.004
    stock['low'] = stock[['open', 'close']].min(axis=1) * .996
    index = daily_frame(np.linspace(20_000., 23_000., len(stock)))
    return {'DIP': stock}, index


def test_future_changes_do_not_change_features_signals_regime_or_past_replay(tmp_path):
    universe, index = dip_history()
    cut = 267  # Includes a closed trade plus a future suffix to perturb.
    future = {s: f.copy() for s, f in universe.items()}
    future['DIP'].loc[cut:, ['open', 'high', 'low', 'close']] *= 10
    market = DailyMarket(universe, index)
    altered = DailyMarket(future, index)
    prefix = DailyMarket({s: f.iloc[:cut].copy() for s, f in universe.items()}, index.iloc[:cut])
    pd.testing.assert_frame_equal(market.feats['DIP'].iloc[:cut], prefix.feats['DIP'])
    pd.testing.assert_frame_equal(market.feats['DIP'].iloc[:cut], altered.feats['DIP'].iloc[:cut])
    pd.testing.assert_frame_equal(market.regime.iloc[:cut], prefix.regime)
    for day in index['datetime'].iloc[250:cut]:
        assert market.signals(day) == prefix.signals(day) == altered.signals(day)
    _, full_eq, full_trades, _ = run_backtest(universe, index, workdir=tmp_path / 'full')
    _, prefix_eq, prefix_trades, _ = run_backtest(
        {s: f.iloc[:cut].copy() for s, f in universe.items()}, index.iloc[:cut],
        workdir=tmp_path / 'prefix')
    pd.testing.assert_series_equal(full_eq.loc[prefix_eq.index], prefix_eq)
    closed = full_trades[pd.to_datetime(full_trades['exit_time']) <= prefix_eq.index[-1]]
    pd.testing.assert_frame_equal(closed.reset_index(drop=True), prefix_trades.reset_index(drop=True))
    assert len(full_trades) > 0  # Causality check actually exercises a round trip.
    assert full_trades['costs'].gt(0).all()


def seeded_engine(tmp_path):
    ledger = Ledger(tmp_path, 'swing', 33_333.33)
    engine = SwingEngine(BotConfig(), PaperBroker(), ledger, workdir=tmp_path,
                         defer_close_exits=True)
    pos = Position('SAMPLE', 'swing', 'LONG', 10, 100., 90., 90.,
                   pd.Timestamp('2025-01-01'), 2.,
                   meta={'last_bar': '2025-01-01', 'margin': 1000., 'entry_costs': 0.})
    ledger.positions.append(pos)
    ledger.state['cash'] -= 1000.
    return engine, ledger, pos


def test_close_exit_waits_for_next_open_and_survives_restart(tmp_path):
    stock = daily_frame([100., 110., 120.], volume=1_000_000.)
    stock.loc[2, 'open'] = 112.
    market = DailyMarket({}, stock)
    # DailyMarket deliberately ignores <30 bars: install explicit feature rows
    # for this execution-unit scenario (feature causality is checked above).
    market.feats['SAMPLE'] = stock.assign(ema_exit=[101., 105., 115.], atr=2.,
                                         turnover=1e8).set_index('datetime')
    market.signals = lambda day: []
    engine, ledger, pos = seeded_engine(tmp_path)
    engine.run(market, stock['datetime'].iloc[1])
    assert ledger.closed_trades().empty
    assert pos.meta['close_exit']['signal_time'].startswith('2025-01-02')
    restarted = Ledger(tmp_path, 'swing', 999.)
    engine = SwingEngine(BotConfig(), PaperBroker(), restarted, workdir=tmp_path,
                         defer_close_exits=True)
    engine.run(market, stock['datetime'].iloc[2])
    trade = restarted.closed_trades().iloc[0]
    assert pd.Timestamp(trade['exit_time']) == stock['datetime'].iloc[2]
    assert trade['exit_price'] < 112.  # Open minus slippage, not either day's close.
    assert trade['exit_price'] > 111.
    assert not restarted.positions


@pytest.mark.parametrize('side,price', [('LONG', 80.), ('SHORT', 120.)])
def test_stop_slippage_is_adverse_for_both_directions(side, price):
    pos = Position('SAMPLE', 'swing', side, 10, 100., 90. if side == 'LONG' else 110.,
                   90. if side == 'LONG' else 110., pd.Timestamp('2025-01-01'), 2.)
    fill = PaperBroker(stop_slippage_bps=10.).exit(pos, price, 'stop (gap)', '2025-01-02')
    assert (fill.price < price) if side == 'LONG' else (fill.price > price)
    assert fill.costs > 0


def test_queued_exit_cannot_avoid_a_gap_stop(tmp_path):
    stock = daily_frame([100., 110., 120.], volume=1_000_000.)
    stock.loc[2, ['open', 'low']] = [85., 80.]
    market = DailyMarket({}, stock)
    market.feats['SAMPLE'] = stock.assign(ema_exit=105., atr=2., turnover=1e8).set_index('datetime')
    market.signals = lambda day: []
    engine, ledger, pos = seeded_engine(tmp_path)
    engine.broker.stop_slip = .0005
    pos.meta['last_bar'] = str(stock['datetime'].iloc[1])
    pos.meta['close_exit'] = dict(signal_time=str(stock['datetime'].iloc[1]), reason='max hold 7 bars')
    engine.run(market, stock['datetime'].iloc[2])
    trade = ledger.closed_trades().iloc[0]
    assert trade['exit_reason'] == 'stop (gap)'
    assert trade['exit_price'] < 85.  # Never the old 90 stop or the later 120 close.


@pytest.mark.parametrize('slip', [-1., float('nan'), float('inf'), 10_000.])
def test_invalid_slippage_is_rejected(slip):
    with pytest.raises(ValueError, match='slippage'):
        PaperBroker(slippage_bps=slip)


def test_delivery_legs_reconcile_to_hand_calculated_fees():
    # Research schedule assumptions: buy INR 1,000, sell INR 1,100.
    # STT=2.10, stamp=.15, exchange=.06237, SEBI=.0021,
    # GST=.0116046, DP=15.34 => 17.6660746. No brokerage.
    expected = 2.10 + .15 + .06237 + .0021 + .0116046 + 15.34
    assert DEFAULT_CHARGES.cnc(1000., 1100.) == pytest.approx(expected)
    broker = PaperBroker(slippage_bps=0.)
    pending = dict(order_id='SYNTHETIC', spec=dict(symbol='SAMPLE', side='LONG',
                   qty=10, product='CNC', stop=90., signal_time='2025-01-01'))
    entry = broker.resolve_entry(pending, dict(open=100., datetime='2025-01-02')).fill
    pos = Position('SAMPLE', 'swing', 'LONG', 10, 100., 90., 90.,
                   pd.Timestamp('2025-01-02'), 2.)
    exit_fill = broker.exit(pos, 110., 'synthetic exit', '2025-01-03')
    assert entry.costs + exit_fill.costs == pytest.approx(expected)


def test_opening_gap_cannot_overdraw_paper_cash(tmp_path):
    stock = daily_frame([100., 150., 160.], volume=1_000_000.)
    stock.loc[1, ['open', 'high', 'low']] = [200., 201., 140.]
    market = DailyMarket({}, stock)
    market.feats['SAMPLE'] = stock.assign(ema_exit=999., atr=2., turnover=1e8).set_index('datetime')
    market.signals = lambda day: []
    engine, ledger, _ = seeded_engine(tmp_path)
    ledger.positions.clear()
    ledger.state['cash'] = 33_333.33
    ledger.state['pending'] = [dict(order_id='SYNTHETIC', spec=dict(symbol='SAMPLE', side='LONG',
        qty=200, product='CNC', ref_price=100., stop=90., signal_time='2025-01-01'))]
    outcome = engine.run(market, stock['datetime'].iloc[1])
    assert not outcome['filled']
    assert 'exceeds available paper cash' in outcome['cancelled'][0][1]
    assert ledger.cash == 33_333.33
    assert not ledger.positions and not ledger.state['pending']
