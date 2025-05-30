import pytest
import importlib

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask
from sonic_labs.sonic_labs_bp import sonic_labs_bp
from data.models import Hedge

class MockPositions:
    def __init__(self):
        self.data = {
            "long1": {
                "id": "long1",
                "position_type": "LONG",
                "entry_price": 100.0,
                "liquidation_price": 50.0,
                "size": 1.0,
                "collateral": 100.0,
                "leverage": 1.0,
                "current_price": 100.0,
            },
            "short1": {
                "id": "short1",
                "position_type": "SHORT",
                "entry_price": 110.0,
                "liquidation_price": 160.0,
                "size": 1.0,
                "collateral": 100.0,
                "leverage": 1.0,
                "current_price": 110.0,
            },
        }

    def get_position_by_id(self, pid):
        return self.data.get(pid)

class MockHedges:
    def get_hedges(self):
        h = Hedge(id="h1", positions=["long1", "short1"])
        return [h]

class MockSystem:
    def get_active_theme_profile(self):
        return {}

class MockModifiers:
    def get_all_modifiers(self, group):
        return {}

class MockDataLocker:
    def __init__(self):
        self.positions = MockPositions()
        self.hedges = MockHedges()
        self.system = MockSystem()
        self.modifiers = MockModifiers()

def make_client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.data_locker = MockDataLocker()
    app.register_blueprint(sonic_labs_bp, url_prefix="/sonic_labs")
    return app.test_client()


def test_evaluate_hedge_endpoint():
    client = make_client()
    resp = client.get("/sonic_labs/api/evaluate_hedge", query_string={"hedge_id": "h1", "price": "120"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "long" in data and "short" in data
    assert data["long"]["id"] == "long1"
    assert data["short"]["id"] == "short1"


