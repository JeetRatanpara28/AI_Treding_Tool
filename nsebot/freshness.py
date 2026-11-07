"""Fail closed on stale daily paper-run inputs; historical replays are unaffected.

Use the reviewed offline exchange calendar, including special sessions.
Missing/expired coverage never falls back to weekdays. No network or portfolio
writes occur here.
"""

import numpy as np
import pandas as pd

from . import market
from .session_calendar import CalendarError, load_calendar


class DataFreshnessError(ValueError):
    pass


def expected_daily_session(now=None):
    now = pd.Timestamp(now) if now is not None else market.now_ist()
    now = now.tz_localize(market.IST) if now.tzinfo is None else now.tz_convert(market.IST)
    try:
        return pd.Timestamp(load_calendar().expected_session(now.to_pydatetime()))
    except CalendarError as exc:
        raise DataFreshnessError(f'SESSION CALENDAR: {exc}') from exc


def require_daily_session(frame, session, label, is_index=False):
    """Require one complete OHLCV bar on session, even after sanitization."""
    expected = pd.Timestamp(session).normalize()
    prefix = f'{label}: expected complete daily bar for {expected.date()}'
    fields = ['open', 'high', 'low', 'close', 'volume']
    if frame is None or frame.empty or not {'datetime', *fields}.issubset(frame.columns):
        raise DataFreshnessError(f'{prefix}; data missing or columns incomplete')
    dates = pd.DatetimeIndex(pd.to_datetime(frame['datetime'], errors='coerce'))
    if dates.tz is not None:
        dates = dates.tz_convert(market.IST).tz_localize(None)
    dates = dates.normalize()
    if dates.isna().any() or not dates.is_monotonic_increasing:
        raise DataFreshnessError(f'{prefix}; invalid or unsorted dates')
    rows = frame.loc[dates == expected, fields]
    if len(rows) != 1:
        latest = dates[dates <= expected]
        last = str(latest.max().date()) if len(latest) else 'none'
        raise DataFreshnessError(f'{prefix}; found {len(rows)} bars, latest available {last}')
    values = pd.to_numeric(rows.iloc[0], errors='coerce').to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise DataFreshnessError(f'{prefix}; missing or non-finite OHLCV values')
    open_, high, low, close, volume = values
    if min(open_, high, low, close) <= 0 or high < max(open_, low, close) or low > min(open_, high, close):
        raise DataFreshnessError(f'{prefix}; invalid OHLC prices')
    if volume < 0 or (not is_index and volume == 0):
        raise DataFreshnessError(f'{prefix}; invalid volume')


def require_intraday_bar(frame, now, label, interval_minutes=5, is_index=False):
    """Require the latest finished interval; never accept an older tick or a forming bar."""
    now = pd.Timestamp(now)
    now = now.tz_localize(market.IST) if now.tzinfo is None else now.tz_convert(market.IST)
    expected = now.floor(f'{interval_minutes}min') - pd.Timedelta(minutes=interval_minutes)
    if expected.date() != now.date() or expected.time() < market.SESSION_OPEN:
        raise DataFreshnessError(f'{label}: no completed intraday interval yet')
    if frame is None or frame.empty or 'datetime' not in frame:
        raise DataFreshnessError(f'{label}: missing intraday data for {expected}')
    dates = pd.DatetimeIndex(pd.to_datetime(frame['datetime'], errors='coerce'))
    dates = dates.tz_localize(market.IST) if dates.tz is None else dates.tz_convert(market.IST)
    if dates.isna().any() or not dates.is_monotonic_increasing:
        raise DataFreshnessError(f'{label}: invalid intraday dates')
    rows = frame.loc[dates == expected].copy()
    if len(rows) != 1:
        raise DataFreshnessError(f'{label}: expected one complete intraday bar at {expected}; found {len(rows)}')
    rows['datetime'] = pd.Timestamp(expected.date())
    require_daily_session(rows, pd.Timestamp(expected.date()), label, is_index=is_index)
