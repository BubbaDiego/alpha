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
flask_stub.current_app = types.SimpleNamespace()
sys.modules.setdefault("flask", flask_stub)

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

