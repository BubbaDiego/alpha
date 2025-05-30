#!/usr/bin/env python3
"""Twilio test script for authentication and optional Studio Flow trigger."""

import argparse
__test__ = False
import os
import sys
from typing import Optional, List

import requests
try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
except Exception:  # pragma: no cover - optional dependency
    Client = None
    class TwilioRestException(Exception):
        pass


def authenticate(account_sid: str, auth_token: str) -> Client:
    """Return a Twilio client if credentials are valid, else raise."""
    client = Client(account_sid, auth_token)
    client.api.accounts(account_sid).fetch()
    return client


def trigger_flow(client: Client, flow_sid: str, from_phone: str, to_phone: str) -> None:
    """Trigger a Twilio Studio Flow."""
    client.studio.v2.flows(flow_sid).executions.create(from_=from_phone, to=to_phone)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Test Twilio credentials and optionally trigger a flow")
    parser.add_argument("--sid", help="Twilio Account SID")
    parser.add_argument("--token", help="Twilio Auth Token")
    parser.add_argument("--flow-sid", help="Studio Flow SID")
    parser.add_argument("--from-phone", help="From phone number")
    parser.add_argument("--to-phone", help="To phone number")
    args = parser.parse_args(argv)

    sid = args.sid or os.getenv("TWILIO_ACCOUNT_SID")
    token = args.token or os.getenv("TWILIO_AUTH_TOKEN")

    if not sid or not token:
        print("Account SID and Auth Token are required")
        return 1

    try:
        client = authenticate(sid, token)
        print("✅ Authentication succeeded")
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

    if args.flow_sid and args.from_phone and args.to_phone:
        try:
            trigger_flow(client, args.flow_sid, args.from_phone, args.to_phone)
            print("✅ Flow triggered")
        except TwilioRestException as exc:
            print("❌ Failed to trigger flow")
            print(f"HTTP Status: {exc.status}")
            print(f"Error Code: {exc.code}")
            print(f"Message: {exc.msg}")
            if exc.more_info:
                print(f"More Info: {exc.more_info}")
            return 1
        except Exception as exc:
            print("❌ Unexpected error triggering flow")
            print(str(exc))
            return 1
    elif args.flow_sid:
        print("Flow SID provided without from/to phone numbers; skipping flow trigger")

    return 0


if __name__ == "__main__":
    sys.exit(main())
