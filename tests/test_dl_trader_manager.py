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
    assert m.get_trader_by_name("Alice") is not None

    m.update_trader("Alice", {"mood": "sad"})
    assert m.get_trader_by_name("Alice")["mood"] == "sad"

    m.create_trader({"name": "Bob"})
    assert len(m.list_traders()) == 2

    m.delete_trader("Alice")
    names = [t["name"] for t in m.list_traders()]
    assert "Alice" not in names and "Bob" in names


def test_delete_nonexistent_trader_returns_false(dl):
    m = dl.traders
    result = m.delete_trader("Ghost")
    assert result is False


def test_defaults_added_on_load(dl):
    m = dl.traders

    m.create_trader({"name": "Carol"})
    trader = m.get_trader_by_name("Carol")

    assert trader["initial_collateral"] == 0.0
    assert "born_on" in trader

    listed = [t for t in m.list_traders() if t["name"] == "Carol"][0]
    assert listed["initial_collateral"] == 0.0
    assert listed["born_on"] == trader["born_on"]
