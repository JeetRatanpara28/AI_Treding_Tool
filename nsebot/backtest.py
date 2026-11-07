"""Historical replay of the shared swing engine, with causal exit timing.

Replay uses PaperBroker and isolated Ledger state. Close-observed discretionary
exits wait for the next available open; protective stops remain gap-aware.
The daily runner's legacy same-close convention is separate. Features must pass
prefix-invariance tests; those tests do not certify an external market dataset.
Use research.offline_backtest for reviewed local data without downloads.
"""

import logging
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from .broker.paper import PaperBroker
from .config import BotConfig
from .engine.market_view import DailyMarket
from .engine.swing import SwingEngine
from .ledger import Ledger
from .signals import ReversionSignalEngine

logger = logging.getLogger(__name__)
IS_FRACTION = 0.6


def validate_history(universe, index_df, warmup=200):
    """Reject unusable replay inputs before creating any simulation state.

    Index volume may be unavailable: this swing replay uses index prices only.
    Equity volume and every OHLC price remain mandatory. Runtime freshness and
    other consumers keep their own stricter contracts.
    This checks supplied bars, not source rights, exchange-calendar coverage or
    corporate actions. Those still need a reviewed dataset before real research.
    """
    if isinstance(warmup, bool) or not isinstance(warmup, int) or warmup < 0:
        raise ValueError('warmup must be a nonnegative integer')
    if not universe:
        raise ValueError('BACKTEST DATA: equity universe is empty')
    fields = ['open', 'high', 'low', 'close', 'volume']
    inputs = [('index', index_df, True), *((s, f, False) for s, f in universe.items())]
    for label, frame, is_index in inputs:
        if frame is None or frame.empty or not {'datetime', *fields}.issubset(frame.columns):
            raise ValueError(f'BACKTEST DATA: {label}: missing daily OHLCV columns or rows')
        dates = pd.DatetimeIndex(pd.to_datetime(frame['datetime'], errors='coerce'))
        if (dates.tz is not None or dates.isna().any() or not dates.is_unique
                or not dates.is_monotonic_increasing or not dates.equals(dates.normalize())):
            raise ValueError(f'BACKTEST DATA: {label}: dates must be unique ordered naive session dates')
        values = frame[fields].apply(pd.to_numeric, errors='coerce').to_numpy(dtype=float)
        if not np.isfinite(values[:, :4]).all() or (not is_index and not np.isfinite(values[:, 4]).all()):
            raise ValueError(f'BACKTEST DATA: {label}: missing or non-finite OHLCV')
        o, h, l, c, v = values.T
        if ((np.minimum.reduce([o, h, l, c]) <= 0).any()
                or (h < np.maximum.reduce([o, l, c])).any()
                or (l > np.minimum.reduce([o, h, c])).any()
                or (v < 0).any() or np.isinf(v).any() or (not is_index and (v == 0).any())):
            raise ValueError(f'BACKTEST DATA: {label}: invalid OHLCV')
    if len(index_df) <= warmup:
        raise ValueError(f'BACKTEST DATA: need more than {warmup} index sessions; '
                         f'got {len(index_df)}. No performance result is available.')


def _curve(eq):
    eq = eq.dropna()
    if len(eq) < 20:
        return {}
    r = eq.pct_change().dropna()
    yrs = len(r) / 252
    vol = r.std() * np.sqrt(252)
    return {'cagr': (eq.iloc[-1] / eq.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan,
            'sharpe': r.mean() * 252 / vol if vol > 0 else np.nan,
            'maxdd': float((eq / eq.cummax() - 1).min()), 'ret': eq.iloc[-1] / eq.iloc[0] - 1}


def _trades(t):
    if t is None or len(t) == 0:
        return {'n': 0}
    net = t['net_pnl'].astype(float)
    return {'n': len(t), 'win': float((net > 0).mean()), 'net_sum': float(net.sum()),
            'avg_net': float(net.mean()), 'avg_r': float(t['net_r'].astype(float).mean()),
            'costs': float(t['costs'].astype(float).sum())}


def run_backtest(universe, index_df, cfg=None, initial_cash=50_000.0, warmup=200, workdir=None,
                 slippage_bps=5.0, historical_execution=False):
    validate_history(universe, index_df, warmup)
    if not np.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError('initial_cash must be finite and positive')
    if workdir is not None and Path(workdir).exists() and any(Path(workdir).iterdir()):
        raise ValueError('BACKTEST STATE: workdir must be new or empty; existing files are preserved')
    if historical_execution:
        from .research.historical_execution import DatedPaperBroker
        broker = DatedPaperBroker(universe, slippage_bps=slippage_bps,
                                  stop_slippage_bps=slippage_bps)
    else:
        broker = PaperBroker(slippage_bps=slippage_bps, stop_slippage_bps=slippage_bps)
    cfg = cfg or BotConfig()
    market = DailyMarket(universe, index_df, ReversionSignalEngine(cfg.reversion))
    root = workdir or tempfile.mkdtemp(prefix='nsebot_bt_')
    ledger = Ledger(root, 'swing', initial_cash)
    engine = SwingEngine(cfg, broker, ledger, workdir=root, log=lambda m: None,
                         defer_close_exits=True)
    dates = market.dates[warmup:]
    for d in dates:
        if historical_execution:
            broker.set_session(d)
        engine.run(market, d)
    eq = ledger.equity_history()
    eq = pd.Series(eq['equity'].astype(float).to_numpy(), index=pd.to_datetime(eq['session']))
    trades = ledger.closed_trades()
    return market, eq, trades, ledger


def report(universe, index_df, cfg=None, initial_cash=50_000.0, workdir=None, slippage_bps=5.0,
           historical_execution=False):
    market, eq, trades, ledger = run_backtest(universe, index_df, cfg, initial_cash, workdir=workdir,
                                              slippage_bps=slippage_bps,
                                              historical_execution=historical_execution)
    if eq.empty:
        raise ValueError('BACKTEST DATA: no evaluated sessions; no performance result is available')
    cut_pos = max(1, min(len(eq) - 1, int(len(eq) * IS_FRACTION)))
    nifty = (index_df.set_index(pd.to_datetime(index_df['datetime']))['close']
             .reindex(eq.index))
    if nifty.isna().any():
        raise ValueError('BACKTEST DATA: benchmark is missing evaluated sessions; no forward filling allowed')
    tr = trades.copy()
    if len(tr):
        tr['exit_time'] = pd.to_datetime(tr['exit_time'])
    halves = {'Full': (eq.index[0], eq.index[-1])}
    if len(eq) > 1:
        halves.update({'Earlier 60%': (eq.index[0], eq.index[cut_pos - 1]),
                       'Later 40%': (eq.index[cut_pos], eq.index[-1])})
    md = ['## Portfolio backtest — shared swing engine with causal replay timing', '',
          f"₹{initial_cash:,.0f} paper book · {eq.index[0].date()} → {eq.index[-1].date()} "
          f"({len(eq)} sessions) · shared signal/sizing/ledger code (causal historical exits, "
          f"risk caps, breakers, regime dial; "
          f"{'dated exchange/IPFT and monthly ticks, conservative DP assumption' if historical_execution else 'static cost assumptions'}).", '',
          '| period | return | CAGR | Sharpe | max DD | Nifty CAGR | trades | win | net ₹ | avg net R | costs ₹ |',
          '|---|---|---|---|---|---|---|---|---|---|---|']
    md.insert(2, 'Execution: close-observed exits execute at the next available open; '
                 'protective stops/gaps are intrabar. All exit types pay configured adverse slippage '
                 f'({slippage_bps:g} bps) and adverse tick rounding. '
                 'The daily runner retains its legacy same-close convention. '
                 'Chronological splits are descriptive, not untouched out-of-sample evidence. '
                 'Nifty is a gross price-index reference, not a net investable fund. '
                 'Final equity marks open positions without assuming liquidation.')
    for name, (a, b) in halves.items():
        # Include the previous close as the later segment's return anchor while
        # assigning each exit/trade to exactly one segment.
        anchor = eq.index[max(0, eq.index.get_loc(a) - 1)]
        c = _curve(eq.loc[anchor:b])
        n = _curve(nifty.loc[anchor:b])
        t = _trades(tr[(tr['exit_time'] >= a) & (tr['exit_time'] <= b)] if len(tr) else tr)
        if not c:
            continue
        md.append(f"| {name} | {c['ret'] * 100:+.1f}% | {c['cagr'] * 100:+.1f}% | {c['sharpe']:.2f} | "
                  f"{c['maxdd'] * 100:.1f}% | {n.get('cagr', float('nan')) * 100:+.1f}% | {t['n']} | "
                  + (f"{t['win'] * 100:.0f}% | {t['net_sum']:+,.0f} | {t['avg_r']:+.3f} | {t['costs']:,.0f} |"
                     if t['n'] else '— | — | — | — |'))
    if len(tr):
        md += ['', '| exit reason | trades | net ₹ | avg net R |', '|---|---|---|---|']
        for reason, g in tr.groupby(tr['exit_reason'].str.split(':').str[0]):
            md.append(f"| {reason} | {len(g)} | {g['net_pnl'].sum():+,.0f} | {g['net_r'].mean():+.3f} |")
        exposure = (eq.index.size and len(tr) / eq.index.size)
        md += ['', f"Average trades per session: {exposure:.2f} · final equity ₹{eq.iloc[-1]:,.0f} · "
                   f"worst trade ₹{tr['net_pnl'].min():+,.0f} · best ₹{tr['net_pnl'].max():+,.0f}"]
    return '\n'.join(md), eq, trades


def main(out_dir='research_results'):
    from .data import YahooProvider
    from .universe import INDEX_SYMBOL, SWING_UNIVERSE
    initial_cash = float(os.environ.get('SWING_CAPITAL', '50000'))
    if not np.isfinite(initial_cash) or initial_cash <= 0:
        raise ValueError('SWING_CAPITAL must be finite and positive')
    os.makedirs(out_dir, exist_ok=True)
    run_dir = Path(tempfile.mkdtemp(prefix='backtest-', dir=out_dir))
    prov = YahooProvider()
    universe = prov.daily(SWING_UNIVERSE, lookback_days=520)
    index_df = prov.daily([INDEX_SYMBOL], lookback_days=520)[INDEX_SYMBOL]
    md, eq, trades = report(universe, index_df, initial_cash=initial_cash,
                            workdir=run_dir / 'engine')
    md += f'\n\nResults: {run_dir}\n'
    eq.to_csv(run_dir / 'backtest_equity.csv', encoding='utf-8', mode='x')
    trades.to_csv(run_dir / 'backtest_trades.csv', index=False, encoding='utf-8', mode='x')
    with (run_dir / 'BACKTEST.md').open('x', encoding='utf-8') as fh:
        fh.write(md + '\n')
    return md
