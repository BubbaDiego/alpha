import pytest

from flask import Flask, render_template

from app.dashboard_bp import dashboard_bp
from app.alerts_bp import alerts_bp
from app.system_bp import system_bp
from dashboard import dashboard_service

@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp, url_prefix="/alerts")
    app.register_blueprint(system_bp, url_prefix="/system")

    # Simplify heavy view logic
    app.view_functions["alerts.alert_status_page"] = lambda: render_template("alert_status.html", alerts=[])
    app.view_functions["system.hedge_calculator_page"] = lambda: render_template(
        "hedge_modifiers.html",
        theme={},
        long_positions=[],
        short_positions=[],
        modifiers={},
        default_long_id=None,
        default_short_id=None,
    )

    app.data_locker = object()
    app.system_core = object()

    monkeypatch.setattr(dashboard_service, "get_profit_badge_value", lambda dl, sc: 42)

    @app.context_processor
    def inject_profit_badge():
        value = dashboard_service.get_profit_badge_value(app.data_locker, app.system_core)
        return {"profit_badge_value": value}

    with app.test_client() as client:
        yield client

def test_badge_on_new_dashboard(client):
    resp = client.get("/new_dashboard")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "profit-badge" in html
    assert "42" in html

def test_badge_on_hedge_calculator(client):
    resp = client.get("/system/hedge_calculator")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "profit-badge" in html
    assert "42" in html

def test_badge_on_alert_status(client):
    resp = client.get("/alerts/status_page")
    assert resp.status_code == 200
    html = resp.data.decode()
    assert "profit-badge" in html
    assert "42" in html
