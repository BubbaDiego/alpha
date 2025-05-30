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


def _enabled_config():
    return {
        "alert_ranges": {
            "positions_alerts": {
                "heat_index": {"enabled": True},
                "travel_percent": {"enabled": True},
                "profit": {"enabled": True},
            },
            "portfolio_alerts": {
                "total_value": {"enabled": True},
                "total_size": {"enabled": True},
                "avg_leverage": {"enabled": True},
                "avg_travel_percent": {"enabled": True},
                "value_to_collateral_ratio": {"enabled": True},
                "total_heat": {"enabled": True},
            },
        }
    }


def _disabled_config():
    return {
        "alert_ranges": {
            "positions_alerts": {
                "heat_index": {"enabled": False},
                "travel_percent": {"enabled": False},
                "profit": {"enabled": False},
            },
            "portfolio_alerts": {
                "total_value": {"enabled": False},
                "total_size": {"enabled": False},
                "avg_leverage": {"enabled": False},
                "avg_travel_percent": {"enabled": False},
                "value_to_collateral_ratio": {"enabled": False},
                "total_heat": {"enabled": False},
            },
        }
    }


def test_alert_creation_configurebility(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "enabled.db"
    dl = DataLocker(str(db_path))
    _insert_position(dl)

    store = AlertStore(dl, _enabled_config)
    store.create_portfolio_alerts()
    store.create_position_alerts()

    alerts = dl.db.fetch_all("alerts")
    assert len(alerts) == 9

    db_path2 = tmp_path / "disabled.db"
    dl2 = DataLocker(str(db_path2))
    _insert_position(dl2)

    store2 = AlertStore(dl2, _disabled_config)
    store2.create_portfolio_alerts()
    store2.create_position_alerts()

    alerts_disabled = dl2.db.fetch_all("alerts")
    assert len(alerts_disabled) == 0
