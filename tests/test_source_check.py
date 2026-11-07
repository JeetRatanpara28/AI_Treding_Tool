"""Official report recovery must reject bad prices, dates and duplicate rows."""

import pandas as pd
import pytest

from nsebot.freshness import DataFreshnessError
from nsebot.research.source_check import load_official_snapshot, main


@pytest.fixture
def reports(tmp_path):
    cash = pd.DataFrame([{'TradDt': '2026-11-06', 'Sgmt': 'CM', 'Src': 'NSE', 'FinInstrmTp': 'STK',
                          'TckrSymb': symbol, 'SctySrs': 'EQ', 'OpnPric': 100., 'HghPric': 105.,
                          'LwPric': 99., 'ClsPric': 104., 'LastPric': 103., 'TtlTradgVol': 1000}
                         for symbol in ('RELIANCE', 'TCS')])
    index = pd.DataFrame([{'Index Name': 'Nifty 50', 'Index Date': '06-11-2026',
                           'Open Index Value': 1000., 'High Index Value': 1020., 'Low Index Value': 990.,
                           'Closing Index Value': 1010., 'Volume': 10000}])
    cp, ip = tmp_path / 'cash.csv', tmp_path / 'index.csv'
    cash.to_csv(cp, index=False)
    index.to_csv(ip, index=False)
    return cp, ip


def test_official_close_is_not_last_price_and_index_mapping_is_explicit(reports):
    out = load_official_snapshot(*reports, '2026-11-06')
    assert set(out) == {'RELIANCE', 'TCS', '^NSEI'}
    assert out['TCS']['close'].iloc[0] == 104.
    assert out['^NSEI']['close'].iloc[0] == 1010.


@pytest.mark.parametrize('problem', ['cash_date', 'index_date', 'missing_close', 'missing_index_close',
                                    'duplicate_stock', 'duplicate_index', 'wrong_segment'])
def test_invalid_official_report_cannot_be_used(reports, problem):
    cp, ip = reports
    cash, index = pd.read_csv(cp), pd.read_csv(ip)
    if problem == 'cash_date':
        cash.loc[0, 'TradDt'] = '2026-11-05'
    elif problem == 'index_date':
        index.loc[0, 'Index Date'] = '05-11-2026'
    elif problem == 'missing_close':
        cash.loc[0, 'ClsPric'] = float('nan')
    elif problem == 'missing_index_close':
        index.loc[0, 'Closing Index Value'] = float('nan')
    elif problem == 'duplicate_stock':
        cash = pd.concat([cash, cash.iloc[[0]]])
    elif problem == 'duplicate_index':
        index = pd.concat([index, index])
    elif problem == 'wrong_segment':
        cash.loc[0, 'Sgmt'] = 'FO'
    cash.to_csv(cp, index=False)
    index.to_csv(ip, index=False)
    with pytest.raises(DataFreshnessError):
        load_official_snapshot(cp, ip, '2026-11-06')


def test_verified_output_refuses_existing_destination(reports, tmp_path):
    cp, ip = reports
    out = tmp_path / 'result'
    args = ['--cash', str(cp), '--index', str(ip), '--date', '2026-11-06', '--out', str(out)]
    assert main(args) == 0
    before = {p: p.read_bytes() for p in out.iterdir()}
    with pytest.raises(FileExistsError):
        main(args)
    assert {p: p.read_bytes() for p in out.iterdir()} == before
