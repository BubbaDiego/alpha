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

    m.create_trader({"name": "Alice", "mood": "happy"})
    alice = m.get_trader_by_name("Alice")
    assert alice is not None
    assert "born_on" in alice
    assert alice["initial_collateral"] == 0.0

    m.update_trader("Alice", {"mood": "sad"})
    assert m.get_trader_by_name("Alice")["mood"] == "sad"

    m.create_trader({"name": "Bob"})
    traders = m.list_traders()
    assert len(traders) == 2
    for t in traders:
        assert "born_on" in t

    m.delete_trader("Alice")
    names = [t["name"] for t in m.list_traders()]
    assert "Alice" not in names and "Bob" in names


def test_delete_nonexistent_trader_returns_false(dl):
    m = dl.traders
    result = m.delete_trader("Ghost")
    assert result is False
