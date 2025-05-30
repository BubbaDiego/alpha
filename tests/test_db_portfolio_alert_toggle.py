import asyncio

from data.data_locker import DataLocker
from alert_core.alert_core import AlertCore


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


def _base_config():
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


def _disable_portfolio(cfg):
    import copy
    cfg = copy.deepcopy(cfg)
    port = cfg["alert_ranges"]["portfolio_alerts"]
    for key in port:
        port[key]["enabled"] = False
    return cfg


def test_db_portfolio_alert_toggle(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "alerts.db"
    dl = DataLocker(str(db_path))
    _insert_position(dl)

    all_enabled = _base_config()
    dl.system.set_var("alert_thresholds", all_enabled)

    core = AlertCore(dl)
    print("\n🚀 Creating alerts with all enabled")
    asyncio.run(core.create_all_alerts())

    alerts = dl.db.fetch_all("alerts")
    portfolio_alerts = [a for a in alerts if a["alert_class"] == "Portfolio"]
    print(f"Portfolio alerts after enable: {len(portfolio_alerts)}")
    assert len(portfolio_alerts) == 6

    disabled_cfg = _disable_portfolio(all_enabled)
    dl.system.set_var("alert_thresholds", disabled_cfg)
    print("\n🚀 Running creation with portfolio alerts disabled")
    asyncio.run(core.create_all_alerts())

    alerts2 = dl.db.fetch_all("alerts")
    portfolio_alerts2 = [a for a in alerts2 if a["alert_class"] == "Portfolio"]
    print(f"Portfolio alerts after disable run: {len(portfolio_alerts2)}")
    assert len(portfolio_alerts2) == 6

    dl.system.set_var("alert_thresholds", all_enabled)
    print("\n🚀 Re-enabling portfolio alerts and creating again")
    asyncio.run(core.create_all_alerts())

    alerts3 = dl.db.fetch_all("alerts")
    portfolio_alerts3 = [a for a in alerts3 if a["alert_class"] == "Portfolio"]
    print(f"Portfolio alerts after re-enable run: {len(portfolio_alerts3)}")
    assert len(portfolio_alerts3) == 6

