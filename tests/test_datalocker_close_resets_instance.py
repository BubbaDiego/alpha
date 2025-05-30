import os
import pytest
from data.data_locker import DataLocker


def _patch_seeding(monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)


def test_close_resets_singleton(tmp_path, monkeypatch):
    _patch_seeding(monkeypatch)
    DataLocker._instance = None
    path = str(tmp_path / "dl.db")

    first = DataLocker.get_instance(path)
    first_id = id(first)

    first.close()

    second = DataLocker.get_instance(path)
    assert id(second) != first_id

    second.db.close()

