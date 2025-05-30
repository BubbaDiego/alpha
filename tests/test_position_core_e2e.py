import sys
import types
import pytest
from datetime import datetime
from uuid import uuid4

# Stub the requests module before importing PositionSyncService
requests_stub = types.ModuleType("requests")
sys.modules.setdefault("requests", requests_stub)

from data.data_locker import DataLocker
from positions.position_core import PositionCore
from positions.position_sync_service import PositionSyncService


def build_test_position(id=None):
    return {
        "id": id or str(uuid4()),
        "asset_type": "BTC",
        "position_type": "long",
        "entry_price": 42000.0,
        "current_price": 41000.0,
        "liquidation_price": 39000.0,
        "collateral": 1000.0,
        "size": 0.05,
        "leverage": 2.0,
        "value": 2000.0,
        "wallet_name": "TestWallet",
        "last_updated": datetime.now().isoformat(),
        "pnl_after_fees_usd": 50.0,
        "travel_percent": 5.0,
    }


@pytest.fixture
def dl(tmp_path, monkeypatch):
    for name in [
        "_seed_modifiers_if_empty",
        "_seed_wallets_if_empty",
        "_seed_thresholds_if_empty",
        "_seed_alerts_if_empty",
    ]:
        monkeypatch.setattr(DataLocker, name, lambda self: None)
    db_file = tmp_path / "test.db"
    locker = DataLocker(str(db_file))
    yield locker
    locker.db.close()


def test_position_core_sync_records_snapshot(dl, monkeypatch):
    core = PositionCore(dl)
    sync = PositionSyncService(dl)

    core.clear_all_positions()
    core.create_position(build_test_position())
    assert len(core.get_all_positions()) == 1

    assert dl.portfolio.get_latest_snapshot() == {}

    monkeypatch.setattr(
        PositionSyncService,
        "update_jupiter_positions",
        lambda self: {"message": "ok", "imported": 0, "skipped": 0, "errors": 0},
    )

    result = sync.run_full_jupiter_sync(source="test_runner")

    assert result["success"] is True
    assert result["imported"] == 0
    snapshot = dl.portfolio.get_latest_snapshot()
    assert snapshot != {}

