#!/usr/bin/env python3
"""Run Twilio authentication and optional flow using environment variables.

This script loads credentials and flow parameters from environment variables or
an optional `.env` file at the repository root. It then delegates to
`scripts.twilio_test` to perform authentication and optionally trigger a
Twilio Studio Flow.

Expected environment variables:
    TWILIO_ACCOUNT_SID   - Twilio Account SID
    TWILIO_AUTH_TOKEN    - Twilio Auth Token
    TWILIO_FLOW_SID      - (optional) Studio Flow SID
    TWILIO_FROM_PHONE    - (optional) From phone number
    TWILIO_TO_PHONE      - (optional) To phone number
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from typing import List

# Make sure we can import scripts.twilio_test when executed from repo root
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from twilio_test import main as twilio_test_main


def build_argv() -> List[str]:
    """Construct argument list for ``twilio_test.main`` from environment."""
    argv: List[str] = []
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    flow_sid = os.getenv("TWILIO_FLOW_SID")
    from_phone = os.getenv("TWILIO_FROM_PHONE")
    to_phone = os.getenv("TWILIO_TO_PHONE")

    if sid:
        argv += ["--sid", sid]
    if token:
        argv += ["--token", token]
    if flow_sid:
        argv += ["--flow-sid", flow_sid]
    if from_phone:
        argv += ["--from-phone", from_phone]
    if to_phone:
        argv += ["--to-phone", to_phone]
    return argv


def main() -> int:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    argv = build_argv()
    return twilio_test_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
