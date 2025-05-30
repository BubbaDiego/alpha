import pytest
from data.data_locker import DataLocker
from alert_core.alert_store import AlertStore


def _insert_position(dl):
    pos = {
        "id": "pos1",
        "asset_type": "BTC",
        "entry_price": 100.0,
        "liquidation_price": 50.0,
        "position_type": "LONG",
        "wallet_name": "test",
        "current_heat_index": 0.0,
        "pnl_after_fees_usd": 0.0,
        "travel_percent": 0.0,
        "liquidation_distance": 0.0,
    }
    dl.positions.insert_position(pos)


def test_position_alert_respects_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "alerts.db"
    dl = DataLocker(str(db_path))
    _insert_position(dl)

    def cfg():
        return {
            "alert_ranges": {
                "positions_alerts": {
                    "heat_index": {"enabled": False},
                    "travel_percent": {"enabled": True, "medium": 5},
                    # profit intentionally missing
                }
            }
        }

    store = AlertStore(dl, cfg)
    store.create_position_alerts()

    alerts = dl.db.fetch_all("alerts")
    types = {a["alert_type"] for a in alerts}
    assert types == {"TravelPercentLiquid"}


def test_portfolio_alert_respects_disabled(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "alerts2.db"
    dl = DataLocker(str(db_path))

    def cfg():
        return {
            "alert_ranges": {
                "portfolio_alerts": {
                    "total_value": {"enabled": False},
                    "total_size": {"enabled": True, "medium": 2},
                }
            }
        }

    store = AlertStore(dl, cfg)
    store.create_portfolio_alerts()

    alerts = dl.db.fetch_all("alerts")
    types = {a["alert_type"] for a in alerts}
    assert types == {"TotalSize"}


def test_disabled_string_values(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "alerts3.db"
    dl = DataLocker(str(db_path))
    _insert_position(dl)

    def cfg():
        return {
            "alert_ranges": {
                "positions_alerts": {
                    "heat_index": {"enabled": "false"},
                    "travel_percent": {"enabled": "true", "medium": 5},
                },
                "portfolio_alerts": {
                    "total_value": {"enabled": "false"},
                    "total_size": {"enabled": "true", "medium": 2},
                },
            }
        }

    store = AlertStore(dl, cfg)
    store.create_portfolio_alerts()
    store.create_position_alerts()

    alerts = dl.db.fetch_all("alerts")
    types = {a["alert_type"] for a in alerts}
    assert types == {"TravelPercentLiquid", "TotalSize"}
