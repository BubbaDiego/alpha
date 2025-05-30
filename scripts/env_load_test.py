#!/usr/bin/env python3
"""Simple script to verify .env loading.

This script loads environment variables from a ``.env`` file located at the
repository root (falling back to ``.env.example``) and prints the resulting
values. Use this to confirm that ``python-dotenv`` can locate and parse the
file correctly.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, dotenv_values


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    env_path = repo_root / ".env"
    if not env_path.exists():
        env_example = repo_root / ".env.example"
        if env_example.exists():
            env_path = env_example
        else:
            print("No .env or .env.example file found at repository root")
            return 1

    print(f"Loading environment from {env_path}")
    load_dotenv(env_path)
    values = dotenv_values(env_path)
    for key in sorted(values):
        print(f"{key}={os.getenv(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
