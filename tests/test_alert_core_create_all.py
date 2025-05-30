import asyncio

from data.data_locker import DataLocker
from alert_core.alert_core import AlertCore


def test_create_all_alerts_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)

    dl = DataLocker(str(tmp_path / "core.db"))
    core = AlertCore(dl)

    # Should complete without raising exceptions
    asyncio.run(core.create_all_alerts())

    dl.db.close()
