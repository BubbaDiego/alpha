import pytest
import importlib

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask
from app.dashboard_bp import dashboard_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(dashboard_bp)
    with app.test_client() as client:
        yield client

def test_profit_badge_in_test_dashboard(client):
    response = client.get("/test/desktop")
    assert response.status_code == 200
    html = response.data.decode()
    assert "profit-badge" in html
    assert "123" in html

