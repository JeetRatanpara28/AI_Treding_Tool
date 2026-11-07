import json

import numpy as np
import pytest

from conftest import daily_frame
from nsebot.research.offline_data import load_dataset


def dataset(tmp_path, n=452):
    frame = daily_frame(np.linspace(100., 200., n), volume=1_000_000.)
    frame.to_csv(tmp_path / 'stock.csv', index=False)
    frame.to_csv(tmp_path / 'index.csv', index=False)
    frame[['datetime']].to_csv(tmp_path / 'sessions.csv', index=False)
    manifest = dict(format_version=1, data_kind='synthetic', source='Generated fixture',
                    source_permission='Synthetic local test', calendar_source='Synthetic business days',
                    price_basis='split_adjusted_price', corporate_actions_reviewed=True,
                    sessions='sessions.csv', index='index.csv', stocks={'SAMPLE': 'stock.csv'})
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(manifest), encoding='utf-8')
    return path, frame, manifest


def test_import_is_offline_exact_and_hashes_original_bytes(tmp_path):
    path, frame, _ = dataset(tmp_path)
    universe, index, receipt = load_dataset(path)
    assert universe['SAMPLE']['close'].tolist() == frame['close'].tolist()
    assert index['datetime'].equals(universe['SAMPLE']['datetime'])
    assert receipt['evaluation_sessions'] == 252
    assert receipt['data_kind'] == 'synthetic'
    assert len(receipt['source_sha256']) == 4


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'nan', 'timezone', 'ohlc', 'order'])
def test_import_rejects_bad_history_without_repairing_it(tmp_path, defect):
    path, frame, _ = dataset(tmp_path)
    if defect == 'missing':
        frame = frame.iloc[1:]
    elif defect == 'duplicate':
        frame.loc[1, 'datetime'] = frame.loc[0, 'datetime']
    elif defect == 'nan':
        frame.loc[20, 'close'] = np.nan
    elif defect == 'timezone':
        frame['datetime'] = frame['datetime'].dt.tz_localize('UTC')
    elif defect == 'ohlc':
        frame.loc[20, 'low'] = 9999.
    else:
        frame = frame.iloc[::-1]
    filename = tmp_path / 'stock.csv'
    frame.to_csv(filename, index=False)
    before = filename.read_bytes()
    with pytest.raises(ValueError):
        load_dataset(path)
    assert filename.read_bytes() == before


@pytest.mark.parametrize('field,value', [('source_permission', ''), ('price_basis', 'raw'),
                                         ('corporate_actions_reviewed', False), ('format_version', True)])
def test_import_requires_explicit_metadata(tmp_path, field, value):
    path, _, meta = dataset(tmp_path)
    meta[field] = value
    path.write_text(json.dumps(meta), encoding='utf-8')
    with pytest.raises(ValueError, match='OFFLINE DATA'):
        load_dataset(path)


def test_import_refuses_path_escape_before_reading_outside_csv(tmp_path):
    folder = tmp_path / 'data'
    folder.mkdir()
    path, _, meta = dataset(folder)
    (tmp_path / 'outside.csv').write_text('private outside file', encoding='utf-8')
    meta['index'] = '../outside.csv'
    path.write_text(json.dumps(meta), encoding='utf-8')
    with pytest.raises(ValueError, match='inside the manifest folder'):
        load_dataset(path)


def test_import_requires_evaluation_history_beyond_warmup(tmp_path):
    path, _, _ = dataset(tmp_path, n=451)
    with pytest.raises(ValueError, match='need 252 evaluated sessions'):
        load_dataset(path)


def test_import_rejects_duplicate_csv_headers(tmp_path):
    path, _, _ = dataset(tmp_path)
    stock = tmp_path / 'stock.csv'
    raw = stock.read_text(encoding='utf-8')
    stock.write_text(raw.replace('open,high', 'open,open', 1), encoding='utf-8')
    with pytest.raises(ValueError, match='duplicate CSV column'):
        load_dataset(path)


def test_offline_experiment_runs_all_fixed_scenarios_without_network(tmp_path, monkeypatch):
    import socket
    from nsebot.research.offline_backtest import run
    path, _, _ = dataset(tmp_path)
    def forbidden(*a, **kw):
        pytest.fail('offline research must not open a socket')
    monkeypatch.setattr(socket, 'socket', forbidden)
    out, result = run(path, tmp_path / 'results')
    assert result['data_kind'] == 'synthetic'
    assert [s['slippage_bps'] for s in result['scenarios']] == [5., 10., 25.]
    assert all(s['accounting'] == 'PASS' for s in result['scenarios'])
    assert all(s['closed_trades'] == 0 for s in result['scenarios'])
    assert all(s['final_equity'] == 33_333.33 for s in result['scenarios'])
    assert all(s['average_invested_fraction'] == s['sessions_in_market_fraction'] == 0
               for s in result['scenarios'])
    assert all(s['evidence'] == 'SYNTHETIC_ONLY' for s in result['scenarios'])
    assert len(list(out.glob('slippage-*bps/BACKTEST.md'))) == 3
    json.loads((out / 'summary.json').read_text(encoding='utf-8'))


def test_dated_execution_requires_reviewed_raw_share_units(tmp_path):
    path, _, meta = dataset(tmp_path)
    meta['execution_model'] = 'dated_nse_cash_v1'
    path.write_text(json.dumps(meta), encoding='utf-8')
    with pytest.raises(ValueError, match='raw price/share units'):
        load_dataset(path)


def test_changed_review_evidence_is_rejected_before_replay(tmp_path):
    import hashlib
    path, _, meta = dataset(tmp_path)
    evidence = tmp_path / 'review.json'
    evidence.write_text('{"review": "synthetic"}', encoding='utf-8')
    meta['evidence_sha256'] = {'review.json': hashlib.sha256(evidence.read_bytes()).hexdigest()}
    path.write_text(json.dumps(meta), encoding='utf-8')
    _, _, receipt = load_dataset(path)
    assert receipt['source_sha256']['review.json'] == meta['evidence_sha256']['review.json']
    evidence.write_text('{"review": "changed"}', encoding='utf-8')
    with pytest.raises(ValueError, match='evidence checksum mismatch'):
        load_dataset(path)


def test_dated_replay_and_benchmark_share_frozen_fees_without_network(tmp_path, monkeypatch):
    import socket
    import pandas as pd
    from nsebot.research.offline_backtest import run
    path, frame, meta = dataset(tmp_path)
    frame['datetime'] = pd.bdate_range('2022-01-03', periods=len(frame))
    frame[['datetime']].to_csv(tmp_path / 'sessions.csv', index=False)
    for name in ('stock.csv', 'index.csv'):
        frame.to_csv(tmp_path / name, index=False)
    meta.update(execution_model='dated_nse_cash_v1', raw_price_scale_verified=True)
    path.write_text(json.dumps(meta), encoding='utf-8')
    def forbidden(*a, **kw):
        pytest.fail('dated offline replay must not open a socket')
    monkeypatch.setattr(socket, 'socket', forbidden)
    out, result = run(path, tmp_path / 'results')
    frozen = json.loads((out / 'frozen_spec.json').read_text(encoding='utf-8'))
    assert frozen['source']['execution_model'] == 'dated_nse_cash_v1'
    assert frozen['charges']['dp_inr_including_gst'] == 15.93
    assert frozen['charges']['exchange_ipft_inr_per_crore'][0]['exchange'] == 345.
    for case in result['scenarios']:
        assert case['accounting'] == 'PASS'
        assert case['evidence'] == 'SYNTHETIC_ONLY'
        h = case['benchmark_holdings']['SAMPLE']
        value = h['qty'] * h['entry_price']
        # Independent entry arithmetic: STT + stamp + dated exchange/IPFT/SEBI/GST.
        expected = value * .00115 + value * (.000034501 + .000001) * 1.18
        assert h['entry_costs'] == pytest.approx(expected)
        assert case['closed_trades'] == 0
    assert result['evaluation_sessions'] == 252
