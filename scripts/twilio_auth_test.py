#!/usr/bin/env python3
"""Simple Twilio authentication test script.

Usage:
    python scripts/twilio_auth_test.py --sid <ACCOUNT_SID> --token <AUTH_TOKEN>

If --sid or --token are omitted, the script will try to use the
TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.
"""

import argparse
import os
import sys

__test__ = False
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except Exception:  # pragma: no cover - optional dependency
    Client = None
    class TwilioRestException(Exception):
        pass
import requests


def test_twilio_auth(account_sid: str, auth_token: str) -> int:
    """Attempts to authenticate with Twilio and prints detailed results."""
    try:
        client = Client(account_sid, auth_token)
        account = client.api.accounts(account_sid).fetch()
        print("✅ Authentication succeeded")
        print(f"Account SID: {account.sid}")
        print(f"Friendly Name: {account.friendly_name}")
        return 0
    except TwilioRestException as exc:
        print("❌ Authentication failed")
        print(f"HTTP Status: {exc.status}")
        print(f"Error Code: {exc.code}")
        print(f"Message: {exc.msg}")
        if exc.more_info:
            print(f"More Info: {exc.more_info}")
        return 1
    except requests.exceptions.RequestException as exc:
        print("❌ Network error while contacting Twilio")
        print(str(exc))
        return 1
    except Exception as exc:
        print("❌ Unexpected error")
        print(str(exc))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Twilio credentials")
    parser.add_argument("--sid", help="Twilio Account SID")
    parser.add_argument("--token", help="Twilio Auth Token")
    args = parser.parse_args()

    sid = args.sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = args.token or os.getenv("TWILIO_AUTH_TOKEN")

    if not sid or not token:
        print("Account SID and Auth Token are required")
        return 1

    return test_twilio_auth(sid, token)


if __name__ == "__main__":
    sys.exit(main())
