from pathlib import Path
import runpy
import subprocess
import sys

import pytest


def launcher():
    return runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/research.py'))['main']


def test_offline_launcher_preserves_paths_with_spaces_and_needs_no_network_flag(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(subprocess, 'call', lambda command: calls.append(command) or 0)
    manifest = tmp_path / 'reviewed sample/manifest.json'
    output = tmp_path / 'research results'
    monkeypatch.setattr(sys, 'argv', ['research.py', 'offline-backtest', '--manifest', str(manifest),
                                      '--out', str(output)])
    assert launcher()() == 0
    assert calls == [[sys.executable, '-X', 'utf8', '-m', 'nsebot.research.offline_backtest',
                       '--manifest', str(manifest.resolve()), '--out', str(output.resolve())]]


@pytest.mark.parametrize('arguments', [['backtest'], ['offline-backtest'],
                                      ['status', '--manifest', 'sample.json']])
def test_launcher_rejects_missing_network_permission_or_manifest_before_dispatch(monkeypatch, arguments):
    monkeypatch.setattr(sys, 'argv', ['research.py', *arguments])
    def forbidden(*a, **kw):
        pytest.fail('invalid command must not dispatch any process')
    monkeypatch.setattr(subprocess, 'call', forbidden)
    with pytest.raises(SystemExit) as exc:
        launcher()()
    assert exc.value.code == 2
