"""Offline, raw-share, interval-stress replay; never certifies missing raw OHLC.

Adjusted OHLC are rounded provider observations. Reconstruct conservative price
intervals from raw closes assuming uniform adjustment and nearest-cent rounding.
This is a disclosed stress assumption, NOT independently observed raw OHLC.
Any position/pending order crossing a capital event stops the replay. Terminal
buy-and-hold quantities include bonuses/spin-offs; no invented child daily curve.
"""
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd

from ..backtest import _curve, validate_history
from ..config import BotConfig
from ..engine.market_view import DailyMarket
from ..engine.swing import SwingEngine
from ..ledger import Ledger
from ..market import round_to_tick
from ..signals import ReversionSignalEngine
from .historical_execution import DatedPaperBroker, HistoricalTickTable, historical_charges, historical_execution_spec
from .offline_backtest import _clean


def raw_intervals(adjusted, raw_close):
    """Do not assert an exact raw open from a rounded adjusted bar/close ratio.

    For rounding epsilon .005, raw_close/(adjusted_close +/- epsilon) bounds
    the raw/adjusted multiplier. Buy at the upper open; exits/gaps use the
    lower open; stop tests use the lower low and trailing uses the lower high.
    True close remains the observed raw close. Exact unchanged-unit bars remain
    untouched. These intervals depend on the explicit uniform-adjustment model.
    """
    f = adjusted.copy()
    raw = np.asarray(raw_close, dtype=float)
    c = f['close'].to_numpy(dtype=float)
    prices = f[['open', 'high', 'low', 'close']].to_numpy(dtype=float)
    if (len(raw) != len(f) or not np.isfinite(raw).all() or (raw <= 0).any()
            or not np.isfinite(prices).all() or (prices <= .005).any()):
        raise ValueError('RAW SCALE: complete positive raw closes required')
    unchanged = raw == c
    lo, hi = raw / (c + .005), raw / (c - .005)
    for name in ('open', 'high', 'low'):
        values = f[name].to_numpy(dtype=float)
        lower, upper = (values - .005) * lo, (values + .005) * hi
        f[name] = np.where(unchanged, values, lower)
        if name == 'open':
            f['raw_open_upper'] = np.where(unchanged, values, upper)
    f['close'] = raw
    f['high'] = np.maximum.reduce([f['high'].to_numpy(), f['open'].to_numpy(), raw])
    f['low'] = np.minimum.reduce([f['low'].to_numpy(), f['open'].to_numpy(), raw])
    f['price_scale'] = raw / c
    return f


class RawShareMarket(DailyMarket):
    """Continuous adjusted indicators translated to each decision's raw units.

    Absolute price and turnover gates use raw prices/volumes. Full-history
    adjustment factors must not create artificial split/de-merger dip signals.
    Prefix equality must be checked using the same preserved vendor snapshot;
    it does not establish historical vendor revision availability.
    """
    def __init__(self, universe, index, raw_frames, cfg):
        super().__init__(universe, index, ReversionSignalEngine(cfg.reversion))
        for symbol, adjusted in universe.items():
            raw = raw_frames[symbol]
            if not pd.DatetimeIndex(raw['datetime']).equals(pd.DatetimeIndex(adjusted['datetime'])):
                raise ValueError('RAW SCALE: dates must match the reviewed calendar exactly')
            execution = raw_intervals(adjusted, raw['raw_close'])
            f = self.feats[symbol]
            scale = execution['price_scale'].to_numpy()
            for column in ('ema_trend', 'ema_exit', 'atr', 'stop'):
                f[column] *= scale
            for column in ('open', 'high', 'low', 'close', 'raw_open_upper'):
                f[column] = execution[column].to_numpy()
            f['turnover'] = (f['close'] * f['volume']).rolling(20, min_periods=20).median()
            c = cfg.reversion
            f['liquid'] = ((np.arange(len(f)) >= c.min_bars - 1) & (f['close'] >= c.min_price)
                           & (f['turnover'] >= c.min_turnover_inr))
            f['signal'] = f['liquid'] & f['uptrend'] & (f['drop'] <= -c.drop_pct)


class IntervalPaperBroker(DatedPaperBroker):
    def resolve_entry(self, pending, bar):
        if pending['spec']['side'] != 'LONG':
            raise ValueError('INTERVAL REPLAY: only unlevered long research is supported')
        if bar is None or float(bar['open']) <= pending['spec']['stop']:
            return super().resolve_entry(pending, bar)
        worst = dict(bar)
        worst['open'] = float(bar['raw_open_upper'])
        return super().resolve_entry(pending, worst)


def guard_capital_event(ledger, event, day):
    """No silently incorrect holdings across an unsupported capital event."""
    if pd.Timestamp(event['ex_date']) != pd.Timestamp(day):
        return None
    parent = event['parent']
    positions = [p for p in ledger.positions if p.symbol == parent]
    pending = [p for p in ledger.state['pending'] if p['spec']['symbol'] == parent]
    if positions or pending:
        raise ValueError(f'CORPORATE EVENT: {parent}: held/pending exposure requires a full entitlement ledger')
    return dict(parent=parent, ex_date=str(pd.Timestamp(day).date()), positions=0, pending=0, status='PASS_NO_EXPOSURE')


def terminal_holdings(holdings, events, bought_on, end):
    """Non-trading buy-and-hold quantity ledger. Event ordering is essential:
    a later parent bonus must not multiply an earlier spin-off entitlement.
    No income, raw prices, tax cost allocations or tradability are invented.
    """
    quantities = {s: int(h['qty']) for s, h in holdings.items()}
    if any(h['qty'] != quantities[s] or quantities[s] < 0 for s, h in holdings.items()):
        raise ValueError('CORPORATE EVENT: whole nonnegative initial shares required')
    audit = []
    for event in sorted(events, key=lambda e: e['ex_date']):
        if not pd.Timestamp(bought_on) < pd.Timestamp(event['ex_date']) <= pd.Timestamp(end):
            continue  # Buying on ex-date gives no entitlement.
        qty = quantities.get(event['parent'], 0)
        numerator, denominator = event['numerator'], event['denominator']
        if (type(numerator) is not int or type(denominator) is not int or numerator <= 0 or denominator <= 0):
            raise ValueError('CORPORATE EVENT: positive integer entitlement ratio required')
        new = qty * numerator / denominator
        if not float(new).is_integer():
            raise ValueError('CORPORATE EVENT: fractional entitlement requires reviewed cash-in-lieu')
        if event['type'] == 'bonus':
            quantities[event['parent']] = qty + int(new)
        elif event['type'] == 'demerger':
            child = event['child']
            quantities[child] = quantities.get(child, 0) + int(new)
        else:
            raise ValueError('CORPORATE EVENT: unsupported event type')
        audit.append(dict(event=event, entitled_parent_qty=qty, added_qty=int(new)))
    return quantities, audit


def terminal_buy_hold(raw_frames, adjusted, dates, capital, slip, events, terminal_marks):
    """Endpoint wealth only: absent child daily prices block risk-curve metrics."""
    ticks = HistoricalTickTable({s: f.rename(columns={'raw_close': 'close'})
                                 for s, f in raw_frames.items()}).set_session(dates[1])
    charges = historical_charges(dates[1])
    cash, holdings = float(capital), {}
    for symbol in sorted(adjusted):
        bounds = raw_intervals(adjusted[symbol], raw_frames[symbol]['raw_close']).set_index('datetime')
        opening = float(bounds.loc[dates[1], 'raw_open_upper'])
        price = round_to_tick(opening * (1 + slip / 1e4), ticks.tick(symbol, opening), 'up')
        qty = int((capital / len(adjusted)) // (price + charges.cnc(price, 0., False)))
        fee = charges.cnc(price * qty, 0., False)
        cash -= qty * price + fee
        holdings[symbol] = dict(qty=qty, entry_price=price, entry_costs=fee)
    quantities, audit = terminal_holdings(holdings, events, dates[1], dates[-1])
    wealth = cash
    for symbol, qty in quantities.items():
        mark = terminal_marks.get(symbol)
        if mark is None or not np.isfinite(mark) or mark <= 0:
            raise ValueError('BENCHMARK: official terminal mark missing/invalid')
        wealth += qty * mark
    if cash < -.001:
        raise ValueError('BENCHMARK: cannot borrow cash')
    return dict(final_equity=wealth, ret=wealth / capital - 1, cash=cash,
                initial_holdings=holdings, terminal_quantities=quantities, events=audit,
                daily_curve=None, maxdd=None, sharpe=None,
                basis='Endpoint raw-share wealth, including spin-offs; excludes dividends and liquidation costs')


def run(universe, index, raw_frames, events, terminal_marks, out_root, provenance):
    validate_history(universe, index)
    if len(index) < 452 or set(universe) != set(raw_frames):
        raise ValueError('CORPORATE REPLAY: need complete reviewed daily/raw pilot history')
    cfg, capital = BotConfig(), 33_333.33
    # Validate all data before producing any simulated orders/state.
    market = RawShareMarket(universe, index, raw_frames, cfg)
    raw_universe = {s: f[['datetime', 'raw_close']].rename(columns={'raw_close': 'close'})
                    for s, f in raw_frames.items()}
    parent = Path(out_root)
    out = Path(tempfile.mkdtemp(prefix='five-stock-interval-', dir=parent))
    spec = dict(kind='RAW_SHARE_INTERVAL_STRESS_NOT_EXACT_RAW_OHLC', strategy='unchanged BotConfig reversion',
                config=cfg.to_dict(), capital=capital, slippage_bps=[5., 10., 25.],
                execution=historical_execution_spec(), events=events, provenance=provenance,
                assumptions=['Uniform per-bar adjustment; nearest-cent adjusted-OHLC rounding.',
                             'Worst-case open/low/high bounds, not observed raw OHLC.',
                             'Held/pending exposure at capital events fails closed.',
                             'No child daily prices: benchmark endpoint wealth only.',
                             'No dividends, broker transport, tax cost-basis claims or live readiness.'])
    base = Path(__file__).resolve().parents[1]
    spec['implementation_sha256'] = {str(p.relative_to(base)): hashlib.sha256(p.read_bytes()).hexdigest()
                                     for p in sorted(base.rglob('*.py'))}
    (out / 'frozen_spec.json').write_text(json.dumps(spec, indent=2, default=str), encoding='utf-8')
    results = []
    for slip in spec['slippage_bps']:
        case = out / f'{slip:g}bps'
        case.mkdir()
        broker = IntervalPaperBroker(raw_universe, slippage_bps=slip)
        ledger = Ledger(case / 'engine', 'swing', capital)
        engine = SwingEngine(cfg, broker, ledger, workdir=case / 'engine', log=lambda _: None,
                             defer_close_exits=True)
        checked, trace = [], []
        for day in market.dates[200:]:
            for event in events:
                result = guard_capital_event(ledger, event, day)
                if result:
                    checked.append(result)
            broker.set_session(day)
            report = engine.run(market, day)
            trace.append(dict(day=str(day.date()), signals=report.get('signals', 0),
                              placed=len(report['placed']), filled=len(report['filled']),
                              declined=report['declined'], closed=len(report['closed'])))
        journal, trades = ledger.equity_history(), ledger.closed_trades()
        equity = pd.Series(journal['equity'].to_numpy(dtype=float), index=pd.to_datetime(journal['session']))
        mark = ledger.cash + sum(p.qty * market.last_close(p.symbol, market.dates[-1]) for p in ledger.positions)
        unrealized = sum((market.last_close(p.symbol, market.dates[-1]) - p.entry_price) * p.qty
                         - p.meta.get('entry_costs', 0.) for p in ledger.positions)
        realized = float(trades['net_pnl'].sum()) if len(trades) else 0.
        if ((journal['cash'] < -.01).any() or abs(mark - equity.iloc[-1]) > .02
                or abs(mark - capital - realized - unrealized) > .02 + .01 * len(trades)):
            raise ValueError('ACCOUNTING: raw-share replay does not reconcile')
        hold = terminal_buy_hold(raw_frames, universe, equity.index, capital, slip, events, terminal_marks)
        equity.to_csv(case / 'equity.csv', encoding='utf-8', mode='x')
        trades.to_csv(case / 'trades.csv', index=False, encoding='utf-8', mode='x')
        (case / 'trace.json').write_text(json.dumps(trace, indent=2, default=str), encoding='utf-8')
        results.append(dict(slippage_bps=slip, strategy=_curve(equity), final_equity=float(equity.iloc[-1]),
                            net_pnl=float(equity.iloc[-1]) - capital, closed_trades=len(trades),
                            open_positions=len(ledger.positions), pending_entries=len(ledger.state['pending']),
                            paid_closed_costs=float(trades['costs'].sum()),
                            event_exposure_checks=checked, benchmark=hold, accounting='PASS'))
    summary = dict(status='INTERVAL_STRESS_COMPLETED_NOT_STRICT_SOURCE_CERTIFIED', scenarios=results,
                   evaluation_start=str(equity.index[0].date()), evaluation_end=str(equity.index[-1].date()),
                   evaluation_sessions=len(equity), symbols=list(universe), network_requests=0,
                   strict_raw_ohlc_backtest_ready=False, child_daily_benchmark_ready=False)
    summary = _clean(summary)
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    return out, summary
