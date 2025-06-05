import sys
import types
import subprocess

import pytest


def _prepare_sonic_env(monkeypatch):
    """Install minimal stubs so ``sonic_app`` imports without heavy deps."""
    class DummyFlask:
        def __init__(self, *a, **k):
            self.config = {}
            self.view_functions = {}
        def route(self, *a, **k):
            def decorator(func):
                self.view_functions[func.__name__] = func
                return func
            return decorator
        def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
            if view_func:
                self.view_functions[endpoint or view_func.__name__] = view_func
        def context_processor(self, func):
            return func
        def add_template_filter(self, func, name=None):
            pass
        def register_blueprint(self, bp, **k):
            pass
        def app_context(self):
            class Ctx:
                def __enter__(self_inner):
                    return self
                def __exit__(self_inner, exc_type, exc, tb):
                    pass
            return Ctx()
        def run(self, *a, **k):  # pragma: no cover - never executed
            raise RuntimeError('Flask not installed')
    flask_stub = types.ModuleType('flask')
    flask_stub.Flask = DummyFlask
    flask_stub.redirect = lambda loc: loc
    flask_stub.url_for = lambda endpoint, **kwargs: endpoint
    flask_stub.current_app = types.SimpleNamespace()
    flask_stub.jsonify = lambda *a, **k: {}
    monkeypatch.setitem(sys.modules, 'flask', flask_stub)
    monkeypatch.setitem(sys.modules, 'flask_socketio', types.SimpleNamespace(SocketIO=lambda *a, **k: None))

    # Import global stubs from conftest (rich_logger etc.)
    import tests.conftest  # noqa: F401

    core_logging = types.ModuleType('core.logging')
    class DummyLog:
        logger = types.SimpleNamespace(setLevel=lambda level: None)
        def __getattr__(self, name):
            def noop(*a, **k):
                pass
            return noop
    core_logging.log = DummyLog()
    core_logging.configure_console_log = lambda debug=False: None
    monkeypatch.setitem(sys.modules, 'core.logging', core_logging)
    core_imports = types.ModuleType('core.core_imports')
    core_imports.log = core_logging.log
    core_imports.configure_console_log = core_logging.configure_console_log
    core_imports.DB_PATH = ''
    core_imports.BASE_DIR = ''
    core_imports.ALERT_THRESHOLDS_PATH = ''
    core_imports.retry_on_locked = lambda: (lambda f: f)
    monkeypatch.setitem(sys.modules, 'core.core_imports', core_imports)

    DataLocker = type('DataLocker', (), {
        '__init__': lambda self, path: None,
        'system': types.SimpleNamespace(get_var=lambda *a, **k: {}, set_var=lambda *a, **k: None),
        'db': types.SimpleNamespace(get_cursor=lambda: None),
    })
    monkeypatch.setitem(sys.modules, 'data.data_locker', types.SimpleNamespace(DataLocker=DataLocker))
    SystemCore = type('SystemCore', (), {
        '__init__': lambda self, dl: None,
        'get_active_profile': lambda self: None,
    })
    monkeypatch.setitem(sys.modules, 'system.system_core', types.SimpleNamespace(SystemCore=SystemCore))
    monkeypatch.setitem(sys.modules, 'monitor.monitor_core', types.SimpleNamespace(MonitorCore=lambda: None))
    monkeypatch.setitem(sys.modules, 'cyclone.cyclone_engine', types.SimpleNamespace(Cyclone=lambda *a, **k: None))
    monkeypatch.setitem(sys.modules, 'utils.template_filters', types.SimpleNamespace(short_datetime=lambda x: 'time'))

    bp_modules = {
        'app.positions_bp': 'positions_bp',
        'app.alerts_bp': 'alerts_bp',
        'app.prices_bp': 'prices_bp',
        'app.dashboard_bp': 'dashboard_bp',
        'portfolio.portfolio_bp': 'portfolio_bp',
        'sonic_labs.sonic_labs_bp': 'sonic_labs_bp',
        'cyclone.cyclone_bp': 'cyclone_bp',
        'routes.theme_routes': 'theme_bp',
        'app.system_bp': 'system_bp',
        'settings.settings_bp': 'settings_bp',
        'gpt.chat_gpt_bp': 'chat_gpt_bp',
        'gpt.gpt_bp': 'gpt_bp',
        'trader_core.trader_bp': 'trader_bp',
    }
    for mod_name, attr in bp_modules.items():
        mod = types.ModuleType(mod_name)
        setattr(mod, attr, object())
        monkeypatch.setitem(sys.modules, mod_name, mod)


def test_launch_route_opens_browser(monkeypatch):
    _prepare_sonic_env(monkeypatch)
    import sonic_app

    sonic_app.PERPETUAL_TOKENS = {'BTC': {'id': 1}}
    popen_args = []
    monkeypatch.setattr(subprocess, 'Popen', lambda args: popen_args.append(args))

    result = sonic_app.launch_jupiter_position('Default', 'BTC')
    assert result == 'Launching BTC in Default'
    assert popen_args == [[
        'C:/Program Files/Google/Chrome/Application/chrome.exe',
        '--profile-directory=Default',
        'https://jup.ag/perpetuals/BTC',
    ]]

