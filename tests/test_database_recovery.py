import sqlite3
import pytest
import os

from data.data_locker import DataLocker


def test_recover_malformed_db(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    db_path = tmp_path / "test.db"
    dl = DataLocker(str(db_path))

    orig_get_cursor = dl.db.get_cursor

    def failing_cursor():
        if not hasattr(failing_cursor, "called"):
            failing_cursor.called = True
            raise sqlite3.DatabaseError("database disk image is malformed")
        return orig_get_cursor()

    called = {"recover": False}
    orig_recover = dl.db.recover_database

    def spy_recover():
        called["recover"] = True
        orig_recover()

    monkeypatch.setattr(dl.db, "get_cursor", failing_cursor)
    monkeypatch.setattr(dl.db, "recover_database", spy_recover)

    positions = dl.positions.get_all_positions()

    assert positions == []
    assert called["recover"] is True
    assert os.path.exists(db_path)
    dl.db.close()
