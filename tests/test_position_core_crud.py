import pytest
from data.data_locker import DataLocker
from positions.position_core import PositionCore


def _patch_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)


def build_pos(id="p1"):
    return {
        "id": id,
        "asset_type": "BTC",
        "position_type": "LONG",
        "entry_price": 100.0,
        "current_price": 110.0,
        "liquidation_price": 50.0,
        "collateral": 10.0,
        "size": 0.5,
        "wallet_name": "test",
    }


def test_create_position_enriches(tmp_path, monkeypatch):
    _patch_seeding(monkeypatch)
    dl = DataLocker(str(tmp_path / "pos.db"))
    core = PositionCore(dl)

    core.create_position(build_pos())

    rows = dl.positions.get_all_positions()
    assert len(rows) == 1
    stored = rows[0]
    assert stored["leverage"] > 0
    assert stored["travel_percent"] != 0
    dl.db.close()


def test_delete_and_clear_positions(tmp_path, monkeypatch):
    _patch_seeding(monkeypatch)
    dl = DataLocker(str(tmp_path / "pos.db"))
    core = PositionCore(dl)

    core.create_position(build_pos("a"))
    core.create_position(build_pos("b"))
    assert len(dl.positions.get_all_positions()) == 2

    core.delete_position("a")
    rows = dl.positions.get_all_positions()
    assert len(rows) == 1 and rows[0]["id"] == "b"

    core.clear_all_positions()
    assert dl.positions.get_all_positions() == []
    dl.db.close()
