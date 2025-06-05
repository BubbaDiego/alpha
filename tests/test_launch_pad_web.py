import builtins
import sys
import types

import pytest

# Provide minimal rich stubs to satisfy launch_pad import
_dummy_rich = types.ModuleType("rich")
_dummy_console = types.ModuleType("rich.console")
_dummy_text = types.ModuleType("rich.text")
_dummy_panel = types.ModuleType("rich.panel")
_dummy_prompt = types.ModuleType("rich.prompt")
_dummy_table = types.ModuleType("rich.table")

class _Console:
    def print(self, *a, **k):
        pass

_dummy_console.Console = _Console
_dummy_text.Text = str

class _Panel:
    def __init__(self, *a, **k):
        pass

class _Prompt:
    @staticmethod
    def ask(*a, **k):
        return ""

class _Table:
    def __init__(self, *a, **k):
        pass
    def add_row(self, *a, **k):
        pass

_dummy_panel.Panel = _Panel
_dummy_prompt.Prompt = _Prompt
_dummy_table.Table = _Table

_dummy_rich.console = _dummy_console
_dummy_rich.text = _dummy_text
_dummy_rich.panel = _dummy_panel
_dummy_rich.prompt = _dummy_prompt
_dummy_rich.table = _dummy_table
sys.modules.setdefault("rich", _dummy_rich)
sys.modules.setdefault("rich.console", _dummy_console)
sys.modules.setdefault("rich.text", _dummy_text)
sys.modules.setdefault("rich.panel", _dummy_panel)
sys.modules.setdefault("rich.prompt", _dummy_prompt)
sys.modules.setdefault("rich.table", _dummy_table)

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
