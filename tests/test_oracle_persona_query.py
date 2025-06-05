import importlib
import importlib.util
import sys
import types
from pathlib import Path

import pytest

from flask import Flask


def load_blueprint():
    base = Path(__file__).resolve().parents[1]
    pkg = types.ModuleType("gpt")
    pkg.__path__ = [str(base / "gpt")]
    sys.modules.setdefault("gpt", pkg)

    path = base / "gpt" / "gpt_bp.py"
    spec = importlib.util.spec_from_file_location("gpt.gpt_bp", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module.gpt_bp


@pytest.fixture
def client():
    bp = load_blueprint()
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(bp)
    with app.test_client() as client:
        yield client


def test_oracle_query_with_persona(client):
    resp = client.post(
        "/gpt/oracle/query",
        json={"topic": "portfolio", "persona": "Wizard"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["reply"]["modifiers"]["distanceWeight"] == 0.6
