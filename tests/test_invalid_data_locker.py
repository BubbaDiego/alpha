import os
import pytest
from data.data_locker import DataLocker


def test_data_locker_handles_invalid_path(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    path = "/dev/null/test.db"  # invalid directory
    try:
        dl = DataLocker(path)
    except Exception as e:
        pytest.fail(f"DataLocker raised an exception: {e}")

    assert dl.get_all_tables_as_dict() == {}
    dl.db.close()
