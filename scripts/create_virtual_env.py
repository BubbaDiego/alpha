
from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    venv_dir = repo_root / ".venv"
    if venv_dir.exists():
        print("✅ .venv already exists")
        return 0

    print("Creating virtual environment...")
    result = subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=repo_root)
    if result.returncode != 0:
        print("❌ Failed to create .venv")
        return result.returncode

    print("✅ .venv created")
    return 0

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

