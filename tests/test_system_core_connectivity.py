import importlib
import sys
import types
from types import SimpleNamespace

import pytest


def load_core(monkeypatch, requests_module=None):
    sc = importlib.import_module("system.system_core")
    importlib.reload(sc)
    if requests_module is not None:
        monkeypatch.setattr(sc, "requests", requests_module)
    return sc


def make_core(sc):
    return sc.SystemCore(SimpleNamespace())


def test_check_twilio_api_success(monkeypatch):
    class DummyService:
        def __init__(self, *a, **k):
            pass
        def check(self, dry_run=True):
            return {"success": True}

    monkeypatch.setitem(
        sys.modules,
        "xcom.check_twilio_heartbeat_service",
        types.SimpleNamespace(CheckTwilioHeartbeatService=DummyService),
    )
    sc = load_core(monkeypatch)
    core = make_core(sc)
    assert core.check_twilio_api() == "ok"


def test_check_twilio_api_failure(monkeypatch):
    class DummyService:
        def __init__(self, *a, **k):
            pass
        def check(self, dry_run=True):
            return {"success": False, "error": "fail"}

    monkeypatch.setitem(
        sys.modules,
        "xcom.check_twilio_heartbeat_service",
        types.SimpleNamespace(CheckTwilioHeartbeatService=DummyService),
    )
    sc = load_core(monkeypatch)
    core = make_core(sc)
    assert core.check_twilio_api() == "fail"


def test_check_chatgpt_success(monkeypatch):
    class DummyClient:
        def __init__(self, api_key=None):
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda *a, **k: None))

    monkeypatch.setenv("OPENAI_API_KEY", "key")
    monkeypatch.setitem(sys.modules, "openai", types.SimpleNamespace(OpenAI=DummyClient))
    sc = load_core(monkeypatch)
    core = make_core(sc)
    assert core.check_chatgpt() == "ok"


def test_check_chatgpt_no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPEN_AI_KEY", raising=False)
    sc = load_core(monkeypatch)
    core = make_core(sc)
    assert core.check_chatgpt() == "missing api key"


def test_check_jupiter_success(monkeypatch):
    class DummyResp:
        def raise_for_status(self):
            pass
    class Requests:
        def get(self, url, timeout=None):
            return DummyResp()
    sc = load_core(monkeypatch, Requests())
    core = make_core(sc)
    assert core.check_jupiter() == "ok"


def test_check_jupiter_error(monkeypatch):
    class Requests:
        def get(self, url, timeout=None):
            raise Exception("boom")
    sc = load_core(monkeypatch, Requests())
    core = make_core(sc)
    assert core.check_jupiter() == "boom"


def test_check_github_success(monkeypatch):
    class DummyResp:
        def raise_for_status(self):
            pass

    class Requests:
        def get(self, url, timeout=None):
            return DummyResp()

    sc = load_core(monkeypatch, Requests())
    core = make_core(sc)
    assert core.check_github() == "ok"


def test_check_github_error(monkeypatch):
    class Requests:
        def get(self, url, timeout=None):
            raise Exception("boom")

    sc = load_core(monkeypatch, Requests())
    core = make_core(sc)
    assert core.check_github() == "boom"


def test_check_api_dispatch(monkeypatch):
    sc = load_core(monkeypatch)
    core = make_core(sc)

    called = {}

    def dummy():
        called["name"] = True
        return "ok"

    monkeypatch.setattr(core, "check_twilio_api", dummy)

    result = core.check_api("twilio")

    assert result == {"status": "ok"}
    assert called["name"] is True


def test_check_api_unknown(monkeypatch):
    sc = load_core(monkeypatch)
    core = make_core(sc)

    assert core.check_api("doesnotexist") == {"status": "unknown api"}
