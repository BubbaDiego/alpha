import importlib
import sys
import types

import pytest


def load_modules(monkeypatch):
    """Load AutoCore and phantom_workflow with Playwright stubbed."""
    pw_mod = types.ModuleType("playwright")
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = lambda: None
    # Minimal objects so phantom_workflow import succeeds
    sync_api.Page = object
    sync_api.BrowserContext = object
    pw_mod.sync_api = sync_api
    monkeypatch.setitem(sys.modules, "playwright", pw_mod)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)

    importlib.invalidate_caches()
    sys.modules.pop("auto_core.auto_core", None)
    sys.modules.pop("auto_core.phantom_workflow", None)
    pkg = sys.modules.get("auto_core")
    if pkg and hasattr(pkg, "phantom_workflow"):
        delattr(pkg, "phantom_workflow")

    auto_core_mod = importlib.import_module("auto_core.auto_core")
    pwf_mod = importlib.import_module("auto_core.phantom_workflow")
    return auto_core_mod.AutoCore, pwf_mod


class DummyPage:
    def __init__(self):
        self.filled = []
        self.clicked = []

    def fill(self, selector, value):
        self.filled.append((selector, value))

    def click(self, selector):
        self.clicked.append(selector)


def test_deposit_collateral(monkeypatch):
    AutoCore, pwf = load_modules(monkeypatch)
    events = []
    page = DummyPage()

    monkeypatch.setattr(AutoCore, "_launch_context", lambda self: ("pw", "ctx", page))
    monkeypatch.setattr(AutoCore, "_close", lambda self, pw, ctx: events.append("closed"))
    monkeypatch.setattr(pwf, "open_extension_popup", lambda *a, **k: None)
    monkeypatch.setattr(pwf, "connect_wallet", lambda p: events.append("connect"))
    monkeypatch.setattr(pwf, "approve_popup", lambda p: events.append("approve"))
    monkeypatch.setattr(pwf, "confirm_transaction", lambda p: events.append("confirm"))

    core = AutoCore(phantom_path="a", profile_dir="b")
    core.deposit_collateral(5.0)

    assert ("input[type=number]", "5.0") in page.filled
    assert "button:has-text('Deposit')" in page.clicked
    assert "connect" in events
    assert "approve" in events
    assert "confirm" in events
    assert "closed" in events


def test_withdraw_collateral(monkeypatch):
    AutoCore, pwf = load_modules(monkeypatch)
    events = []
    page = DummyPage()

    monkeypatch.setattr(AutoCore, "_launch_context", lambda self: ("pw", "ctx", page))
    monkeypatch.setattr(AutoCore, "_close", lambda self, pw, ctx: events.append("closed"))
    monkeypatch.setattr(pwf, "open_extension_popup", lambda *a, **k: None)
    monkeypatch.setattr(pwf, "connect_wallet", lambda p: events.append("connect"))
    monkeypatch.setattr(pwf, "approve_popup", lambda p: events.append("approve"))
    monkeypatch.setattr(pwf, "confirm_transaction", lambda p: events.append("confirm"))

    core = AutoCore(phantom_path="a", profile_dir="b")
    core.withdraw_collateral(2.0)

    assert ("input[type=number]", "2.0") in page.filled
    assert "button:has-text('Withdraw')" in page.clicked
    assert "connect" in events
    assert "approve" in events
    assert "confirm" in events
    assert "closed" in events
