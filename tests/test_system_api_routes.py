import types
import pytest
from flask import Flask

from app.system_bp import system_bp


@pytest.fixture
def make_app(monkeypatch):
    def _make(core):
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.register_blueprint(system_bp, url_prefix="/system")
        monkeypatch.setattr("app.system_bp.get_core", lambda: core)
        return app
    return _make


def test_api_check_route_calls_core(monkeypatch, make_app):
    called = {}

    def check_api(name):
        called["name"] = name
        return {"result": True}

    core = types.SimpleNamespace(check_api=check_api)
    app = make_app(core)
    with app.test_client() as client:
        resp = client.get("/system/api/check/twilio")
        assert resp.status_code == 200
        assert resp.get_json() == {"result": True}
        assert called["name"] == "twilio"


def test_xcom_api_status_aggregates(monkeypatch, make_app):
    core = types.SimpleNamespace(
        check_twilio_api=lambda: {"success": True},
        check_chatgpt=lambda: {"success": True},
        check_jupiter=lambda: {"success": False, "error": "boom"},
        check_github=lambda: {"success": True},
    )
    app = make_app(core)
    with app.test_client() as client:
        resp = client.get("/system/xcom_api_status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {
            "twilio": "ok",
            "chatgpt": "ok",
            "jupiter": "error: boom",
            "github": "ok",
        }
