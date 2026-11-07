"""Replay safety and end-to-end accounting; all prices below are synthetic."""
import numpy as np
import pandas as pd
import pytest

from conftest import daily_frame
from nsebot.backtest import report, run_backtest


def history(n=240):
    stock = daily_frame(np.linspace(100, 140, n), volume=1_000_000.)
    index = daily_frame(np.linspace(20_000, 22_000, n))
    return {'SAMPLE': stock}, index


def test_short_history_fails_before_state_is_created(tmp_path):
    universe, index = history(1)
    target = tmp_path / 'simulation'
    with pytest.raises(ValueError, match='need more than 200 index sessions'):
        run_backtest(universe, index, workdir=target)
    assert not target.exists()


@pytest.mark.parametrize('defect', ['duplicate', 'unordered', 'nan', 'ohlc', 'volume'])
def test_invalid_bars_fail_before_replay(tmp_path, defect):
    universe, index = history()
    frame = universe['SAMPLE']
    if defect == 'duplicate':
        frame.loc[1, 'datetime'] = frame.loc[0, 'datetime']
    elif defect == 'unordered':
        frame.loc[[0, 1], 'datetime'] = frame.loc[[1, 0], 'datetime'].to_numpy()
    elif defect == 'nan':
        frame.loc[0, 'close'] = np.nan
    elif defect == 'ohlc':
        frame.loc[0, 'high'] = 1.
    else:
        frame.loc[0, 'volume'] = 0.
    target = tmp_path / 'simulation'
    with pytest.raises(ValueError, match='BACKTEST DATA'):
        run_backtest(universe, index, workdir=target)
    assert not target.exists()


def test_replay_refuses_existing_files_without_modifying_them(tmp_path):
    universe, index = history()
    sentinel = tmp_path / 'private-state.txt'
    sentinel.write_text('preserve me', encoding='utf-8')
    with pytest.raises(ValueError, match='workdir must be new or empty'):
        run_backtest(universe, index, workdir=tmp_path)
    assert sentinel.read_text(encoding='utf-8') == 'preserve me'
    assert list(tmp_path.iterdir()) == [sentinel]


def test_no_signal_replay_conserves_cash_and_is_reproducible(tmp_path):
    universe, index = history()
    outputs = []
    for name in ('first', 'second'):
        _, equity, trades, ledger = run_backtest(
            universe, index, initial_cash=33_333.33, workdir=tmp_path / name)
        assert len(equity) == 40
        assert (equity == 33_333.33).all()
        assert trades.empty
        assert ledger.cash == 33_333.33
        assert not ledger.positions
        outputs.append(equity)
    pd.testing.assert_series_equal(*outputs)


def test_report_rejects_missing_benchmark_instead_of_fabricating_close(monkeypatch):
    import nsebot.backtest as bt
    universe, index = history()
    equity = pd.Series(33_333.33, index=pd.date_range('2030-01-01', periods=40))
    monkeypatch.setattr(bt, 'run_backtest', lambda *a, **k: (None, equity, pd.DataFrame(), None))
    with pytest.raises(ValueError, match='no forward filling'):
        report(universe, index)


def test_main_honors_sleeve_capital_and_preserves_old_results(monkeypatch, tmp_path):
    import nsebot.backtest as bt
    calls = []
    class OfflineProvider:
        def daily(self, symbols, **kwargs):
            return {symbol: daily_frame(np.full(240, 100.)) for symbol in symbols}
    def fake_report(universe, index, **kwargs):
        calls.append(kwargs)
        return 'Synthetic test receipt: INR 33,333.33', pd.Series([33_333.33]), pd.DataFrame()
    monkeypatch.setattr('nsebot.data.YahooProvider', OfflineProvider)
    monkeypatch.setattr(bt, 'report', fake_report)
    monkeypatch.setenv('SWING_CAPITAL', '33333.33')
    old = tmp_path / 'BACKTEST.md'
    old.write_text('old report', encoding='utf-8')
    bt.main(tmp_path)
    bt.main(tmp_path)
    assert old.read_text(encoding='utf-8') == 'old report'
    assert len(list(tmp_path.glob('backtest-*/BACKTEST.md'))) == 2
    assert all(c['initial_cash'] == 33_333.33 for c in calls)
    assert calls[0]['workdir'] != calls[1]['workdir']
    assert all(c['workdir'].parent.parent == tmp_path for c in calls)


def test_bad_capital_fails_before_provider_or_files(monkeypatch, tmp_path):
    import nsebot.backtest as bt
    def forbidden():
        pytest.fail('provider must not be constructed')
    monkeypatch.setattr('nsebot.data.YahooProvider', forbidden)
    monkeypatch.setenv('SWING_CAPITAL', 'nan')
    with pytest.raises(ValueError, match='SWING_CAPITAL'):
        bt.main(tmp_path / 'new-output')
    assert not (tmp_path / 'new-output').exists()


def test_report_assigns_boundary_trade_once_and_includes_boundary_return(monkeypatch):
    import nsebot.backtest as bt
    universe, index = history(300)
    dates = pd.DatetimeIndex(index['datetime'].iloc[200:])
    equity = pd.Series(50_000., index=dates)
    equity.iloc[60:] = 55_000.
    trades = pd.DataFrame(dict(exit_time=[dates[59], dates[60]], net_pnl=[1., 2.],
                               net_r=[.1, .2], costs=[1., 1.], exit_reason=['stop', 'stop']))
    monkeypatch.setattr(bt, 'run_backtest', lambda *a, **k: (None, equity, trades, None))
    md, _, _ = bt.report(universe, index)
    rows = {parts[0]: parts for line in md.splitlines() if line.startswith('| ')
            if (parts := [p.strip() for p in line.split('|')[1:-1]])}
    assert rows['Full'][6] == '2'
    assert rows['Earlier 60%'][6] == rows['Later 40%'][6] == '1'
    assert rows['Later 40%'][1] == '+10.0%'
    assert 'not untouched out-of-sample evidence' in md


def test_unused_index_volume_can_stay_missing_without_changing_replay(tmp_path):
    universe, index = history()
    _, expected, _, _ = run_backtest(universe, index, workdir=tmp_path / 'complete')
    index.loc[[2, 220], 'volume'] = np.nan
    _, actual, _, _ = run_backtest(universe, index, workdir=tmp_path / 'missing-index-volume')
    pd.testing.assert_series_equal(actual, expected)
    assert index['volume'].isna().sum() == 2  # Missing data was not replaced with zero.


@pytest.mark.parametrize('field,value', [('close', np.nan), ('volume', np.inf), ('volume', -1.)])
def test_optional_index_volume_does_not_relax_prices_or_allow_invalid_volume(tmp_path, field, value):
    universe, index = history()
    index.loc[220, field] = value
    with pytest.raises(ValueError, match='BACKTEST DATA'):
        run_backtest(universe, index, workdir=tmp_path / 'reject')


def test_equity_named_index_cannot_get_the_index_volume_exception(tmp_path):
    universe, index = history()
    universe = {'index': universe['SAMPLE']}
    universe['index'].loc[220, 'volume'] = np.nan
    with pytest.raises(ValueError, match='BACKTEST DATA'):
        run_backtest(universe, index, workdir=tmp_path / 'reject')
