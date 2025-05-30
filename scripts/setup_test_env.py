#!/usr/bin/env python
"""Install project dependencies for the test suite."""
from pathlib import Path
import subprocess
import sys


def main() -> None:
    req_file = Path(__file__).resolve().parents[1] / "requirements.txt"
    if not req_file.exists():
        print("requirements.txt not found", file=sys.stderr)
        sys.exit(1)
    print(f"Installing dependencies from {req_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
    except Exception as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
