import pytest
from data.data_locker import DataLocker


def disable_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)


def test_system_vars_default_row_main(tmp_path, monkeypatch):
    disable_seeding(monkeypatch)
    db_path = tmp_path / "sys.db"
    dl = DataLocker(str(db_path))
    cursor = dl.db.get_cursor()
    row = cursor.execute("SELECT id FROM system_vars").fetchone()
    dl.close()
    assert row["id"] == "main"
