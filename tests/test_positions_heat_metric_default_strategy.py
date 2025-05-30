import json
from oracle_core.oracle_core import OracleCore

class DummyPositions:
    def __init__(self, positions):
        self._positions = positions
    def get_all_positions(self):
        return self._positions

class DummyLocker:
    def __init__(self, positions):
        self.positions = DummyPositions(positions)
    def get_last_update_times(self):
        return {}


def test_positions_default_strategy(monkeypatch):
    positions = [
        {"id": "p1", "heat_index": 20},
        {"id": "p2", "heat_index": 40},
    ]
    oc = OracleCore(DummyLocker(positions))
    # prevent actual OpenAI calls
    monkeypatch.setattr(oc, "query_gpt", lambda msgs: msgs)

    messages = oc.ask("positions")
    ctx = json.loads(messages[1]["content"])

    # avg_heat_index should be present and computed
    assert "avg_heat_index" in ctx
    assert ctx["avg_heat_index"] == 30

    # heat_control modifiers should be automatically applied
    mods = ctx.get("strategy_modifiers", {})
    assert mods.get("priority_metric") == "avg_heat_index"
    assert mods.get("heat_thresholds", {}).get("warning") == 30
