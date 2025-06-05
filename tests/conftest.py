import sys
import os
import types
import logging
import asyncio

# Automatically fix sys.path for tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Stub rich if not installed so launch_pad and TestCore import cleanly
if "rich" not in sys.modules:
    rich_stub = types.ModuleType("rich")
    rich_console = types.ModuleType("rich.console")
    rich_text = types.ModuleType("rich.text")
    rich_panel = types.ModuleType("rich.panel")
    rich_prompt = types.ModuleType("rich.prompt")
    rich_table = types.ModuleType("rich.table")

    class DummyConsole:
        def print(self, *a, **k):
            pass

    class DummyPanel:
        def __init__(self, *a, **k):
            pass

    class DummyPrompt:
        @staticmethod
        def ask(*a, **k):
            return ""

    class DummyTable:
        def __init__(self, *a, **k):
            pass

    rich_console.Console = DummyConsole
    rich_text.Text = str
    rich_panel.Panel = DummyPanel
    rich_prompt.Prompt = DummyPrompt
    rich_table.Table = DummyTable
    rich_stub.console = rich_console
    rich_stub.text = rich_text
    rich_stub.panel = rich_panel
    rich_stub.prompt = rich_prompt
    rich_stub.table = rich_table

    sys.modules.setdefault("rich", rich_stub)
    sys.modules.setdefault("rich.console", rich_console)
    sys.modules.setdefault("rich.text", rich_text)
    sys.modules.setdefault("rich.panel", rich_panel)
    sys.modules.setdefault("rich.prompt", rich_prompt)
    sys.modules.setdefault("rich.table", rich_table)

# Stub rich_logger and winsound to avoid optional deps during tests
rich_logger_stub = types.ModuleType("utils.rich_logger")
class RichLogger:
    def __getattr__(self, _):
        def no_op(*a, **k):
            pass
        return no_op
class ModuleFilter(logging.Filter):
    def filter(self, record):
        return True
rich_logger_stub.RichLogger = RichLogger
rich_logger_stub.ModuleFilter = ModuleFilter
sys.modules.setdefault("utils.rich_logger", rich_logger_stub)
sys.modules.setdefault("winsound", types.ModuleType("winsound"))

# Stub jsonschema if not installed
if "jsonschema" not in sys.modules:
    jsonschema_stub = types.ModuleType("jsonschema")
    class ValidationError(Exception):
        pass
    def validate(instance=None, schema=None):
        return True
    jsonschema_stub.validate = validate
    jsonschema_stub.exceptions = types.SimpleNamespace(ValidationError=ValidationError)
    jsonschema_stub.IS_STUB = True
    sys.modules["jsonschema"] = jsonschema_stub

# Stub pydantic if not installed
if "pydantic" not in sys.modules:
    pydantic_stub = types.ModuleType("pydantic")
    class BaseModel:
        pass
    def Field(*a, **k):
        return None
    pydantic_stub.BaseModel = BaseModel
    pydantic_stub.Field = Field
    sys.modules["pydantic"] = pydantic_stub

# Stub positions.hedge_manager to avoid circular import during DataLocker init
hedge_stub = types.ModuleType("positions.hedge_manager")
class HedgeManager:
    def __init__(self, *a, **k):
        pass
    def get_hedges(self):
        return []
    @staticmethod
    def find_hedges(db_path=None):
        return []
hedge_stub.HedgeManager = HedgeManager
sys.modules.setdefault("positions.hedge_manager", hedge_stub)

# Stub flask current_app to avoid optional dependency
flask_stub = types.ModuleType("flask")


class DummyBlueprint:
    def __init__(self, name, import_name, url_prefix="", **kwargs):
        self.name = name
        self.import_name = import_name
        self.url_prefix = url_prefix
        self.routes = {}

    def route(self, rule, methods=None):
        methods = methods or ["GET"]

        def decorator(func):
            self.routes.setdefault(rule, {})
            for m in methods:
                self.routes[rule][m] = func
            return func

        return decorator

    def add_app_template_filter(self, func, name=None):  # pragma: no cover - stub
        pass


class DummyResponse:
    def __init__(self, data=b"", json_data=None, status_code=200):
        self.status_code = status_code
        self.data = data if isinstance(data, bytes) else str(data).encode()
        self._json = json_data

    def get_json(self):
        return self._json


def _result_to_response(result):
    status = 200
    body = result
    if isinstance(result, tuple):
        body = result[0]
        if len(result) > 1:
            status = result[1]
    if isinstance(body, DummyResponse):
        if status != 200:
            body.status_code = status
        return body
    if isinstance(body, dict):
        return DummyResponse(json_data=body, status_code=status)
    return DummyResponse(data=str(body), status_code=status)


class DummyFlask:
    def __init__(self, *a, **k):
        self.config = {}
        self.routes = {}
        self.logger = types.SimpleNamespace(error=lambda *a, **k: None)

    def register_blueprint(self, bp, url_prefix=""):
        prefix = url_prefix or getattr(bp, "url_prefix", "")
        for rule, views in getattr(bp, "routes", {}).items():
            for method, func in views.items():
                path = prefix + rule

                def wrapper(*a, __func=func, **k):
                    mod = sys.modules.get(bp.import_name)
                    if mod is not None:
                        globals_map = getattr(__func, "__globals__", {})
                        for name, val in list(globals_map.items()):
                            if hasattr(mod, name):
                                globals_map[name] = getattr(mod, name)
                            elif hasattr(val, "__module__"):
                                m = sys.modules.get(val.__module__)
                                if m and hasattr(m, name):
                                    globals_map[name] = getattr(m, name)
                        if __func.__closure__:
                            for cell in __func.__closure__:
                                inner = cell.cell_contents
                                gmap = getattr(inner, "__globals__", None)
                                if gmap is not None:
                                    for name, val in list(gmap.items()):
                                        if hasattr(mod, name):
                                            gmap[name] = getattr(mod, name)
                                        elif hasattr(val, "__module__"):
                                            m = sys.modules.get(val.__module__)
                                            if m and hasattr(m, name):
                                                gmap[name] = getattr(m, name)
                    return __func(*a, **k)

                self.routes.setdefault(path, {})[method] = wrapper

    def test_client(self):
        app = self

        class Client:
            def __init__(self):
                self.application = app

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def open(self, path, method="GET", json=None):
                from urllib.parse import urlparse, parse_qs

                parsed = urlparse(path)
                route = parsed.path
                args = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
                flask_stub._request = types.SimpleNamespace(
                    args=args,
                    form={},
                    json=json,
                    method=method,
                    path=route,
                    headers={},
                    remote_addr="",
                    get_json=lambda: json,
                )
                flask_stub._current_app = app
                view = app.routes.get(route, {}).get(method)
                if not view:
                    return DummyResponse(status_code=404)
                return _result_to_response(view())

            def get(self, path, **kw):
                return self.open(path, "GET", **kw)

            def post(self, path, json=None, **kw):
                return self.open(path, "POST", json=json)

        return Client()


def jsonify(obj=None, **kwargs):
    return obj if obj is not None else kwargs


def render_template(name, **kwargs):
    import os
    import re

    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))

    def load(fname):
        path = os.path.join(base, fname)
        text = open(path, "r", encoding="utf-8").read()
        return re.sub(r"{% include \"(.*?)\" %}", lambda m: load(m.group(1)), text)

    return load(name)


flask_stub.Flask = DummyFlask
flask_stub.Blueprint = DummyBlueprint
flask_stub.jsonify = jsonify
flask_stub.render_template = render_template
class _RequestProxy:
    def __getattr__(self, name):
        return getattr(flask_stub._request, name)

flask_stub._request = types.SimpleNamespace()
flask_stub.request = _RequestProxy()

class _CurrentAppProxy:
    def __getattr__(self, name):
        return getattr(flask_stub._current_app, name)

flask_stub._current_app = types.SimpleNamespace()
flask_stub.current_app = _CurrentAppProxy()
flask_stub.redirect = lambda loc: loc
flask_stub.url_for = lambda endpoint, **kwargs: endpoint
flask_stub.flash = lambda *a, **k: None
sys.modules.setdefault("flask", flask_stub)

# Minimal jinja2 stubs for blueprint imports
if "jinja2" not in sys.modules:
    jinja2_stub = types.ModuleType("jinja2")
    jinja2_stub.ChoiceLoader = lambda *a, **k: None
    jinja2_stub.FileSystemLoader = lambda *a, **k: None
    sys.modules["jinja2"] = jinja2_stub

if "werkzeug.utils" not in sys.modules:
    werkzeug_utils_stub = types.ModuleType("werkzeug.utils")
    werkzeug_utils_stub.secure_filename = lambda name: name
    sys.modules["werkzeug.utils"] = werkzeug_utils_stub

# Minimal stubs for optional HTTP + Twilio dependencies
requests_stub = types.ModuleType("requests")
requests_stub.post = lambda *a, **k: types.SimpleNamespace(json=lambda: {}, raise_for_status=lambda: None)
sys.modules.setdefault("requests", requests_stub)

twilio_stub = types.ModuleType("twilio")
sys.modules.setdefault("twilio", twilio_stub)
twilio_rest_stub = types.ModuleType("twilio.rest")

class DummyTwilioMessage:
    def __init__(self, sid="SMxxxx"):
        self.sid = sid


class DummyTwilioClient:
    def __init__(self, *a, **k):
        class Messages:
            @staticmethod
            def create(body=None, from_=None, to=None):
                return DummyTwilioMessage()

        self.messages = Messages()

twilio_rest_stub.Client = DummyTwilioClient
sys.modules.setdefault("twilio.rest", twilio_rest_stub)
twilio_voice_stub = types.ModuleType("twilio.twiml.voice_response")
twilio_voice_stub.VoiceResponse = object
sys.modules.setdefault("twilio.twiml.voice_response", twilio_voice_stub)

playsound_stub = types.ModuleType("playsound")
playsound_stub.playsound = lambda *a, **k: None
sys.modules.setdefault("playsound", playsound_stub)

# Disable third-party plugin autoload to avoid missing deps
os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")


def pytest_configure(config):
    """Register the ``asyncio`` marker for tests."""
    config.addinivalue_line("markers", "asyncio: mark test to run using asyncio")


def pytest_pyfunc_call(pyfuncitem):
    """Run asyncio-marked tests via ``asyncio.run`` without pytest-asyncio."""
    if pyfuncitem.get_closest_marker("asyncio"):
        test_func = pyfuncitem.obj
        if asyncio.iscoroutinefunction(test_func):
            # Extract only arguments that the test function expects
            args = {
                name: pyfuncitem.funcargs[name]
                for name in pyfuncitem._fixtureinfo.argnames
            }
            asyncio.run(test_func(**args))
            return True

