import builtins
import sys
import types

dummy_rich = types.ModuleType("rich")
dummy_console = types.ModuleType("rich.console")
dummy_text = types.ModuleType("rich.text")

class _Console:
    def print(self, *args, **kwargs):
        pass

dummy_console.Console = _Console
dummy_text.Text = str
dummy_rich.console = dummy_console
dummy_rich.text = dummy_text
sys.modules.setdefault("rich", dummy_rich)
sys.modules.setdefault("rich.console", dummy_console)
sys.modules.setdefault("rich.text", dummy_text)

import pytest

try:
    import launch_pad
except Exception:
    pytest.skip("launch_pad module unavailable", allow_module_level=True)


def test_operations_menu_recover(monkeypatch):
    called = {"recover": False}

    class DummyDB:
        def recover_database(self):
            called["recover"] = True

    class DummyLocker:
        def __init__(self, path):
            self.db = DummyDB()

        def initialize_database(self):
            pass

        def _seed_modifiers_if_empty(self):
            pass

        def _seed_wallets_if_empty(self):
            pass

        def _seed_thresholds_if_empty(self):
            pass

        def _seed_alerts_if_empty(self):
            pass

        def close(self):
            pass

    inputs = iter(["3", "", "b"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    monkeypatch.setattr(launch_pad, "clear_screen", lambda: None)
    monkeypatch.setattr(launch_pad, "DataLocker", DummyLocker)

    launch_pad.operations_menu()

    assert called["recover"] is True
