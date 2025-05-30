import json
import importlib.util
from pathlib import Path
import types
import sys


class DummyCore:
    def build_payload(self, instructions: str = "") -> dict:
        return {"test": True, "instructions_for_ai": instructions or "default"}


def load_module():
    base = Path(__file__).resolve().parents[1] / "gpt"
    # Create dummy gpt package
    pkg = types.ModuleType("gpt")
    sys.modules.setdefault("gpt", pkg)

    ctx_path = base / "context_loader.py"
    ctx_spec = importlib.util.spec_from_file_location("gpt.context_loader", ctx_path)
    ctx_mod = importlib.util.module_from_spec(ctx_spec)
    assert ctx_spec and ctx_spec.loader
    ctx_spec.loader.exec_module(ctx_mod)
    sys.modules["gpt.context_loader"] = ctx_mod
    setattr(pkg, "context_loader", ctx_mod)

    path = base / "create_gpt_context_service.py"
    spec = importlib.util.spec_from_file_location("gpt.create_gpt_context_service", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    sys.modules["gpt.create_gpt_context_service"] = module
    return module


def test_create_analysis_context(monkeypatch):
    mod = load_module()
    core = DummyCore()
    messages = mod.create_gpt_context_service(core, "analysis", "inspect")
    assert messages[0]["role"] == "system"
    payload = json.loads(messages[1]["content"])
    assert payload["test"] is True
    assert payload["instructions_for_ai"] == "inspect"


def test_create_portfolio_context(monkeypatch):
    mod = load_module()
    core = DummyCore()

    def fake_context_messages():
        return [{"role": "system", "content": "ctx"}]

    monkeypatch.setattr(mod, "get_context_messages", fake_context_messages)
    messages = mod.create_gpt_context_service(core, "portfolio", "summary")
    assert messages[0]["role"] == "system"
    assert messages[-1]["content"] == "summary"
