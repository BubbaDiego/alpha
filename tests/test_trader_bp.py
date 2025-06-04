import types
import importlib

import pytest

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask

from trader_core.trader_bp import trader_bp


class DummyWallets:
    def get_wallets(self):
        return [{"name": "TestWallet", "balance": 5.0}]

    def get_wallet_by_name(self, name):
        return {"name": name, "balance": 1.23}

    def read_wallets(self):
        return self.get_wallets()


class DummyTraders:
    """Minimal traders manager stub."""

    def delete_trader(self, name):
        return False


class DummyLocker:
    def __init__(self):
        self.wallets = DummyWallets()
        self.traders = DummyTraders()
        self.positions = types.SimpleNamespace(get_all_positions=lambda: [])
        self.portfolio = types.SimpleNamespace(get_latest_snapshot=lambda: {})

    def get_last_update_times(self):
        return {}

    def read_wallets(self):
        return self.wallets.get_wallets()


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.data_locker = DummyLocker()
    app.register_blueprint(trader_bp)
    with app.test_client() as client:
        yield client


def test_trader_api(client):
    resp = client.get("/trader/api/Angie")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Angie"


def test_trader_factory_page(client):
    resp = client.get("/trader/factory/Angie")
    assert resp.status_code == 200
    assert b"Angie" in resp.data


def test_trader_cards_page(client):
    resp = client.get("/trader/cards")
    assert resp.status_code == 200
    # Should include at least one persona name
    assert b"Angie" in resp.data


def test_wallet_list_api(client):
    resp = client.get("/trader/api/wallets")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert isinstance(data["wallets"], list)


def test_delete_missing_trader_returns_error(client):
    resp = client.delete("/trader/api/traders/Ghost/delete")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["success"] is False
