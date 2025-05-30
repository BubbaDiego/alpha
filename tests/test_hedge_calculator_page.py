import pytest
import importlib

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask

from sonic_labs.sonic_labs_bp import sonic_labs_bp

class MockPositionService:
    @staticmethod
    def get_all_positions(db_path):
        return [
            {"id": "long1", "position_type": "LONG"},
            {"id": "short1", "position_type": "SHORT"},
        ]

class MockSystem:
    def get_active_theme_profile(self):
        return {}

class MockModifiers:
    def get_all_modifiers(self, group):
        return {}

class MockDataLocker:
    def __init__(self):
        self.system = MockSystem()
        self.modifiers = MockModifiers()

@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.data_locker = MockDataLocker()

    # Patch PositionService used inside the blueprint
    monkeypatch.setitem(sonic_labs_bp.__dict__, "PositionService", MockPositionService)

    app.register_blueprint(sonic_labs_bp, url_prefix="/sonic_labs")

    with app.test_client() as client:
        yield client

def test_hedge_modifiers_page_contains_inputs(client):
    response = client.get("/sonic_labs/hedge_calculator")
    assert response.status_code == 200
    html = response.data.decode()
    assert "feePercentage" in html
    assert "distanceWeightInput" in html
