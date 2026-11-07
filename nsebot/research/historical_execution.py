"""Offline cash-equity execution context; no broker connection or downloads.

The dated exchange/IPFT schedule is reviewed, but the fixed DP charge is a
conservative research assumption. Delivery STT/stamp/DP are charged even for
same-session round trips; settlement netting, income taxes and personal broker
tariffs are not modelled. Tick anchors must be historical *raw* closes, or the
caller must explicitly transform these raw ticks into its execution units.
"""
from dataclasses import replace
import math

import pandas as pd

from ..broker.paper import PaperBroker
from ..costs import DEFAULT_CHARGES


SUPPORTED_START = pd.Timestamp('2021-11-08')
SUPPORTED_END = pd.Timestamp('2026-11-06')
# Effective date, exchange INR/crore, IPFT INR/crore, each side.
FEE_SCHEDULE = (
    ('2021-11-08', 345.0, .01),
    ('2023-04-01', 325.0, 10.0),
    ('2024-04-01', 322.0, 10.0),
    ('2024-10-01', 297.0, 10.0),
    ('2026-03-01', 306.99, .01),
)
DP_ASSUMPTION_INR = 15.93  # Fixed stress assumption, already including GST.


def _day(value):
    try:
        day = pd.Timestamp(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError('HISTORICAL EXECUTION: invalid session date') from None
    if (pd.isna(day) or day.tzinfo is not None or day != day.normalize()
            or not SUPPORTED_START <= day <= SUPPORTED_END):
        raise ValueError('HISTORICAL EXECUTION: require a naive session date within reviewed bounds')
    return day


def _positive(value, label):
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError(f'HISTORICAL EXECUTION: invalid {label}') from None
    if isinstance(value, bool) or not math.isfinite(number) or number <= 0:
        raise ValueError(f'HISTORICAL EXECUTION: require finite positive {label}')
    return number


def historical_charges(day):
    """Dated exchange+IPFT, delivery taxes, and a fixed DP stress assumption.

    Combine IPFT with exchange charges so both receive GST in the existing
    itemised arithmetic. This changes research instances only, never defaults.
    """
    day = _day(day)
    row = next(row for row in reversed(FEE_SCHEDULE) if pd.Timestamp(row[0]) <= day)
    return replace(DEFAULT_CHARGES, exchange_pct=(row[1] + row[2]) / 10_000_000.,
                   dp_charge_inr=DP_ASSUMPTION_INR)


def historical_execution_spec():
    """Fresh JSON-compatible copy, suitable for freezing before a replay."""
    return dict(
        supported_dates=[str(SUPPORTED_START.date()), str(SUPPORTED_END.date())],
        exchange_ipft_inr_per_crore=[dict(effective=d, exchange=e, ipft=i)
                                    for d, e, i in FEE_SCHEDULE],
        dp_inr_including_gst=DP_ASSUMPTION_INR,
        dp_basis='Fixed conservative assumption; not a verified historical DP tariff',
        delivery_basis='CNC STT/stamp/DP even for same-day exits; may overcharge netted trades',
        taxes='Delivery STT 0.1% each leg; buy stamp 0.015%; SEBI 10/crore; GST 18%',
        excluded='Income/capital-gains tax, personal tariffs and settlement-netting differences',
        ticks='Historical raw prior-month close; special first April2025 anchor 2025-03-28',
        sources=[
            'https://archives.nseindia.com/content/circulars/FA56129.pdf',
            'https://zerodha.com/marketintel/bulletin/373933/revision-in-nse-transaction-charges-from-april-1-2024',
            'https://nsearchives.nseindia.com/content/circulars/FA64232.pdf',
            'https://nsearchives.nseindia.com/content/circulars/FA73061.pdf',
            'https://nsearchives.nseindia.com/content/circulars/CMTR62174.pdf',
            'https://nsearchives.nseindia.com/content/circulars/CMTR67133.pdf',
            'https://zerodha.com/charges/',
        ])


class HistoricalTickTable:
    """Monthly tick context from validated, ordered historical raw close rows.

    The importer separately validates the exchange calendar. A supplied month
    must contain its reviewed last session; this table cannot certify missing
    sessions merely by selecting the latest supplied row.
    """

    def __init__(self, universe):
        if not isinstance(universe, dict) or not universe:
            raise ValueError('HISTORICAL EXECUTION: raw equity universe is required')
        self._closes = {}
        for symbol, frame in universe.items():
            if (not isinstance(symbol, str) or not symbol or frame is None
                    or not {'datetime', 'close'}.issubset(frame.columns) or frame.empty):
                raise ValueError('HISTORICAL EXECUTION: invalid raw close history')
            dates = pd.DatetimeIndex(pd.to_datetime(frame['datetime'], errors='coerce'))
            closes = pd.to_numeric(frame['close'], errors='coerce').to_numpy(dtype=float)
            if (dates.isna().any() or dates.tz is not None or not dates.is_unique
                    or not dates.is_monotonic_increasing
                    or not dates.equals(dates.normalize())
                    or any(not math.isfinite(p) or p <= 0 for p in closes)):
                raise ValueError('HISTORICAL EXECUTION: invalid raw close dates or values')
            self._closes[symbol] = pd.Series(closes, index=dates)
        self.session = None
        self._ticks = {}

    def set_session(self, day):
        self.session, self._ticks = None, {}
        day = _day(day)
        ticks = {}
        for symbol, closes in self._closes.items():
            if day < pd.Timestamp('2024-06-10'):
                ticks[symbol] = .05
                continue
            month_start = day.replace(day=1)
            previous_start = month_start - pd.DateOffset(months=1)
            anchors = closes.loc[(closes.index >= previous_start) & (closes.index < month_start)]
            if pd.Timestamp('2025-04-15') <= day < pd.Timestamp('2025-05-01'):
                anchor = pd.Timestamp('2025-03-28')
                if anchor not in anchors.index:
                    raise ValueError('HISTORICAL EXECUTION: missing 2025-03-28 tick anchor')
                price = float(anchors.loc[anchor])
            elif anchors.empty:
                raise ValueError(f'HISTORICAL EXECUTION: missing previous-month tick anchor for {symbol}')
            else:
                price = float(anchors.iloc[-1])
            if day < pd.Timestamp('2025-04-15'):
                tick = .01 if price < 250. else .05
            elif price < 250.:
                tick = .01
            else:
                tick = next(t for upper, t in ((1000., .05), (5000., .10), (10000., .50),
                                               (20000., 1.), (math.inf, 5.)) if price <= upper)
            ticks[symbol] = tick
        self.session, self._ticks = day, ticks
        return self

    def tick(self, symbol, price):
        _positive(price, 'execution price')
        if self.session is None or symbol not in self._ticks:
            raise ValueError('HISTORICAL EXECUTION: missing session or symbol tick context')
        return self._ticks[symbol]

    def lot(self, symbol):
        if symbol not in self._closes:
            raise ValueError('HISTORICAL EXECUTION: unknown equity symbol')
        return 1


class DatedPaperBroker(PaperBroker):
    """Paper-only CNC research fills with actual-fill dated fee/tick context."""

    def __init__(self, universe, slippage_bps=5., stop_slippage_bps=None):
        ticks = HistoricalTickTable(universe)
        super().__init__(slippage_bps=slippage_bps,
                         stop_slippage_bps=slippage_bps if stop_slippage_bps is None else stop_slippage_bps,
                         charges=historical_charges(SUPPORTED_START), ticks=ticks)
        self.session = None

    def set_session(self, day):
        self.session = None
        day = _day(day)
        self.ticks.set_session(day)
        self.charges = historical_charges(day)
        self.session = day
        return self

    def resolve_entry(self, pending, bar):
        if bar is not None:
            spec = pending['spec']
            if spec.get('product') != 'CNC' or spec.get('side') not in ('LONG', 'SHORT'):
                raise ValueError('HISTORICAL EXECUTION: only CNC equity research is supported')
            qty = _positive(spec.get('qty'), 'quantity')
            if not qty.is_integer():
                raise ValueError('HISTORICAL EXECUTION: whole equity shares are required')
            _positive(spec.get('stop'), 'stop')
            _positive(bar.get('open'), 'entry open')
            self.set_session(bar.get('datetime'))
        return super().resolve_entry(pending, bar)

    def exit(self, position, price, reason, when):
        if position.mode != 'swing' or position.side not in ('LONG', 'SHORT'):
            raise ValueError('HISTORICAL EXECUTION: only swing equity research exits are supported')
        _positive(price, 'exit price')
        qty = _positive(position.qty, 'quantity')
        if not qty.is_integer():
            raise ValueError('HISTORICAL EXECUTION: whole equity shares are required')
        self.set_session(when)
        return super().exit(position, price, reason, when)

    def _leg_cost(self, product, value, leg, dp):
        if self.session is None or product != 'CNC':
            raise ValueError('HISTORICAL EXECUTION: dated CNC fee context is required')
        return super()._leg_cost(product, value, leg, dp)
