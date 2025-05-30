import importlib


def test_playwright_modules_load():
    importlib.import_module('jupiter_integration.playwright.phantom_manager')
    importlib.import_module('jupiter_integration.playwright.solflare_manager')
    importlib.import_module('jupiter_integration.playwright.jupiter_perps_flow')


def test_anchorpy_client_modules_load():
    importlib.import_module('jupiter_integration.anchorpy_client.jupiter_order')


def test_console_apps_modules_load():
    importlib.import_module('jupiter_integration.console_apps.phantom_console_app')
    importlib.import_module('jupiter_integration.console_apps.solflare_console_app')

