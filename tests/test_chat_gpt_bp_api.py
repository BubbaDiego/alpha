import importlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest

flask = importlib.import_module("flask")
if not getattr(flask, "Flask", None):
    pytest.skip("Flask not available", allow_module_level=True)
from flask import Flask


def load_module():
    base = Path(__file__).resolve().parents[1] / "gpt"
    pkg = types.ModuleType("gpt")
    pkg.__path__ = [str(base)]
    sys.modules.setdefault("gpt", pkg)
    path = base / "chat_gpt_bp.py"
    spec = importlib.util.spec_from_file_location("gpt.chat_gpt_bp", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_chat_post_returns_503_when_no_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPEN_AI_KEY", raising=False)
    module = load_module()
    assert module.client is None

    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(module.chat_gpt_bp)
    with app.test_client() as client:
        resp = client.post("/GPT/chat", json={"message": "hi"})
        assert resp.status_code == 503
        data = resp.get_json()
        assert "error" in data

