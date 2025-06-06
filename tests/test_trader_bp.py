import types
import pytest

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
    def __init__(self):
        self._traders = []

    def list_traders(self):
        return list(self._traders)

    def get_trader_by_name(self, name):
        for t in self._traders:
            if t.get("name") == name:
                return t
        return None

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

    def get_wallet_by_name(self, name):
        return self.wallets.get_wallet_by_name(name)


@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.data_locker = DummyLocker()
    # Preload a trader for API tests
    app.data_locker.traders._traders.append(
        {
            "name": "Angie",
            "born_on": "2020-01-01T00:00:00",
            "initial_collateral": 0.0,
        }
    )
    app.register_blueprint(trader_bp)
    # Map explicit route for our dummy client
    func = app.routes.get("/trader/api/traders/<name>", {}).get("GET")
    if func:
        app.routes["/trader/api/Angie"] = {"GET": lambda: func(name="Angie")["trader"]}
    with app.test_client() as client:
        yield client


def test_trader_api(client):
    resp = client.get("/trader/api/Angie")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Angie"
    assert "born_on" in data and "initial_collateral" in data
    from datetime import datetime
    datetime.fromisoformat(data["born_on"])


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


def test_list_traders_handles_missing_persona(client):
    client.application.data_locker.traders._traders = [
        {
            "name": "Ghost",
            "born_on": "2020-01-01T00:00:00",
            "initial_collateral": 0.0,
        }
    ]
    resp = client.get("/trader/api/traders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["traders"][0]["name"] == "Ghost"
    assert "wallet_balance" in data["traders"][0]
    assert "born_on" in data["traders"][0]
    assert "initial_collateral" in data["traders"][0]
    from datetime import datetime
    datetime.fromisoformat(data["traders"][0]["born_on"])


def test_list_traders_triggers_wallet_refresh(client):
    called = {}

    def refresh():
        called["r"] = True

    client.application.system_core = types.SimpleNamespace(
        wallet_core=types.SimpleNamespace(refresh_wallet_balances=refresh)
    )
    resp = client.get("/trader/api/traders")
    assert resp.status_code == 200
    assert called.get("r") is True

