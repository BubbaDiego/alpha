import types
import pytest

from flask import Flask

from sonic_labs.sonic_labs_bp import sonic_labs_bp


class DummyEngine:
    def __init__(self, log):
        self.log = log

    async def select_position_type(self, kind):
        self.log.append(("select_position_type", kind))


class DummySequencer:
    def __init__(self, log):
        self.log = log

    async def run_full_open_position_flow(self, **kwargs):
        self.log.append(("run_full_open_position_flow", kwargs))
        return "ok"


class DummyCore:
    def __init__(self, log):
        self.engine = DummyEngine(log)
        self.sequencer = DummySequencer(log)


def make_client(log):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.data_locker = object()
    app.order_core = DummyCore(log)
    app.register_blueprint(sonic_labs_bp, url_prefix="/sonic_labs")
    return app.test_client()


def test_engine_action_endpoint(monkeypatch):
    log = []
    client = make_client(log)
    resp = client.post(
        "/sonic_labs/api/order_engine_action",
        json={"action": "select_position_type", "value": "long"},
    )
    assert resp.status_code == 200
    assert ("select_position_type", "long") in log


def test_sequence_endpoint(monkeypatch):
    log = []
    client = make_client(log)
    resp = client.post(
        "/sonic_labs/api/order_sequence",
        json={"flow": "run_full_open_position_flow", "params": {"asset": "SOL"}},
    )
    assert resp.status_code == 200
    assert any(evt[0] == "run_full_open_position_flow" for evt in log)

