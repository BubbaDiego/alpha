#!/usr/bin/env python3
"""Create a virtual environment for the project if it doesn't exist."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
VENV_PATH = PROJECT_ROOT / ".venv"


def main() -> int:
    if VENV_PATH.exists():
        print("✅ .venv already exists")
        return 0

    print("Creating virtual environment…")
    result = subprocess.run([sys.executable, "-m", "venv", str(VENV_PATH)])
    if result.returncode == 0:
        print("✅ .venv created")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

