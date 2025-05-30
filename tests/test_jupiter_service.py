import sys
import importlib
from types import SimpleNamespace
import pytest


class DummyResponse:
    def __init__(self, data=None, status=200):
        self._data = data or {}
        self.status_code = status

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("error")


def load_service(monkeypatch, mock_post):
    requests_stub = SimpleNamespace(post=mock_post)
    monkeypatch.setitem(sys.modules, 'requests', requests_stub)
    import wallets.jupiter_service as js
    importlib.reload(js)
    return js, js.JupiterService


def test_increase_position_success(monkeypatch):
    calls = {}

    def mock_post(url, json=None, timeout=None):
        calls['url'] = url
        calls['json'] = json
        return DummyResponse({'ok': True})

    js, JupiterService = load_service(monkeypatch, mock_post)
    svc = JupiterService(api_base='http://test')
    result = svc.increase_position('wallet1', 'BTC', 5.0)

    assert result == {'ok': True}
    assert calls['url'] == 'http://test/v1/increase_position'
    assert calls['json'] == {
        'wallet': 'wallet1',
        'market': 'BTC',
        'collateral_delta': 5.0,
        'size_usd_delta': 0,
    }


def test_decrease_position_success(monkeypatch):
    def mock_post(url, json=None, timeout=None):
        return DummyResponse({'ok': True})

    js, JupiterService = load_service(monkeypatch, mock_post)
    svc = JupiterService(api_base='http://test')
    result = svc.decrease_position('w', 'ETH', 1.2)

    assert result == {'ok': True}


def test_increase_position_error(monkeypatch):
    def mock_post(url, json=None, timeout=None):
        return DummyResponse(status=500)

    js, JupiterService = load_service(monkeypatch, mock_post)
    svc = JupiterService(api_base='http://test')
    with pytest.raises(Exception):
        svc.increase_position('w', 'BTC', 1.0)

