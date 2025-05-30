from pathlib import Path
from typing import List
import pytest
from test_core.test_core import TestCore


def test_run_glob_filters_virtual_envs(tmp_path, monkeypatch):
    # Set up directory structure with various test files
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "test_valid.py").write_text("")

    for d in [".venv", "venv", "site-packages"]:
        (tmp_path / d).mkdir()
        (tmp_path / d / "test_ignore.py").write_text("")

    captured: List[Path] = []

    def fake_run_files(self, files):
        captured.extend(files)

    tc = TestCore()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(TestCore, "run_files", fake_run_files)

    tc.run_glob("test_*.py")

    assert captured == [Path("sub/test_valid.py")]


def test_run_glob_skips_pycache_and_pyc(tmp_path, monkeypatch):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "test_cache.py").write_text("")
    (tmp_path / "test_ok.py").write_text("")
    (tmp_path / "test_skip.pyc").write_text("")

    captured: List[Path] = []

    def fake_run_files(self, files):
        captured.extend(files)

    tc = TestCore()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(TestCore, "run_files", fake_run_files)

    tc.run_glob("test*")

    assert captured == [Path("test_ok.py")]


def test_run_files_filters_non_py(tmp_path, monkeypatch):
    tc = TestCore(report_dir=tmp_path)
    (tmp_path / "good.py").write_text("print('ok')")
    (tmp_path / "bad.pyc").write_text("")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "cache.py").write_text("")

    captured_args = []

    def fake_pytest_main(args):
        captured_args.extend(args)
        return 0

    monkeypatch.setattr(TestCore, "_open_html_report", lambda self, p: None)
    monkeypatch.setattr("pytest.main", fake_pytest_main)

    tc.run_files([tmp_path / "good.py", tmp_path / "bad.pyc", tmp_path / "__pycache__" / "cache.py"])

    assert captured_args[0] == str(tmp_path / "good.py")
    assert len(captured_args) > 0 and str(tmp_path / "bad.pyc") not in captured_args
    assert str(tmp_path / "__pycache__" / "cache.py") not in captured_args
