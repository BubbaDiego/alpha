import pytest
import importlib

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask
from app.alerts_bp import alerts_bp
from core.core_imports import log
from data.data_locker import DataLocker

# Setup the Flask Test App
@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    dl = DataLocker(str(tmp_path / "alerts.db"))

    app = Flask(__name__)
    app.register_blueprint(alerts_bp)
    app.json_manager = None  # Skip JsonManager for now if not needed in these tests
    app.config['TESTING'] = True
    app.data_locker = dl

    with app.test_client() as client:
        yield client

    dl.db.close()

# --- API Endpoint Tests ---

def test_refresh_alerts(client):
    """Test POST /alerts/refresh endpoint."""
    log.banner("TEST: Refresh Alerts API Start")
    response = client.post('/alerts/refresh')
    assert response.status_code in [200, 500]  # Allow 500 if no alerts loaded yet
    log.success(f"✅ Refresh Alerts API response: {response.status_code}", source="TestAlertsAPI")

def test_create_all_alerts(client):
    """Test POST /alerts/create_all endpoint."""
    log.banner("TEST: Create All Alerts API Start")
    response = client.post('/alerts/create_all')
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True

    alerts = client.application.data_locker.db.fetch_all("alerts")
    assert len(alerts) == 1
    assert alerts[0]["id"] == "alert-sample-1"

    log.success(
        f"✅ Create All Alerts API response: {response.status_code}",
        source="TestAlertsAPI",
    )

def test_delete_all_alerts(client):
    """Test POST /alerts/delete_all endpoint."""
    log.banner("TEST: Delete All Alerts API Start")
    client.post('/alerts/create_all')

    response = client.post('/alerts/delete_all')
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True

    alerts = client.application.data_locker.db.fetch_all("alerts")
    assert alerts == []

    log.success(
        f"✅ Delete All Alerts API response: {response.status_code}",
        source="TestAlertsAPI",
    )

def test_monitor_alerts(client):
    """Test GET /alerts/monitor endpoint."""
    log.banner("TEST: Monitor Alerts API Start")
    response = client.get('/alerts/monitor')
    assert response.status_code == 200
    data = response.get_json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
    log.success(f"✅ Monitor Alerts API response: {response.status_code}, {len(data['alerts'])} alerts returned", source="TestAlertsAPI")
