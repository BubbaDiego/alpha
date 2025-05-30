#!/usr/bin/env python3
"""Run an end-to-end Playwright test using the Phantom wallet extension.

This script exercises the ``AutoCore`` automation helpers outside of pytest.
It simply deposits (or withdraws) a small amount of collateral on Jupiter
using Playwright with the Phantom extension loaded.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Ensure repository root is on the import path
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))



def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AutoCore E2E workflow with Playwright and Phantom"
    )
    parser.add_argument("--phantom-path", required=True, help="Path to Phantom extension")
    parser.add_argument(
        "--profile-dir",
        default="/tmp/playwright-profile",
        help="Persistent browser profile directory",
    )
    parser.add_argument(
        "--amount", type=float, default=0.01, help="Collateral amount to use"
    )
    parser.add_argument(
        "--withdraw", action="store_true", help="Run withdraw instead of deposit"
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run browser in headless mode"
    )
    parser.add_argument(
        "--extension-id",
        help="Phantom extension ID (required for headless popup handling)",
    )
    parser.add_argument("--user-agent", help="Optional custom user agent")
    parser.add_argument("--slow-mo", type=int, help="Slow motion delay in ms")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    try:
        from auto_core import AutoCore
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"Playwright/AutoCore unavailable: {exc}")
        return 1

    core = AutoCore(
        args.phantom_path,
        args.profile_dir,
        headless=args.headless,
        extension_id=args.extension_id,
        user_agent=args.user_agent,
        slow_mo=args.slow_mo,
    )

    if args.withdraw:
        core.withdraw_collateral(args.amount)
    else:
        core.deposit_collateral(args.amount)

    print("✅ E2E workflow completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
