import importlib.util
from pathlib import Path


def load_module():
    base = Path(__file__).resolve().parents[1]
    path = base / "oracle_core" / "positions_topic_handler.py"
    spec = importlib.util.spec_from_file_location("oracle_core.positions_topic_handler", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_get_context_includes_avg_heat_index(monkeypatch):
    mod = load_module()
    handler = mod.PositionsTopicHandler(None)
    positions = [
        {
            "size": 1.0,
            "value": 100.0,
            "collateral": 50.0,
            "leverage": 2.0,
            "travel_percent": 5.0,
            "heat_index": 10.0,
        },
        {
            "size": 1.0,
            "value": 50.0,
            "collateral": 25.0,
            "leverage": 1.0,
            "travel_percent": 2.5,
            "heat_index": 20.0,
        },
    ]
    monkeypatch.setattr(handler.data_service, "fetch_positions", lambda: positions)
    context = handler.get_context()
    assert context[handler.output_key] == positions
    assert context["avg_heat_index"] == 15.0
