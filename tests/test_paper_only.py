"""Fail closed before any credential access, transport, or runner side effects."""
import pytest

from nsebot import __main__ as cli
from nsebot.broker.kite import KiteBroker, KiteSession, LiveTradingDisabled
from nsebot.kite_login import main as login


@pytest.mark.parametrize('kind', ['kite', 'live', 'unknown', ''])
def test_factory_rejects_every_nonpaper_broker(kind):
    with pytest.raises(ValueError, match='disabled'):
        cli._broker(kind)


@pytest.mark.parametrize('command', ['swing', 'intraday'])
@pytest.mark.parametrize('via_env', [False, True])
def test_cli_rejects_live_before_dispatch(command, via_env, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('runner side effects must not start')
    monkeypatch.setattr(cli, 'cmd_' + command, forbidden)
    argv = [command]
    if via_env:
        monkeypatch.setenv('NSEBOT_BROKER', 'kite')
    else:
        argv += ['--broker', 'kite']
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)
    assert exc.value.code == 2


@pytest.mark.parametrize('client', [None, object()])
def test_session_rejects_real_transport_without_reading_credentials(client, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('credential access must not occur')
    monkeypatch.setattr('nsebot.broker.kite.os.environ.get', forbidden)
    with pytest.raises(LiveTradingDisabled):
        KiteSession(client=client)


def test_login_is_disabled():
    assert login([]) == 2


def test_factory_defaults_to_simulated_execution():
    broker = cli._broker('paper')
    assert broker.name == 'paper'
    assert broker.is_live is False


def test_broker_rejects_transport_injection_before_loading_instruments():
    with pytest.raises(LiveTradingDisabled):
        KiteBroker(object())


def test_fresh_portfolio_has_one_lakh_and_refuses_existing_state(tmp_path):
    import json
    from scripts.init_research import initialize
    root = tmp_path / 'fresh'
    initialize(root)
    before = {p: p.read_bytes() for p in root.rglob('state.json')}
    states = [json.loads(value) for value in before.values()]
    assert len(states) == 3
    assert sum(state['cash'] for state in states) == 100_000
    assert all(not state['positions'] and not state['pending'] for state in states)
    with pytest.raises(FileExistsError):
        initialize(root)
    assert {p: p.read_bytes() for p in before} == before
