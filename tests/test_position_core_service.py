import sys
import types

import pytest

from positions.position_core_service import PositionCoreService


class DummyDB:
    def __init__(self):
        self.positions = {}

    def get_cursor(self):
        return self

    def execute(self, sql, params=()):
        if sql.startswith("UPDATE positions SET hedge_buddy_id = NULL"):
            target = params[0]
            for p in self.positions.values():
                if p.get("hedge_buddy_id") == target:
                    p["hedge_buddy_id"] = None
        return self

    def commit(self):
        pass

    def close(self):
        pass


class DummyPositions:
    def __init__(self, db: DummyDB):
        self.db = db

    def create_position(self, pos):
        self.db.positions[pos["id"]] = pos

    def get_all_positions(self):
        return list(self.db.positions.values())

    def delete_position(self, pos_id):
        self.db.positions.pop(pos_id, None)

    def get_position_by_id(self, pos_id):
        return self.db.positions.get(pos_id)


class MockDataLocker:
    def __init__(self):
        self.db = DummyDB()
        self.positions = DummyPositions(self.db)
        self.alert_list = []

    def get_alerts(self):
        return self.alert_list

    def delete_position(self, pos_id):
        self.positions.delete_position(pos_id)


class DummyAlertEvaluator:
    called_with = None

    def __init__(self, config, dl):
        self.config = config
        self.dl = dl

    def update_alert_for_position(self, pos):
        DummyAlertEvaluator.called_with = pos


class DummyAlertController:
    deleted = []

    def delete_alert(self, alert_id):
        DummyAlertController.deleted.append(alert_id)
        return True


def test_update_position_and_alert(monkeypatch):
    dl = MockDataLocker()

    # patch AlertEvaluator module
    evaluator_module = types.ModuleType("alert_core.alert_evaluator")
    evaluator_module.AlertEvaluator = DummyAlertEvaluator
    monkeypatch.setitem(sys.modules, "alert_core.alert_evaluator", evaluator_module)

    service = PositionCoreService(dl)
    pos = {"id": "pos1", "asset_type": "BTC", "position_type": "LONG"}

    service.update_position_and_alert(pos)

    stored = dl.positions.get_all_positions()
    assert len(stored) == 1
    assert stored[0]["id"] == "pos1"
    assert DummyAlertEvaluator.called_with == pos


def test_delete_position_and_cleanup(monkeypatch):
    dl = MockDataLocker()

    # existing positions
    dl.positions.create_position({"id": "pos1", "asset_type": "BTC", "position_type": "LONG"})
    dl.positions.create_position({"id": "pos2", "asset_type": "BTC", "position_type": "SHORT", "hedge_buddy_id": "pos1"})

    # alerts referencing positions
    dl.alert_list = [
        {"id": "a1", "position_reference_id": "pos1"},
        {"id": "a2", "position_reference_id": "pos2"},
    ]

    controller_module = types.ModuleType("alert_core.alert_controller")
    controller_module.AlertController = lambda: DummyAlertController()
    monkeypatch.setitem(sys.modules, "alert_core.alert_controller", controller_module)

    service = PositionCoreService(dl)
    DummyAlertController.deleted.clear()

    service.delete_position_and_cleanup("pos1")

    # only alert a1 should be deleted
    assert DummyAlertController.deleted == ["a1"]

    remaining = dl.positions.get_all_positions()
    assert len(remaining) == 1
    assert remaining[0]["id"] == "pos2"
    assert remaining[0].get("hedge_buddy_id") is None
