"""Offline fixed swing pilot and buy-and-hold comparison, without downloads.

Uses reviewed local CSVs only. Every run is isolated; existing portfolios are
never used. Synthetic inputs produce engineering evidence, not market results.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np
import pandas as pd

from ..backtest import _curve, report
from ..config import BotConfig
from ..costs import DEFAULT_CHARGES
from ..ledger import Ledger
from ..market import TickTable, round_to_tick
from .offline_data import load_dataset


def buy_and_hold(universe, dates, capital, slippage_bps, historical_execution=False):
    """Predetermined equal-budget buys at session 2 open; session 1 stays cash.
    Integer shares, buy charges and adverse ticks; terminal holdings stay marked
    just like the strategy. No dividends or fictitious index-fund transaction.
    """
    if len(dates) < 2 or not universe:
        raise ValueError('buy-and-hold needs symbols and at least two sessions')
    if not np.isfinite(capital) or capital <= 0 or not 0 <= slippage_bps < 10000:
        raise ValueError('invalid capital or slippage')
    frames = {s: f.set_index('datetime') for s, f in universe.items()}
    ticks, cash, holdings = TickTable(), float(capital), {}
    charges = DEFAULT_CHARGES
    if historical_execution:
        from .historical_execution import HistoricalTickTable, historical_charges
        ticks = HistoricalTickTable(universe)
        ticks.set_session(dates[1])
        charges = historical_charges(dates[1])
    for symbol in sorted(frames):
        raw_open = float(frames[symbol].loc[dates[1], 'open'])
        price = round_to_tick(raw_open * (1 + slippage_bps / 1e4), ticks.tick(symbol, raw_open), 'up')
        budget = capital / len(frames)
        unit_cost = charges.cnc(price, 0., dp_charged=False)
        qty = int(np.floor(budget / (price + unit_cost)))
        cost = charges.cnc(price * qty, 0., dp_charged=False)
        cash -= qty * price + cost
        holdings[symbol] = dict(qty=qty, entry_price=price, entry_costs=cost)
    values = [float(capital)]
    for day in dates[1:]:
        values.append(cash + sum(h['qty'] * float(frames[s].loc[day, 'close'])
                                 for s, h in holdings.items()))
    return pd.Series(values, index=dates, name='buy_hold_equity'), holdings


def _clean(value):
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value


def _write_json(path, payload):
    with path.open('x', encoding='utf-8') as fh:
        json.dump(_clean(payload), fh, indent=2, allow_nan=False, default=str)


def run(manifest_path, out_root, capital=33_333.33):
    if not np.isfinite(capital) or capital <= 0:
        raise ValueError('capital must be finite and positive')
    universe, index, source = load_dataset(manifest_path)
    parent = Path(out_root)
    parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='offline-backtest-', dir=parent))
    cfg = BotConfig()
    historical_execution = source['execution_model'] == 'dated_nse_cash_v1'
    # Fix the scenarios before computing any returns. Never select a winner.
    spec = dict(strategy='existing swing reversion; no parameter search',
                config=cfg.to_dict(), capital=capital, warmup=200,
                slippage_scenarios_bps=[5., 10., 25.],
                charges=asdict(DEFAULT_CHARGES),
                cost_basis='Static research assumptions, not a dated historical fee schedule',
                close_exits='next available open', protective_stops='gap-aware plus adverse slippage',
                universe='Fixed supplied engineering sample, not a point-in-time index universe',
                benchmark='Equal-budget same stocks, buy at second evaluated open; integer shares/costs',
                reference='Nifty gross price index; not an investable cost-adjusted benchmark',
                terminal='Mark all open positions; no invented terminal fill; dividends excluded',
                acceptance='Accounting/causality/data gates; no guaranteed return threshold',
                source=source)
    if historical_execution:
        from .historical_execution import historical_execution_spec
        spec['charges'] = historical_execution_spec()
        spec['cost_basis'] = 'Dated exchange plus IPFT; conservative fixed DP; CNC taxation assumption'
    try:
        spec['source_commit'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=Path(__file__).resolve().parents[2],
            text=True, encoding='utf-8', stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        spec['source_commit'] = 'unavailable'
    # Dirty source identity matters: the commit alone may omit local repairs.
    base = Path(__file__).resolve().parents[1]
    spec['implementation_sha256'] = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(base.rglob('*.py'))}
    spec['versions'] = dict(python=sys.version, pandas=pd.__version__, numpy=np.__version__)
    _write_json(out / 'frozen_spec.json', spec)
    outcomes = []
    for slip in spec['slippage_scenarios_bps']:
        case = out / f'slippage-{slip:g}bps'
        case.mkdir()
        md, equity, trades = report(universe, index, cfg, initial_cash=capital,
                                     workdir=case / 'engine', slippage_bps=slip,
                                     historical_execution=historical_execution)
        ledger = Ledger(case / 'engine', 'swing', capital)
        journal = ledger.equity_history()
        if ledger.cash < -.01 or (journal['cash'].astype(float) < -.01).any():
            raise ValueError('ACCOUNTING: unlevered swing replay cannot borrow cash')
        closes = {s: float(f['close'].iloc[-1]) for s, f in universe.items()}
        mark = ledger.cash + sum(p.qty * closes[p.symbol] for p in ledger.positions)
        if abs(mark - float(equity.iloc[-1])) > .02:
            raise ValueError('ACCOUNTING: cash plus final position marks does not reconcile')
        unrealized_net = sum((closes[p.symbol] - p.entry_price) * p.qty
                             - float(p.meta.get('entry_costs', 0.)) for p in ledger.positions)
        realized = float(trades['net_pnl'].sum()) if len(trades) else 0.
        if abs(mark - capital - realized - unrealized_net) > .02 + .01 * len(trades):
            raise ValueError('ACCOUNTING: net P&L does not reconcile with equity')
        hold, holdings = buy_and_hold(universe, equity.index, capital, slip,
                                     historical_execution=historical_execution)
        if source['data_kind'] == 'synthetic':
            md = 'SYNTHETIC ENGINEERING CHECK ONLY - NOT MARKET PERFORMANCE\n\n' + md
        (case / 'BACKTEST.md').write_text(md + '\n', encoding='utf-8')
        equity.to_csv(case / 'equity.csv', encoding='utf-8', mode='x')
        trades.to_csv(case / 'trades.csv', index=False, encoding='utf-8', mode='x')
        hold.to_csv(case / 'buy_hold.csv', encoding='utf-8', mode='x')
        outcomes.append(dict(slippage_bps=slip, strategy=_curve(equity),
                             same_stocks_buy_hold=_curve(hold),
                             average_invested_fraction=float((journal['open_value'].astype(float)
                                                             / journal['equity'].astype(float)).mean()),
                             sessions_in_market_fraction=float((journal['open_positions'] > 0).mean()),
                             final_equity=float(equity.iloc[-1]),
                             net_pnl=float(equity.iloc[-1]) - capital,
                             closed_trades=len(trades), closed_trade_costs=float(trades['costs'].sum()),
                             win_rate=float((trades['net_pnl'] > 0).mean()) if len(trades) else None,
                             paid_costs=float(trades['costs'].sum())
                             + sum(float(p.meta.get('entry_costs', 0.)) for p in ledger.positions),
                             benchmark_buy_costs=sum(h['entry_costs'] for h in holdings.values()),
                             open_positions=len(ledger.positions), pending_entries=len(ledger.state['pending']),
                             queued_exits=sum('close_exit' in p.meta for p in ledger.positions),
                             accounting='PASS', benchmark_holdings=holdings,
                             evidence='SYNTHETIC_ONLY' if source['data_kind'] == 'synthetic'
                             else ('NO_CLOSED_TRADES_INCONCLUSIVE' if trades.empty else 'DESCRIPTIVE_ONLY')))
    result = dict(data_kind=source['data_kind'], status='TECHNICAL_CHECKS_PASS',
                  network_requests=0, scenarios=outcomes,
                  input_sessions=source['input_sessions'], warmup_sessions=source['warmup_sessions'],
                  evaluation_sessions=source['evaluation_sessions'], symbols=source['symbols'],
                  evaluation_start=str(equity.index[0].date()), evaluation_end=str(equity.index[-1].date()),
                  nifty_gross_price_reference=_curve(index.set_index('datetime')['close'].reindex(equity.index)),
                  limitations=['Not proof of profitability or source permissions.',
                               ('Dated exchange/IPFT, assumed DP15.93 and held-delivery taxation; no exact historical tax invoice.'
                                if historical_execution else 'Static costs, not dated historical fees.'),
                               'No dividends, band/auction/fill guarantees; daily bars omit intraday order resets.',
                               'Same-close legacy runtime convention remains separate.',
                               'No independent market-data rights/calendar/corporate-action certification.'])
    _write_json(out / 'summary.json', result)
    return out, result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--out', type=Path, default=Path('E:/AI-Trading-Data/results/nsebot'))
    args = parser.parse_args(argv)
    out, result = run(args.manifest, args.out)
    print(f"{result['status']} ({result['data_kind']}): {out / 'summary.json'}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
