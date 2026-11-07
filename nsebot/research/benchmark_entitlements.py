"""Passive buy-and-hold wealth with explicit unlisted receivables, not fake bars."""
import numpy as np
import pandas as pd

from ..backtest import _curve
from ..market import round_to_tick
from .corporate_replay import terminal_holdings
from .historical_execution import HistoricalTickTable, historical_charges
from .offline_backtest import _clean


def initial_buys(raw_frames, dates, capital, slip, official_opens):
    """The five official entry opens replace interval estimates for benchmark buys."""
    if not np.isfinite(capital) or capital<=0 or not 0<=slip<10000:
        raise ValueError('BENCHMARK: invalid capital/slippage')
    ticks=HistoricalTickTable({s:f[['datetime','raw_close']].rename(columns={'raw_close':'close'})
                               for s,f in raw_frames.items()}).set_session(dates[1])
    charges=historical_charges(dates[1]);cash=float(capital);holdings={}
    if set(official_opens)!=set(raw_frames):
        raise ValueError('BENCHMARK: every initial raw open must be independently supplied')
    for symbol in sorted(raw_frames):
        opening=float(official_opens[symbol])
        if not np.isfinite(opening) or opening<=0:raise ValueError('BENCHMARK: invalid official open')
        price=round_to_tick(opening*(1+slip/10000),ticks.tick(symbol,opening),'up')
        qty=int((capital/len(raw_frames))//(price+charges.cnc(price,0.,False)))
        costs=charges.cnc(price*qty,0.,False)
        cash-=qty*price+costs
        holdings[symbol]=dict(qty=qty,entry_price=price,entry_costs=costs)
    if cash<-.001:raise ValueError('BENCHMARK: cannot borrow cash')
    return cash,holdings


def wealth_curve(holdings,cash,parent_closes,child_closes,events,dates,indicative_marks,capital):
    """Never fill missing listed prices. Before listing, the investor holds an
    unlisted entitlement receivable: model it at an explicitly supplied indicative
    event value, never cash or a tradable stock quote. A separate quoted-only
    equity series stays missing whenever such an unlisted receivable exists.
    """
    dates=pd.DatetimeIndex(dates)
    rows=[]
    for i,day in enumerate(dates):
        if i==0:
            rows.append(dict(datetime=day,marked_equity=float(capital),quoted_equity=float(capital),
                             indicative_receivable_value=0.,unlisted_symbols=''))
            continue
        quantities,_=terminal_holdings(holdings,events,dates[1],day)
        total=float(cash);receivables=0.;unlisted=[]
        for symbol,qty in quantities.items():
            if qty==0:continue
            if symbol in parent_closes:
                series=parent_closes[symbol]
                if day not in series.index:raise ValueError('BENCHMARK: missing parent traded close')
                value=float(series.loc[day])
            else:
                if symbol not in child_closes or child_closes[symbol].empty:
                    raise ValueError('BENCHMARK: missing child listed history')
                series=child_closes[symbol]
                if day<series.index[0]:
                    value=float(indicative_marks[symbol])
                    receivables+=qty*value;unlisted.append(symbol)
                elif day not in series.index:
                    raise ValueError('BENCHMARK: missing listed child price; no forward fill')
                else:value=float(series.loc[day])
            if not np.isfinite(value) or value<=0:raise ValueError('BENCHMARK: invalid valuation')
            total+=qty*value
        rows.append(dict(datetime=day,marked_equity=total,
                         quoted_equity=np.nan if unlisted else total,
                         indicative_receivable_value=receivables,unlisted_symbols=','.join(sorted(unlisted))))
    frame=pd.DataFrame(rows).set_index('datetime')
    missing=frame['quoted_equity'].isna()
    start=int(np.flatnonzero(missing.to_numpy())[-1]+1) if missing.any() else 0
    fully_quoted=frame['quoted_equity'].iloc[start:]
    quantities,audit=terminal_holdings(holdings,events,dates[1],dates[-1])
    result=dict(final_equity=float(frame['marked_equity'].iloc[-1]),
                ret=float(frame['marked_equity'].iloc[-1])/capital-1,
                terminal_quantities=quantities,events=audit,
                indicative_valuation_sessions=int(missing.sum()),
                full_period_marked_model_risk=_curve(frame['marked_equity']),
                full_period_observed_benchmark_risk=None,
                fully_quoted_final_segment=dict(start=str(fully_quoted.index[0].date()) if len(fully_quoted) else None,
                    sessions=len(fully_quoted),risk=_curve(fully_quoted)),
                valuation_basis='Unlisted receivables use declared fixed discovery marks, not tradable quotes; listed days require actual raw closes',
                dividends=False,terminal_liquidation=False)
    return frame,_clean(result)
