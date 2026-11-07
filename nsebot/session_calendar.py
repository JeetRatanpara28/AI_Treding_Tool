"""Reviewed offline NSE cash-equity session calendar. Standard library only."""

from datetime import date, datetime, time, timedelta, timezone
import json
import os
from pathlib import Path
import re
from urllib.parse import urlparse

IST = timezone(timedelta(hours=5, minutes=30))
DEFAULT_CALENDAR = Path(__file__).parent / 'calendars' / 'nse_cash_2026.json'


class CalendarError(ValueError):
    """Unverified, invalid, expired, or uncovered session information."""


def _day(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise CalendarError('calendar dates must use YYYY-MM-DD')
    return date.fromisoformat(value)


def _hours(record):
    fields = ('open', 'normal_close', 'post_close_end', 'ready_after')
    values = []
    for key in fields:
        value = record[key]
        if not isinstance(value, str) or not re.fullmatch(r'\d{2}:\d{2}', value):
            raise CalendarError('calendar times must use HH:MM')
        values.append(time.fromisoformat(value))
    if not values[0] < values[1] <= values[2] < values[3]:
        raise CalendarError('invalid session hours or data-finalization buffer')
    return dict(zip(fields, values))


class SessionCalendar:
    def __init__(self, data):
        try:
            if (data['schema_version'], data['exchange'], data['segment'], data['timezone']) != (
                    1, 'NSE', 'cash_equities', 'Asia/Kolkata'):
                raise CalendarError('unsupported calendar schema, market, or timezone')
            self.start, self.end = _day(data['coverage_start']), _day(data['coverage_end'])
            self.reviewed = _day(data['reviewed_on'])
            self.expires = _day(data['review_expires'])
            if not self.start <= self.reviewed <= self.expires <= self.end:
                raise CalendarError('invalid coverage or review dates')
            if (self.end - self.start).days > 366:
                raise CalendarError('calendar coverage must be bounded to one year')
            sources = data['sources']
            if not sources:
                raise CalendarError('calendar source provenance is required')
            for source in sources.values():
                parsed = urlparse(source['url'])
                if parsed.scheme != 'https' or parsed.hostname not in {
                        'www.nseindia.com', 'nseindia.com', 'nsearchives.nseindia.com'}:
                    raise CalendarError('calendar sources must be official NSE HTTPS URLs')
                if parsed.username or parsed.password:
                    raise CalendarError('calendar sources must not contain credentials')
                if 'sha256' in source and not re.fullmatch(r'[a-f0-9]{64}', source['sha256']):
                    raise CalendarError('invalid source hash')
            self.normal = _hours(data['normal_session'])
            self.closed = set()
            for item in data['holidays']:
                day = _day(item['date'])
                if day in self.closed or not self.start <= day <= self.end or item['source'] not in sources:
                    raise CalendarError('duplicate, uncovered, or unsourced holiday')
                self.closed.add(day)
            self.special = {}
            for item in data['special_sessions']:
                day = _day(item['date'])
                if (day in self.special or day in self.closed or not self.start <= day <= self.end
                        or item['source'] not in sources or item['kind'] != 'trading'):
                    raise CalendarError('conflicting, uncovered, mock, or unsourced special session')
                self.special[day] = _hours(item)
        except CalendarError:
            raise
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise CalendarError(f'invalid calendar: {exc}') from exc

    def session(self, day):
        if not self.start <= day <= self.end:
            raise CalendarError(f'calendar does not cover {day}')
        if day in self.special:
            return self.special[day]
        return self.normal if day.weekday() < 5 and day not in self.closed else None

    def expected_session(self, now):
        if now.tzinfo is None:
            now = now.replace(tzinfo=IST)
        now = now.astimezone(IST)
        if not self.start <= now.date() <= self.end:
            raise CalendarError(f'calendar does not cover {now.date()}')
        if now.date() > self.expires:
            raise CalendarError(f'calendar review expired after {self.expires}; verify NSE updates')
        day = now.date()
        while day >= self.start:
            hours = self.session(day)
            if hours and datetime.combine(day, hours['ready_after'], IST) <= now:
                return day
            day -= timedelta(days=1)
        raise CalendarError('calendar does not cover the preceding completed session')


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise CalendarError(f'duplicate calendar JSON key: {key}')
        result[key] = value
    return result


def load_calendar(path=None):
    path = Path(path if path is not None else os.environ.get('NSEBOT_CALENDAR', DEFAULT_CALENDAR))
    try:
        with path.open(encoding='utf-8') as fh:
            return SessionCalendar(json.load(fh, object_pairs_hook=_unique_keys))
    except (OSError, ValueError, TypeError) as exc:
        raise CalendarError(f'cannot use session calendar {path}: {exc}') from exc
