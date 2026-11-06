"""Archived upstream scheduling invariants and active publication safety guards."""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _wf(name):
    return open(os.path.join(ROOT, 'docs', 'archived-workflows', name + '.disabled')).read()


def _crons(text):
    return re.findall(r"cron:\s*'([^']+)'", text)


def _group(text):
    return re.search(r'concurrency:\s*\n\s*group:\s*(\S+)', text).group(1)


def test_each_bot_has_its_own_queue():
    groups = [_group(_wf(f)) for f in ('main.yml', 'momentum.yml', 'intraday.yml')]
    assert len(set(groups)) == 3, groups


def _slots(cron):
    """(minute, hour) pairs a cron line fires on, for 'M H-H' and 'M H,H' forms."""
    minute, hours = cron.split()[:2]
    hs = []
    for part in hours.split(','):
        a, _, b = part.partition('-')
        hs += list(range(int(a), int(b or a) + 1))
    return [(int(m), h) for m in minute.split(',') for h in hs]


def test_end_of_day_bots_have_many_slots_and_a_next_morning_backup():
    for f in ('main.yml', 'momentum.yml'):
        crons = _crons(_wf(f))
        assert sum(len(_slots(c)) for c in crons) >= 10, (f, crons)
        assert any(c.split()[4] == '2-6' for c in crons), f'{f}: no next-morning backup'


def test_no_slot_at_the_busy_top_or_half_hour():
    for f in ('main.yml', 'momentum.yml', 'intraday.yml'):
        for c in _crons(_wf(f)):
            assert all(m not in (0, 30) for m, _ in _slots(c)), (f, c)


def test_every_scheduled_run_passes_the_gate_first():
    for f, mode in (('main.yml', 'swing'), ('momentum.yml', 'momentum'), ('intraday.yml', 'intraday')):
        text = _wf(f)
        assert f'python3 scripts/should_run.py {mode}' in text, f
        assert text.count("steps.gate.outputs.run == 'true'") == 4, f   # python, install, bot, commit


def test_intraday_session_fits_inside_the_job_limit():
    text = _wf('intraday.yml')
    timeout = int(re.search(r'timeout-minutes:\s*(\d+)', text).group(1))
    assert timeout <= 360                                    # GitHub's cap for hosted runners
    end_ist = 15 * 60 + 12                                   # square-off 15:10 + 2 minutes
    for c in _crons(text):
        for minute, hour in _slots(c):
            start_ist = hour * 60 + minute + 330             # UTC -> IST
            assert start_ist >= 9 * 60 + 15                  # never before the open
            assert end_ist - start_ist + 5 <= timeout        # 5 minutes for setup and the final commit


def test_every_bot_saves_state_and_redraws_the_progress_chart_through_one_script():
    for f in ('main.yml', 'momentum.yml', 'intraday.yml'):
        step = _wf(f).split('- name: Commit state')[1]
        assert "if: always() && steps.gate.outputs.run == 'true'" in step, f
        assert 'run: bash scripts/commit_state.sh "' in step, f


def test_active_workflows_have_no_automatic_events_or_write_permissions():
    from pathlib import Path
    for path in (Path(ROOT) / '.github' / 'workflows').glob('*.yml'):
        text = path.read_text(encoding='utf-8')
        assert 'workflow_dispatch:' in text, path
        assert not re.search(r'^\s*(schedule|push|pull_request|workflow_run|repository_dispatch):', text, re.M), path
        assert 'contents: read' in text, path
        assert 'contents: write' not in text, path
        assert 'commit_state.sh' not in text and 'git push' not in text, path
        assert 'secrets.' not in text, path
        assert not re.search(r'python(?:3)? -m nsebot(?:\s|$)', text), path


def test_trading_workflow_jobs_are_unconditionally_disabled():
    from pathlib import Path
    for name in ('main.yml', 'momentum.yml', 'intraday.yml'):
        text = (Path(ROOT) / '.github' / 'workflows' / name).read_text(encoding='utf-8')
        assert 'if: ${{ false }}' in text, name
        assert 'actions/checkout' not in text, name


def test_manual_research_workflow_runs_only_maintained_tests():
    from pathlib import Path
    text = (Path(ROOT) / '.github' / 'workflows' / 'research.yml').read_text(encoding='utf-8')
    assert 'python -X utf8 -m pytest tests diagnostics -q' in text
    assert 'windows-latest' in text and 'ubuntu-latest' in text
