import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import tempfile
from system.theme_service import ThemeService
from unittest.mock import MagicMock
import pytest

@pytest.fixture
def dl():
    mock = MagicMock()
    mock.system.get_theme_mode.return_value = "dark"
    mock.system.set_theme_mode.return_value = None
    return mock

@pytest.fixture
def config_path(tmp_path):
    path = tmp_path / "theme.json"
    path.write_text('{"bg": "#ffffff", "fg": "#000000"}')
    return str(path)

def test_get_theme_mode_success(dl):
    service = ThemeService(dl)
    mode = service.get_theme_mode()
    assert mode == "dark"
    return "✅ get_theme_mode passed"

def test_set_theme_mode_success(dl):
    service = ThemeService(dl)
    service.set_theme_mode("light")
    dl.system.set_theme_mode.assert_called_with("light")
    return "✅ set_theme_mode passed"

def test_load_theme_config_exists(dl, config_path):
    service = ThemeService(dl, config_path=config_path)
    config = service.load_theme_config()
    assert config["bg"] == "#ffffff"
    return "✅ load_theme_config (exists) passed"

def test_load_theme_config_missing(dl):
    service = ThemeService(dl, config_path="missing_config.json")
    config = service.load_theme_config()
    assert config == {}
    return "✅ load_theme_config (missing) passed"

def test_save_theme_config(dl):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        config_path = tmp.name

    try:
        service = ThemeService(dl, config_path=config_path)
        new_config = {"bg": "#111111", "fg": "#222222"}
        service.save_theme_config(new_config)

        with open(config_path) as f:
            loaded = json.load(f)

        assert loaded == new_config
        return "✅ save_theme_config passed"
    finally:
        os.remove(config_path)


if __name__ == "__main__":
    print("🚀 Self-running ThemeService Test Suite")

    # Mocked data_locker system interface
    mock_dl = MagicMock()
    mock_dl.system.get_theme_mode.return_value = "dark"
    mock_dl.system.set_theme_mode.return_value = None

    # Write temp config file
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp:
        json.dump({"bg": "#ffffff", "fg": "#000000"}, tmp)
        config_path = tmp.name

    # Run tests
    results = []
    try:
        results.append(test_get_theme_mode_success(mock_dl))
        results.append(test_set_theme_mode_success(mock_dl))
        results.append(test_load_theme_config_exists(mock_dl, config_path))
        results.append(test_load_theme_config_missing(mock_dl))
        results.append(test_save_theme_config(mock_dl))
    except AssertionError as e:
        results.append(f"❌ TEST FAILED: {str(e)}")
    finally:
        os.remove(config_path)

    print("\n".join(results))
