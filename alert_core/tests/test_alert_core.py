import asyncio
import os
import sys
from uuid import uuid4
from datetime import datetime

# Ensure repo root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from alert_core.TESTER import run_test

from data.data_locker import DataLocker
from alert_core.alert_core import AlertCore
from data.alert import AlertType, Condition


def _create_position(dl, pos_id="pos1"):
    position = {
        "id": pos_id,
        "asset_type": "BTC",
        "entry_price": 10000.0,
        "liquidation_price": 5000.0,
        "position_type": "LONG",
        "wallet_name": "test",
        "current_heat_index": 10.0,
        "pnl_after_fees_usd": 150.0,
        "travel_percent": 0.0,
        "liquidation_distance": 0.0,
    }
    dl.positions.create_position(position)


def _profit_alert(pos_id="pos1"):
    return {
        "id": str(uuid4()),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "alert_type": AlertType.Profit.value,
        "alert_class": "Position",
        "asset_type": "BTC",
        "trigger_value": 50.0,
        "condition": Condition.ABOVE.value,
        "notification_type": "Email",
        "position_reference_id": pos_id,
    }


def test_alert_core_create_and_process(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)

    dl = DataLocker(str(tmp_path / "core.db"))
    core = AlertCore(dl, lambda: {})

    _create_position(dl)
    alert = _profit_alert()

    asyncio.run(core.create_alert(alert))
    results = asyncio.run(core.process_alerts())

    assert len(results) == 1
    processed = results[0]
    assert processed.evaluated_value == 150.0

    stored = dl.db.fetch_all("alerts")[0]
    assert stored["evaluated_value"] == 150.0
    assert stored["level"].lower() in {"normal", "low", "medium", "high"}

def test_alert_core_basic():
    run_test()

