import sys
import types
import importlib
import pytest


class DummyPM:
    def __init__(self, *a, **k):
        self.called = []
        self.page = "page"

    async def launch_browser(self):
        self.called.append("launch_browser")

    async def connect_wallet(self, **kwargs):
        self.called.append(("connect_wallet", kwargs))

    async def unlock_phantom(self, password):
        self.called.append(("unlock_phantom", password))

    async def close(self):
        self.called.append("close")


class DummyJP:
    def __init__(self, *_):
        self.called = []

    async def select_position_type(self, typ):
        self.called.append(("select_position_type", typ))


pm_mod = types.ModuleType("jupiter_core.phantom_manager")
pm_mod.PhantomManager = DummyPM
sys.modules.setdefault("jupiter_core.phantom_manager", pm_mod)

jp_mod = types.ModuleType("jupiter_core.jupiter_perps_flow")
jp_mod.JupiterPerpsFlow = DummyJP
sys.modules.setdefault("jupiter_core.jupiter_perps_flow", jp_mod)

# Stub out playwright modules that may be imported by other modules
playwright_async = types.ModuleType("playwright.async_api")
playwright_async.async_playwright = lambda: None
playwright_async.Page = object
playwright_async.BrowserContext = object
playwright_async.Error = Exception
sys.modules.setdefault("playwright.async_api", playwright_async)

playwright_sync = types.ModuleType("playwright.sync_api")
playwright_sync.Error = Exception
sys.modules.setdefault("playwright.sync_api", playwright_sync)

from jupiter_modular.engine.jupiter_engine_core import JupiterEngineCore


@pytest.mark.asyncio
async def test_step_modules_execute():
    engine = JupiterEngineCore("ext", "url", phantom_password="pw")
    await engine.launch()

    modules = [
        importlib.import_module("jupiter_modular.steps.auto_connect_wallet"),
        importlib.import_module("jupiter_modular.steps.auto_unlock_wallet"),
        importlib.import_module("jupiter_modular.steps.auto_set_position_type"),
    ]

    for mod in modules:
        await mod.run(engine)

    pm: DummyPM = engine.pm  # type: ignore
    jp: DummyJP = engine.jp  # type: ignore

    assert ("connect_wallet", {
        "dapp_url": engine.dapp_url,
        "phantom_password": engine.phantom_password,
    }) in pm.called
    assert ("unlock_phantom", engine.phantom_password) in pm.called
    assert ("select_position_type", "long") in jp.called

    await engine.close()
