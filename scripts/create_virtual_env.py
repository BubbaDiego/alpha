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


if __name__ == "__main__":
    raise SystemExit(main())
