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


def load_service(monkeypatch, mock_post=None, mock_get=None):
    requests_stub = SimpleNamespace(post=mock_post, get=mock_get)
    monkeypatch.setitem(sys.modules, "requests", requests_stub)
    import wallets.jupiter_trigger_service as svc
    importlib.reload(svc)
    return svc, svc.JupiterTriggerService


def test_create_trigger_order_success(monkeypatch):
    calls = {}

    def mock_post(url, json=None, timeout=None):
        calls["url"] = url
        calls["json"] = json
        return DummyResponse({"ok": True})

    svc_mod, TriggerService = load_service(monkeypatch, mock_post, lambda *a, **k: None)
    svc = TriggerService(api_base="http://test")
    result = svc.create_trigger_order("w1", "BTC", 10.0, 2.0, True)

    assert result == {"ok": True}
    assert calls["url"] == "http://test/v1/create_trigger_order"
    assert calls["json"] == {
        "wallet": "w1",
        "market": "BTC",
        "trigger_price": 10.0,
        "size": 2.0,
        "is_long": True,
    }


def test_cancel_trigger_order_success(monkeypatch):
    def mock_post(url, json=None, timeout=None):
        return DummyResponse({"ok": True})

    svc_mod, TriggerService = load_service(monkeypatch, mock_post, lambda *a, **k: None)
    svc = TriggerService(api_base="http://test")
    result = svc.cancel_trigger_order("w", "ord123")

    assert result == {"ok": True}


def test_get_trigger_orders_error(monkeypatch):
    def mock_get(url, params=None, timeout=None):
        return DummyResponse(status=500)

    svc_mod, TriggerService = load_service(monkeypatch, lambda *a, **k: None, mock_get)
    svc = TriggerService(api_base="http://test")
    with pytest.raises(Exception):
        svc.get_trigger_orders("w")

