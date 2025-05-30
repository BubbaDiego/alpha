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


def test_positions_heat_metric(monkeypatch):
    positions = [
        {"id": "p1", "heat_index": 10},
        {"id": "p2", "heat_index": 50},
    ]
    oc = OracleCore(DummyLocker(positions))
    monkeypatch.setattr(oc, "query_gpt", lambda msgs: msgs)

    avg = sum(p["heat_index"] for p in positions) / len(positions)
    monkeypatch.setattr(
        oc.handlers["positions"],
        "get_context",
        lambda: {"positions": positions, "avg_heat_index": avg},
    )

    messages = oc.ask("positions")
    ctx = json.loads(messages[1]["content"])

    assert ctx.get("avg_heat_index") == avg
    mods = ctx.get("strategy_modifiers", {})
    assert mods.get("heat_thresholds", {}).get("warning") == 30

