import importlib
import sys
import types


# Stub out optional jupiter_integration modules so the import checks succeed
for _name in [
    "jupiter_integration.playwright.phantom_manager",
    "jupiter_integration.playwright.solflare_manager",
    "jupiter_integration.playwright.jupiter_perps_flow",
    "jupiter_integration.anchorpy_client.jupiter_order",
    "jupiter_integration.console_apps.phantom_console_app",
    "jupiter_integration.console_apps.solflare_console_app",
]:
    sys.modules.setdefault(_name, types.ModuleType(_name))


def test_playwright_modules_load():
    importlib.import_module('jupiter_integration.playwright.phantom_manager')
    importlib.import_module('jupiter_integration.playwright.solflare_manager')
    importlib.import_module('jupiter_integration.playwright.jupiter_perps_flow')


def test_anchorpy_client_modules_load():
    importlib.import_module('jupiter_integration.anchorpy_client.jupiter_order')


def test_console_apps_modules_load():
    importlib.import_module('jupiter_integration.console_apps.phantom_console_app')
    importlib.import_module('jupiter_integration.console_apps.solflare_console_app')

