import sys
import types

# Provide a minimal Playwright stub for import time
playwright_stub = types.ModuleType("playwright.sync_api")
playwright_stub.sync_playwright = lambda: None
playwright_stub.Page = object
playwright_stub.BrowserContext = object
sys.modules.setdefault("playwright", types.ModuleType("playwright"))
sys.modules.setdefault("playwright.sync_api", playwright_stub)

from auto_core.auto_core import AutoCore
import auto_core.auto_core as ac_module

class DummyPage:
    def goto(self, url):
        self.url = url

class DummyContext:
    def __init__(self):
        self.closed = False
        self.new_page_called = False
    def new_page(self):
        self.new_page_called = True
        return DummyPage()
    def close(self):
        self.closed = True

class DummyPW:
    def __init__(self, launch_stub):
        self.chromium = types.SimpleNamespace(launch_persistent_context=launch_stub)
        self.stopped = False
    def stop(self):
        self.stopped = True

class DummySync:
    def __init__(self, pw):
        self.pw = pw
    def start(self):
        return self.pw

def make_sync_playwright(launch_stub):
    return lambda: DummySync(DummyPW(launch_stub))

def test_launch_context_headless_false(monkeypatch):
    captured = {}
    def launch_stub(profile_dir, **kwargs):
        captured['kwargs'] = kwargs
        return DummyContext()
    monkeypatch.setattr(ac_module, 'sync_playwright', make_sync_playwright(launch_stub))
    open_called = {'val': False}
    monkeypatch.setattr(ac_module.pwf, 'open_extension_popup', lambda ctx, eid: open_called.update(val=True))

    ac = AutoCore('ext', 'profile', headless=False)
    pw, ctx, page = ac._launch_context()

    assert captured['kwargs']['headless'] is False
    assert '--headless=new' not in captured['kwargs']['args']
    assert open_called['val'] is False


def test_launch_context_headless_true(monkeypatch):
    captured = {}
    def launch_stub(profile_dir, **kwargs):
        captured['kwargs'] = kwargs
        return DummyContext()
    monkeypatch.setattr(ac_module, 'sync_playwright', make_sync_playwright(launch_stub))
    open_called = {'val': False}
    monkeypatch.setattr(ac_module.pwf, 'open_extension_popup', lambda ctx, eid: open_called.update(val=True))

    ac = AutoCore('ext', 'profile', headless=True, extension_id='ID')
    pw, ctx, page = ac._launch_context()

    assert captured['kwargs']['headless'] is True
    assert '--headless=new' in captured['kwargs']['args']
    assert open_called['val'] is True

