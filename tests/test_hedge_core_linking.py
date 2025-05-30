import pytest

from data.data_locker import DataLocker
from hedge_core.hedge_core import HedgeCore


@pytest.fixture
def dl(monkeypatch):
    # Skip default modifier seeding to keep tests self-contained
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)
    locker = DataLocker(":memory:")
    yield locker
    locker.db.close()


def test_link_hedges_assigns_same_id_for_long_and_short(dl):
    long_pos = {
        "id": "long1",
        "asset_type": "BTC",
        "position_type": "long",
        "wallet_name": "TestWallet",
    }
    short_pos = {
        "id": "short1",
        "asset_type": "BTC",
        "position_type": "short",
        "wallet_name": "TestWallet",
    }

    dl.positions.create_position(long_pos)
    dl.positions.create_position(short_pos)

    core = HedgeCore(dl)
    groups = core.link_hedges()
    assert len(groups) == 1

    hedge_id = groups[0][0]["hedge_buddy_id"]
    assert hedge_id
    assert all(p["hedge_buddy_id"] == hedge_id for p in groups[0])

    db_positions = dl.positions.get_all_positions()
    ids = {p["hedge_buddy_id"] for p in db_positions}
    assert ids == {hedge_id}
