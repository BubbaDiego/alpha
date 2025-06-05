import types
import pytest

from flask import Flask
from app.dashboard_bp import dashboard_bp
from dashboard import dashboard_service


def _setup_app(monkeypatch, context):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(dashboard_bp)
    monkeypatch.setattr(
        dashboard_service,
        "get_dashboard_context",
        lambda dl, sc: context,
    )
    app.data_locker = object()
    app.system_core = object()
    return app


def test_dash_page_handles_missing_wallet(monkeypatch):
    context = {
        "positions": [],
        "liquidation_positions": [
            {
                "wallet_name": "Ghost",
                "wallet_image": "ghost.jpg",
                "asset_type": "BTC",
                "travel_percent": 0,
                "heat_index": 0,
            }
        ],
        "wallets": [],
        "status_items": [],
        "monitor_items": [],
        "portfolio_limits": {},
        "profit_badge_value": None,
        "graph_data": {},
        "size_composition": {},
        "collateral_composition": {},
        "price_monitor_history": [],
        "positions_monitor_history": [],
        "operations_monitor_history": [],
        "xcom_monitor_history": [],
        "price_monitor_status": "",
        "positions_monitor_status": "",
        "operations_monitor_status": "",
        "xcom_monitor_status": "",
        "theme_mode": "dark",
    }
    app = _setup_app(monkeypatch, context)
    with app.test_client() as client:
        resp = client.get("/dash")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "ghost.jpg" in html
        assert "/launch/Default/BTC" in html


def test_dash_page_uses_wallet_profile(monkeypatch):
    context = {
        "positions": [],
        "liquidation_positions": [
            {
                "wallet_name": "Known",
                "wallet_image": "known.jpg",
                "asset_type": "ETH",
                "travel_percent": 0,
                "heat_index": 0,
            }
        ],
        "wallets": [
            {"name": "Known", "chrome_profile": "Profile1"}
        ],
        "status_items": [],
        "monitor_items": [],
        "portfolio_limits": {},
        "profit_badge_value": None,
        "graph_data": {},
        "size_composition": {},
        "collateral_composition": {},
        "price_monitor_history": [],
        "positions_monitor_history": [],
        "operations_monitor_history": [],
        "xcom_monitor_history": [],
        "price_monitor_status": "",
        "positions_monitor_status": "",
        "operations_monitor_status": "",
        "xcom_monitor_status": "",
        "theme_mode": "dark",
    }
    app = _setup_app(monkeypatch, context)
    with app.test_client() as client:
        resp = client.get("/dash")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "/launch/Profile1/ETH" in html
