"""Downloads must reject HTML/block pages, changed PDFs, and implicit network use."""

from types import SimpleNamespace

import pytest

from nsebot.research import fetch_official as fetch


def test_network_flag_is_required_before_any_request(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail('network must not start without explicit flag')

    monkeypatch.setattr(fetch.requests, 'get', forbidden)
    with pytest.raises(SystemExit) as exc:
        fetch.main(['--group', 'calendar', '--out', str(tmp_path / 'out')])
    assert exc.value.code == 2


@pytest.mark.parametrize('status, content', [(200, b'<html>blocked</html>'), (403, b'blocked'),
                                           (302, b'redirect'), (200, b'%PDF-1.7 changed source')])
def test_bad_or_changed_official_pdf_is_not_saved(status, content, tmp_path, monkeypatch):
    monkeypatch.setitem(fetch.SOURCES, 'calendar', [fetch.BASE + 'circulars/CMTR76941.pdf'])
    result = fetch.download('calendar', tmp_path / 'out',
                            get=lambda *args, **kwargs: SimpleNamespace(status_code=status, content=content))
    assert result['status'] == 'FAIL'
    assert not (tmp_path / 'out' / 'CMTR76941.pdf').exists()


def test_existing_destination_is_never_replaced(tmp_path):
    root = tmp_path / 'existing'
    root.mkdir()
    marker = root / 'keep.txt'
    marker.write_text('preserve', encoding='utf-8')
    with pytest.raises(FileExistsError):
        fetch.download('calendar', root)
    assert marker.read_text(encoding='utf-8') == 'preserve'
