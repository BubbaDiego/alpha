import importlib
from types import SimpleNamespace

import pytest


def test_cyclone_loads_json_when_db_missing(tmp_path, monkeypatch):
    dummy_config = {"dummy": True}

    # Redirect DB_PATH to a temporary location
    import core.constants as constants
    tmp_db = tmp_path / "temp.db"
    monkeypatch.setattr(constants, "DB_PATH", tmp_db)

    # Reload engine to use patched DB_PATH
    ce = importlib.reload(importlib.import_module("cyclone.cyclone_engine"))

    # Force missing config in DB
    monkeypatch.setattr(ce.global_data_locker.system, "get_var", lambda k: None)

    store = {}
    monkeypatch.setattr(ce.global_data_locker.system, "set_var", lambda k, v: store.setdefault(k, v))

    # Stub file loader
    def fake_loader(dl):
        dl.system.set_var("alert_thresholds", dummy_config)
        return dummy_config

    monkeypatch.setattr(ce, "load_alert_thresholds_from_file", fake_loader)

    engine = ce.Cyclone()

    assert engine.config == dummy_config
    assert store["alert_thresholds"] == dummy_config
