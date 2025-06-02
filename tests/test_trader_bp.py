import types
import importlib

import pytest

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask

from trader.trader_bp import trader_bp


class DummyWallets:
    def get_wallet_by_name(self, name):
        return {"name": name}


class DummyLocker:
    def __init__(self):
        self.wallets = DummyWallets()
        self.positions = types.SimpleNamespace(get_all_positions=lambda: [])
        self.portfolio = types.SimpleNamespace(get_latest_snapshot=lambda: {})

    def get_last_update_times(self):
        return {}


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


def test_trader_factory_index(client):
    resp = client.get("/trader/factory")
    assert resp.status_code == 200
    assert b"Angie" in resp.data
