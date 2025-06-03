#!/usr/bin/env python3
"""Bootstrap a fresh tree setup.

This helper installs dependencies, seeds the database with default
thresholds and wallets, ensures a ``.env`` file is present and then runs
``StartUpService.run_all()`` to verify the environment. Use it when
cloning the project on a new machine.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utils.startup_service import StartUpService


def ensure_virtualenv() -> None:
    """Exit if no virtual environment is active."""
    active = os.environ.get("VIRTUAL_ENV") or sys.prefix != sys.base_prefix
    if not active:
        raise SystemExit("❌ Activate a virtual environment before running this script")


def run(cmd: str) -> None:
    """Execute ``cmd`` and exit on failure."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def ensure_requirements() -> None:
    """Install packages from ``requirements.txt``."""
    req = REPO_ROOT / "requirements.txt"
    if not req.exists():
        raise SystemExit("requirements.txt not found")
    cmd = f"{sys.executable} -m pip install -r \"{req}\""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(
            "❌ Failed to install dependencies. "
            "Ensure you are using Python 3.10+ and try upgrading pip with"
        )
        print(f"   {sys.executable} -m pip install --upgrade pip")
        raise SystemExit(result.returncode)


def seed_database() -> None:
    """Initialize the DB and seed default data."""
    init = SCRIPT_DIR / "initialize_database.py"
    if init.exists():
        run(f"{sys.executable} {init} --reset --all")
    insert = SCRIPT_DIR / "insert_wallets.py"
    if insert.exists():
        run(f"{sys.executable} {insert}")


def ensure_env_file() -> None:
    """Create ``.env`` from the example if missing."""
    env = REPO_ROOT / ".env"
    example = REPO_ROOT / ".env.example"
    if not env.exists() and example.exists():
        env.write_text(example.read_text())
        print("📄 Created .env from .env.example")


def new_tree_protocol() -> None:
    """Run all setup steps for a new installation."""
    ensure_virtualenv()
    ensure_requirements()
    seed_database()
    ensure_env_file()
    StartUpService.run_all(play_sound=False)
    print("✅ New tree setup complete.")


if __name__ == "__main__":
    new_tree_protocol()
