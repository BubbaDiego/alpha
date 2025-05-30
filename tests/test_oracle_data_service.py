import importlib.util
from pathlib import Path


def load_module():
    base = Path(__file__).resolve().parents[1]
    path = base / "oracle_core" / "oracle_data_service.py"
    spec = importlib.util.spec_from_file_location("oracle_core.oracle_data_service", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_fetch_system_includes_new_fields():
    mod = load_module()

    class DummyDL:
        def get_last_update_times(self):
            return {"t": 1}

        def get_death_log_entries(self, limit=20):
            return ["d1"]

        def get_system_alerts(self, limit=20):
            return ["a1"]

    ods = mod.OracleDataService(DummyDL())
    data = ods.fetch_system()
    assert data["last_update_times"] == {"t": 1}
    assert data["death_log"] == ["d1"]
    assert data["system_alerts"] == ["a1"]
