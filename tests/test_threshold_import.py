import json
from datetime import datetime
from data.data_locker import DataLocker
from data.dl_thresholds import DLThresholdManager
from data.models import AlertThreshold


def setup_dl(tmp_path, monkeypatch):
    monkeypatch.setattr(DataLocker, "_seed_modifiers_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_wallets_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_thresholds_if_empty", lambda self: None)
    monkeypatch.setattr(DataLocker, "_seed_alerts_if_empty", lambda self: None)
    dl = DataLocker(str(tmp_path / "thr.db"))
    return dl


def test_import_replaces_old_thresholds(tmp_path, monkeypatch):
    dl = setup_dl(tmp_path, monkeypatch)
    mgr = DLThresholdManager(dl.db)

    t1 = AlertThreshold("t1", "A", "C", "k", "ABOVE", 1, 2, 3)
    t2 = AlertThreshold("t2", "B", "C", "k", "ABOVE", 1, 2, 3)
    mgr.insert(t1)
    mgr.insert(t2)

    new = [
        t1.to_dict(),
        {
            "id": "t3",
            "alert_type": "C",
            "alert_class": "C",
            "metric_key": "k",
            "condition": "ABOVE",
            "low": 1,
            "medium": 2,
            "high": 3,
            "enabled": True,
            "last_modified": datetime.utcnow().isoformat(),
            "low_notify": "",
            "medium_notify": "",
            "high_notify": "",
        },
    ]

    json_path = tmp_path / "thresh.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new, f)

    count = mgr.import_from_json(str(json_path))
    ids = {t.id for t in mgr.get_all()}

    assert count == 2
    assert ids == {"t1", "t3"}


def test_changes_export_to_json(tmp_path, monkeypatch):
    json_path = tmp_path / "saved.json"
    import data.dl_thresholds as dl_thr
    monkeypatch.setattr(dl_thr, "ALERT_THRESHOLDS_JSON_PATH", str(json_path))
    original_export = dl_thr.DLThresholdManager.export_to_json

    def export_with_path(self, path=str(json_path)):
        return original_export(self, path)

    monkeypatch.setattr(dl_thr.DLThresholdManager, "export_to_json", export_with_path)
    dl = setup_dl(tmp_path, monkeypatch)
    mgr = DLThresholdManager(dl.db)

    t1 = AlertThreshold("t1", "A", "C", "k", "ABOVE", 1, 2, 3)
    mgr.insert(t1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["source"] == "db"
    assert len(data["thresholds"]) == 1
    assert data["thresholds"][0]["id"] == "t1"

    mgr.update("t1", {"low": 5})
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["thresholds"][0]["low"] == 5

    mgr.delete("t1")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["thresholds"] == []
