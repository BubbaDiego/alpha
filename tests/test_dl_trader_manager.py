import pytest
from data.data_locker import DataLocker


def _disable_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)


@pytest.fixture

def dl(tmp_path, monkeypatch):
    _disable_seeding(monkeypatch)
    locker = DataLocker(str(tmp_path / "trader.db"))
    yield locker
    locker.db.close()


def test_crud_flow(dl):
    m = dl.traders

    m.create_trader({"name": "Alice", "mood": "happy", "wallet_balance": 10})
    alice = m.get_trader_by_name("Alice")
    assert alice is not None
    assert "born_on" in alice and "initial_collateral" in alice
    from datetime import datetime
    datetime.fromisoformat(alice["born_on"])
    assert alice["initial_collateral"] == 10

    m.update_trader("Alice", {"mood": "sad"})
    assert m.get_trader_by_name("Alice")["mood"] == "sad"

    m.create_trader({"name": "Bob", "wallet_balance": 5})
    bob = m.get_trader_by_name("Bob")
    assert len(m.list_traders()) == 2
    assert "born_on" in bob and "initial_collateral" in bob
    datetime.fromisoformat(bob["born_on"])
    assert bob["initial_collateral"] == 5

    m.delete_trader("Alice")
    names = [t["name"] for t in m.list_traders()]
    assert "Alice" not in names and "Bob" in names


def test_delete_nonexistent_trader_returns_false(dl):
    m = dl.traders
    result = m.delete_trader("Ghost")
    assert result is False
