import builtins
import sys
import types

# Importing tests.conftest ensures the global ``rich`` stub is loaded if
# the actual library is unavailable. The variable itself isn't used here.
import tests.conftest  # noqa: F401

# Stub core.logging so ``configure_console_log`` and ``log`` usage inside
# :mod:`launch_pad` do not require the full implementation during import.
core_logging_stub = types.ModuleType("core.logging")

class _DummyLog:
    logger = types.SimpleNamespace(setLevel=lambda *a, **k: None)

    def __getattr__(self, _):
        def noop(*a, **k):
            pass

        return noop

core_logging_stub.log = _DummyLog()
core_logging_stub.configure_console_log = lambda *a, **k: None
sys.modules.setdefault("core.logging", core_logging_stub)

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
