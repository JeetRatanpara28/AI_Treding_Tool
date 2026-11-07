"""Offline calendar boundaries, official special cases, and fail-closed behavior."""

import json
from datetime import datetime

import pandas as pd
import pytest

from nsebot.__main__ import main
from nsebot.session_calendar import CalendarError, DEFAULT_CALENDAR, SessionCalendar, load_calendar


@pytest.mark.parametrize('now, expected', [
    ('2026-01-15 18:00', '2026-01-14'),
    ('2026-02-01 16:14:59', '2026-01-30'),
    ('2026-02-01 16:15:00', '2026-02-01'),
    ('2026-02-02 09:00', '2026-02-01'),
    ('2026-11-08 16:14:59', '2026-11-06'),
    ('2026-11-08 16:15:00', '2026-11-08'),
    ('2026-11-09 09:00', '2026-11-08'),
    ('2026-11-10 18:00', '2026-11-09'),
    ('2026-11-08 10:45:00+00:00', '2026-11-08'),
])
def test_verified_holidays_and_special_sessions(now, expected):
    calendar = load_calendar()
    assert calendar.expected_session(datetime.fromisoformat(now)).isoformat() == expected


@pytest.mark.parametrize('now, message', [
    ('2027-01-01 18:00', 'does not cover'),
    ('2025-12-31 18:00', 'does not cover'),
    ('2026-01-01 10:00', 'preceding completed session'),
    ('2026-11-11 10:00', 'review expired'),
])
def test_unknown_or_expired_coverage_never_falls_back_to_weekdays(now, message):
    with pytest.raises(CalendarError, match=message):
        load_calendar().expected_session(datetime.fromisoformat(now))


@pytest.mark.parametrize('problem', ['schema', 'segment', 'timezone', 'coverage', 'sources',
                                    'source_url', 'hash', 'duplicate_holiday', 'duplicate_session',
                                    'conflicting_date', 'hours', 'mock_session', 'missing_hours'])
def test_bad_schedule_is_rejected(problem):
    data = json.loads(DEFAULT_CALENDAR.read_text(encoding='utf-8'))
    if problem == 'schema':
        data['schema_version'] = 99
    elif problem == 'segment':
        data['segment'] = 'derivatives'
    elif problem == 'timezone':
        data['timezone'] = 'UTC'
    elif problem == 'coverage':
        data['coverage_end'] = '2026-01-01'
    elif problem == 'sources':
        data['sources'] = {}
    elif problem == 'source_url':
        data['sources']['annual']['url'] = 'https://example.com/calendar'
    elif problem == 'hash':
        data['sources']['muhurat']['sha256'] = 'invalid'
    elif problem == 'duplicate_holiday':
        data['holidays'].append(data['holidays'][0])
    elif problem == 'duplicate_session':
        data['special_sessions'].append(data['special_sessions'][0])
    elif problem == 'conflicting_date':
        data['special_sessions'][0]['date'] = data['holidays'][0]['date']
    elif problem == 'hours':
        data['special_sessions'][0]['ready_after'] = '15:00'
    elif problem == 'mock_session':
        data['special_sessions'][0]['kind'] = 'mock'
    elif problem == 'missing_hours':
        del data['special_sessions'][0]['normal_close']
    with pytest.raises(CalendarError):
        SessionCalendar(data)


def test_duplicate_json_keys_are_not_silently_accepted(tmp_path):
    path = tmp_path / 'bad.json'
    path.write_text('{"schema_version":1,"schema_version":2}', encoding='utf-8')
    with pytest.raises(CalendarError, match='duplicate calendar JSON key'):
        load_calendar(path)


@pytest.mark.parametrize('command', ['swing', 'momentum', 'intraday'])
@pytest.mark.parametrize('problem', ['missing', 'corrupt', 'expired'])
def test_calendar_failure_stops_cli_before_download_or_ledger_access(command, problem, tmp_path, monkeypatch, caplog):
    path = tmp_path / 'calendar.json'
    if problem == 'corrupt':
        path.write_text('not JSON', encoding='utf-8')
    elif problem == 'expired':
        data = json.loads(DEFAULT_CALENDAR.read_text(encoding='utf-8'))
        data['review_expires'] = '2026-11-06'
        path.write_text(json.dumps(data), encoding='utf-8')
    monkeypatch.setenv('NSEBOT_CALENDAR', str(path))
    monkeypatch.setattr('nsebot.market.now_ist', lambda: pd.Timestamp('2026-11-07 10:00', tz='Asia/Kolkata'))

    def forbidden(*args, **kwargs):
        pytest.fail('calendar failure must stop before network or portfolio access')

    monkeypatch.setattr('nsebot.data.YahooProvider.daily', forbidden)
    monkeypatch.setattr('nsebot.__main__.Ledger', forbidden)
    state = tmp_path / 'state'
    assert main([command, '--state', str(state)]) == 3
    assert 'SESSION CALENDAR' in caplog.text
    assert not state.exists()


def test_scheduling_gate_and_cli_share_special_session_and_cutoff():
    from scripts.should_run import expected_session
    from nsebot.freshness import expected_daily_session
    for now in ('2026-11-08 16:14:59', '2026-11-08 16:15', '2026-11-09 09:00'):
        assert pd.Timestamp(expected_session(datetime.fromisoformat(now))) == expected_daily_session(now)


def test_manual_gate_cannot_bypass_bad_calendar(tmp_path, monkeypatch):
    from scripts.should_run import decide
    monkeypatch.setenv('NSEBOT_CALENDAR', str(tmp_path / 'missing.json'))
    run, reason = decide('momentum', datetime.fromisoformat('2026-11-08 18:00'), {}, 'workflow_dispatch')
    assert run is False and 'session calendar unavailable' in reason


@pytest.mark.parametrize('now, expected_code', [('2026-11-08 14:30', 3), ('2026-11-10 10:00', 0),
                                               ('2026-11-07 12:00', 0)])
def test_intraday_never_uses_regular_hours_on_special_or_closed_day(now, expected_code, tmp_path, monkeypatch):
    monkeypatch.setattr('nsebot.market.now_ist', lambda: pd.Timestamp(now, tz='Asia/Kolkata'))

    def forbidden(*args, **kwargs):
        pytest.fail('unsupported/closed intraday session must not download or access portfolio')

    monkeypatch.setattr('nsebot.__main__.Ledger', forbidden)
    monkeypatch.setattr('nsebot.data.YahooProvider.daily', forbidden)
    assert main(['intraday', '--state', str(tmp_path / 'state')]) == expected_code
