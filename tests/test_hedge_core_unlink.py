import pytest

from data.data_locker import DataLocker
from hedge_core.hedge_core import HedgeCore


@pytest.fixture
def dl(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)
    locker = DataLocker(":memory:")
    yield locker
    locker.db.close()


def setup_hedged_positions(dl):
    dl.positions.create_position({
        "id": "long1",
        "asset_type": "ETH",
        "position_type": "long",
        "wallet_name": "WalletA",
    })
    dl.positions.create_position({
        "id": "short1",
        "asset_type": "ETH",
        "position_type": "short",
        "wallet_name": "WalletA",
    })
    HedgeCore(dl).link_hedges()


def test_unlink_hedges_clears_ids(dl):
    setup_hedged_positions(dl)
    core = HedgeCore(dl)
    core.unlink_hedges()
    positions = dl.positions.get_all_positions()
    assert all(p["hedge_buddy_id"] is None for p in positions)
