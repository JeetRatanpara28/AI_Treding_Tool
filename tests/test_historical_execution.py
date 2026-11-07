"""Independent historical fee arithmetic and causal monthly raw-tick anchors."""
import math

import pandas as pd
import pytest

from nsebot.costs import DEFAULT_CHARGES
from nsebot.research.historical_execution import (
    DatedPaperBroker, HistoricalTickTable, historical_charges, historical_execution_spec,
)
from nsebot.risk.exits import Position


def raw(dates, closes):
    return {'SAMPLE': pd.DataFrame({'datetime': pd.to_datetime(dates), 'close': closes})}


@pytest.mark.parametrize('day,total', [
    ('2021-11-08', 345.01), ('2023-03-31', 345.01),
    ('2023-04-01', 335.), ('2024-03-31', 335.),
    ('2024-04-01', 332.), ('2024-09-30', 332.),
    ('2024-10-01', 307.), ('2026-02-28', 307.),
    ('2026-03-01', 307.), ('2026-11-06', 307.),
])
def test_exchange_and_ipft_dated_boundaries(day, total):
    charges = historical_charges(day)
    assert charges.exchange_pct * 10_000_000 == pytest.approx(total)
    # INR10,000 each way: STT20, buy stamp1.5, SEBI.02, DP15.93.
    exchange = total * .002
    expected = 20. + 1.5 + exchange + .02 + .18 * (exchange + .02) + 15.93
    assert charges.cnc(10_000., 10_000.) == pytest.approx(expected)
    assert DEFAULT_CHARGES.exchange_pct == .0000297  # Runtime defaults preserved.
    assert DEFAULT_CHARGES.dp_charge_inr == 15.34


@pytest.mark.parametrize('day', ['2021-11-07', '2026-11-07', '2025-01-01T12:00:00',
                                '2025-01-01T00:00:00Z', 'invalid', None])
def test_unsupported_dates_fail_closed(day):
    with pytest.raises(ValueError, match='HISTORICAL EXECUTION'):
        historical_charges(day)


def test_spec_is_a_fresh_copy_with_explicit_assumptions():
    spec = historical_execution_spec()
    assert spec['dp_inr_including_gst'] == 15.93
    assert 'same-day' in spec['delivery_basis']
    spec['exchange_ipft_inr_per_crore'].clear()
    assert len(historical_execution_spec()['exchange_ipft_inr_per_crore']) == 5


def test_tick_revision_uses_previous_month_not_current_or_future_price():
    universe = raw(['2024-05-31', '2024-06-10', '2024-06-28', '2024-07-01'],
                   [249., 9000., 251., 200.])
    ticks = HistoricalTickTable(universe)
    ticks.set_session('2024-06-07')
    assert ticks.tick('SAMPLE', 1.) == .05
    ticks.set_session('2024-06-10')
    assert ticks.tick('SAMPLE', 9000.) == .01
    ticks.set_session('2024-06-28')
    assert ticks.tick('SAMPLE', 251.) == .01
    ticks.set_session('2024-07-01')
    assert ticks.tick('SAMPLE', 200.) == .05
    universe['SAMPLE'].loc[1:, 'close'] *= 100.
    changed = HistoricalTickTable(universe).set_session('2024-06-10')
    assert changed.tick('SAMPLE', 9000.) == .01


@pytest.mark.parametrize('price,tick', [
    (249.99, .01), (250., .05), (1000., .05), (1000.01, .10),
    (5000., .10), (5000.01, .50), (10000., .50), (10000.01, 1.),
    (20000., 1.), (20000.01, 5.),
])
def test_april2025_boundaries_and_frozen_march28_anchor(price, tick):
    ticks = HistoricalTickTable(raw(['2025-03-28', '2025-03-31', '2025-04-15'],
                                    [price, 90000., 90000.]))
    ticks.set_session('2025-04-14')
    assert ticks.tick('SAMPLE', 2000.) == .05
    ticks.set_session('2025-04-15')
    assert ticks.tick('SAMPLE', 2000.) == tick
    ticks.set_session('2025-04-30')
    assert ticks.tick('SAMPLE', 1.) == tick


def test_missing_anchors_and_unknown_symbols_stop_context_use():
    ticks = HistoricalTickTable(raw(['2025-02-28', '2025-04-01'], [100., 200.]))
    with pytest.raises(ValueError, match='previous-month'):
        ticks.set_session('2025-04-01')
    with pytest.raises(ValueError, match='2025-03-28'):
        ticks.set_session('2025-04-15')
    ticks.set_session('2025-03-01')
    assert ticks.lot('SAMPLE') == 1
    with pytest.raises(ValueError, match='symbol'):
        ticks.tick('UNKNOWN', 1.)
    with pytest.raises(ValueError, match='unknown'):
        ticks.lot('UNKNOWN')
    with pytest.raises(ValueError):
        ticks.set_session('2026-11-07')
    with pytest.raises(ValueError, match='context'):
        ticks.tick('SAMPLE', 1.)


@pytest.mark.parametrize('closes', [[float('nan')], [math.inf], [0.], [-1.]])
def test_invalid_anchor_values_rejected(closes):
    with pytest.raises(ValueError, match='raw close'):
        HistoricalTickTable(raw(['2025-03-28'], closes))


def test_duplicate_and_unsorted_anchor_dates_are_rejected():
    for dates in [['2025-03-28', '2025-03-28'], ['2025-03-28', '2025-03-27']]:
        with pytest.raises(ValueError, match='raw close'):
            HistoricalTickTable(raw(dates, [100., 101.]))


def test_broker_dates_each_fill_and_applies_identical_cost_math():
    universe = raw(['2024-03-28', '2024-04-01', '2024-09-30', '2024-10-01'],
                   [1200., 1200., 1200., 1200.])
    broker = DatedPaperBroker(universe, slippage_bps=0.)
    pending = dict(order_id='SYNTHETIC', spec=dict(symbol='SAMPLE', side='LONG',
        qty=10, product='CNC', stop=90., signal_time='2024-03-28'))
    assert broker.resolve_entry(pending, None).status == 'WAIT'
    entry = broker.resolve_entry(pending, dict(open=100., datetime='2024-04-01')).fill
    assert broker.session == pd.Timestamp('2024-04-01')
    assert entry.costs == pytest.approx(historical_charges('2024-04-01').cnc(1000., 0., False))
    pos = Position('SAMPLE', 'swing', 'LONG', 10, 100., 90., 90.,
                   pd.Timestamp('2024-04-01'), 2.)
    fill = broker.exit(pos, 110., 'time exit', '2024-10-01')
    assert broker.session == pd.Timestamp('2024-10-01')
    assert fill.costs == pytest.approx(historical_charges('2024-10-01').cnc(0., 1100., True))
    assert not broker.is_live


@pytest.mark.parametrize('price', [float('nan'), math.inf, 0., -1.])
def test_broker_refuses_invalid_fill_prices(price):
    broker = DatedPaperBroker(raw(['2025-03-28'], [1200.]))
    pending = dict(spec=dict(symbol='SAMPLE', side='LONG', qty=10, product='CNC', stop=90.))
    with pytest.raises(ValueError, match='entry open'):
        broker.resolve_entry(pending, dict(open=price, datetime='2025-04-15'))
    pos = Position('SAMPLE', 'swing', 'LONG', 10, 100., 90., 90.,
                   pd.Timestamp('2025-04-15'), 2.)
    with pytest.raises(ValueError, match='exit price'):
        broker.exit(pos, price, 'stop', '2025-04-15')
