"""Validate local official NSE daily reports; never download, trade, or splice prices."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from ..freshness import DataFreshnessError, require_daily_session


def _read(path, columns):
    frame = pd.read_csv(path)
    frame.columns = frame.columns.str.strip()
    if not frame.columns.is_unique or not set(columns).issubset(frame.columns):
        raise DataFreshnessError(f'{Path(path).name}: unexpected NSE report schema')
    return frame


def load_official_snapshot(cash_path, index_path, trade_date):
    """Return separate, unadjusted one-session frames for the approved symbols."""
    day = pd.Timestamp(trade_date).normalize()
    cash = _read(cash_path, ['TradDt', 'Sgmt', 'Src', 'FinInstrmTp', 'TckrSymb', 'SctySrs',
                             'OpnPric', 'HghPric', 'LwPric', 'ClsPric', 'TtlTradgVol'])
    dates = pd.to_datetime(cash['TradDt'], format='%Y-%m-%d', errors='coerce')
    if dates.isna().any() or not (dates == day).all():
        raise DataFreshnessError('cash bhavcopy is missing the requested date or contains another trade date')
    index = _read(index_path, ['Index Name', 'Index Date', 'Open Index Value', 'High Index Value',
                               'Low Index Value', 'Closing Index Value', 'Volume'])
    out = {}
    for symbol in ('RELIANCE', 'TCS'):
        rows = cash[(cash['TckrSymb'].str.strip() == symbol) & (cash['SctySrs'].str.strip() == 'EQ')]
        if len(rows) != 1:
            raise DataFreshnessError(f'{symbol}: expected exactly one NSE EQ cash row')
        row = rows.iloc[0]
        if (row['Sgmt'], row['Src'], row['FinInstrmTp']) != ('CM', 'NSE', 'STK'):
            raise DataFreshnessError(f'{symbol}: wrong exchange, segment or instrument type')
        # ClsPric is the official close; LastPric and SttlmPric are not substitutes.
        out[symbol] = pd.DataFrame([{'datetime': day, 'open': row['OpnPric'], 'high': row['HghPric'],
                                     'low': row['LwPric'], 'close': row['ClsPric'],
                                     'volume': row['TtlTradgVol']}])
    rows = index[index['Index Name'].str.strip().str.upper() == 'NIFTY 50']
    if len(rows) != 1:
        raise DataFreshnessError('NIFTY 50: expected exactly one index row')
    row = rows.iloc[0]
    if pd.to_datetime(row['Index Date'], format='%d-%m-%Y', errors='coerce') != day:
        raise DataFreshnessError('NIFTY 50: wrong or invalid report date')
    out['^NSEI'] = pd.DataFrame([{'datetime': day, 'open': row['Open Index Value'],
                                 'high': row['High Index Value'], 'low': row['Low Index Value'],
                                 'close': row['Closing Index Value'], 'volume': row['Volume']}])
    for symbol, frame in out.items():
        for column in ('open', 'high', 'low', 'close', 'volume'):
            frame[column] = pd.to_numeric(frame[column], errors='coerce')
        require_daily_session(frame, day, symbol, is_index=symbol.startswith('^'))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cash', required=True, type=Path)
    parser.add_argument('--index', required=True, type=Path)
    parser.add_argument('--date', required=True)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(argv)
    frames = load_official_snapshot(args.cash, args.index, args.date)
    report = {'status': 'PASS', 'trade_date': args.date,
              'dataset': 'Official NSE unadjusted one-session verification snapshot',
              'source_delivery': 'user-supplied reports; no network request',
              'limitations': 'Not a historical backtest. No Yahoo splice or automatic broker/engine use.',
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in (args.cash, args.index)},
              'symbols': {symbol: {'rows': len(frame), 'close': float(frame['close'].iloc[0])}
                          for symbol, frame in frames.items()}}
    args.out.mkdir(parents=True, exist_ok=False)
    for symbol, frame in frames.items():
        frame.to_csv(args.out / (symbol.replace('^', 'INDEX_') + '_official.csv'),
                     index=False, encoding='utf-8', mode='x')
    with (args.out / 'summary.json').open('x', encoding='utf-8') as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
