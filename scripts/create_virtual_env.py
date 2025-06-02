#!/usr/bin/env python3
"""Create or update the project's ``.venv`` directory.

This script ensures a local Python virtual environment exists in ``.venv`` at
 the repository root. If the environment does not exist it is created using the
 currently running Python interpreter. Once created, ``pip`` is upgraded to the
 latest version.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_DIR = PROJECT_ROOT / ".venv"


def run(cmd: Sequence[str], cwd: Path | None = None) -> int:
    """Run ``cmd`` returning its exit code."""
    print(f"🔧 {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ command failed: {' '.join(cmd)}")
    return result.returncode


def venv_python() -> Path:
    """Return the path to the ``python`` executable inside ``.venv``."""
    scripts = "Scripts" if sys.platform == "win32" else "bin"
    exe = "python.exe" if sys.platform == "win32" else "python"
    return VENV_DIR / scripts / exe


def create_venv() -> int:
    if VENV_DIR.exists():
        print("✅ .venv already exists")
        return 0

    if sys.version_info < (3, 10):
        print("❌ Python 3.10 or later is required", file=sys.stderr)
        return 1

    print("Creating virtual environment…")
    result = run([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=PROJECT_ROOT)
    if result != 0:
        return result

    # Upgrade pip inside the new environment
    run([str(venv_python()), "-m", "pip", "install", "--upgrade", "pip"], cwd=PROJECT_ROOT)

    print("✅ .venv created")
    return 0


def main() -> int:
    return create_venv()


if __name__ == "__main__":
    raise SystemExit(main())
