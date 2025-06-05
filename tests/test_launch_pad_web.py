import builtins
import sys
import types

import pytest

# Import tests.conftest to ensure the global ``rich`` stub is available when the
# real library isn't installed. The module itself isn't referenced directly.
import tests.conftest  # noqa: F401

# Stub heavy dependencies referenced by launch_pad at import time
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

sys.modules.setdefault("cyclone_app", types.ModuleType("cyclone_app"))
sys.modules["cyclone_app"].main = lambda: None
sys.modules.setdefault("monitor.operations_monitor", types.SimpleNamespace(OperationsMonitor=object))

sys.modules.setdefault("test_core", types.ModuleType("test_core"))
sys.modules["test_core"].TestCore = object
sys.modules.setdefault("data.data_locker", types.ModuleType("data.data_locker"))
sys.modules["data.data_locker"].DataLocker = object

sys.modules.setdefault("utils.startup_service", types.ModuleType("utils.startup_service"))
sys.modules["utils.startup_service"].StartUpService = types.SimpleNamespace(run_all=lambda: None)
sys.modules.setdefault("scripts.verify_all_tables_exist", types.ModuleType("scripts.verify_all_tables_exist"))
sys.modules["scripts.verify_all_tables_exist"].verify_all_tables_exist = lambda: 0
sys.modules.setdefault("monitor.sonic_monitor", types.ModuleType("monitor.sonic_monitor"))

try:
    import launch_pad
except Exception:
    pytest.skip("launch_pad module unavailable", allow_module_level=True)


def _run_launch(func, monkeypatch):
    urls = []
    popen_cmds = []
    monkeypatch.setattr(builtins, "input", lambda _: "")
    monkeypatch.setattr(launch_pad.time, "sleep", lambda _: None)
    monkeypatch.setattr(launch_pad.webbrowser, "open", lambda url: urls.append(url))
    monkeypatch.setattr(launch_pad.subprocess, "Popen", lambda args: popen_cmds.append(args))
    monkeypatch.setattr(launch_pad.log, "print_dashboard_link", lambda *a, **k: None)
    func()
    return urls, popen_cmds


def test_launch_sonic_web_opens_browser(monkeypatch):
    urls, popen_cmds = _run_launch(launch_pad.launch_sonic_web, monkeypatch)
    assert urls == ["http://127.0.0.1:5000"]
    assert popen_cmds == [[sys.executable, "sonic_app.py"]]


def test_launch_trader_cards_opens_browser(monkeypatch):
    urls, popen_cmds = _run_launch(launch_pad.launch_trader_cards, monkeypatch)
    assert urls == ["http://127.0.0.1:5000/trader/cards"]
    assert popen_cmds == [[sys.executable, "sonic_app.py"]]
