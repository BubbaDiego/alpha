import os
from typing import Dict

from flask import current_app
from twilio.rest import Client

from core.logging import log
from .voice_service import VoiceService


class CheckTwilioHeartbeatService:
    """Verify Twilio credentials and optionally place a test voice call."""

    def __init__(self, config: Dict):
        self.config = config or {}

    def _load_creds(self):
        account_sid = self.config.get("account_sid") or os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = self.config.get("auth_token") or os.getenv("TWILIO_AUTH_TOKEN")
        from_phone = self.config.get("default_from_phone") or os.getenv("TWILIO_FROM_PHONE")
        to_phone = self.config.get("default_to_phone") or os.getenv("TWILIO_TO_PHONE")
        return account_sid, auth_token, from_phone, to_phone

    def check(self, dry_run: bool = True) -> Dict:
        """Return dict with success status and whether a call was placed."""
        result = {"success": False, "call_placed": False}
        account_sid, auth_token, from_phone, to_phone = self._load_creds()
        try:
            if not account_sid or not auth_token:
                raise Exception("Missing Twilio credentials")

            client = Client(account_sid, auth_token)
            client.api.accounts(account_sid).fetch()

            if not dry_run:
                if not from_phone or not to_phone:
                    raise Exception("Missing from/to phone numbers")
                VoiceService(self.config).call(to_phone, "XCom heartbeat check")
                result["call_placed"] = True

            result["success"] = True
        except Exception as exc:
            log.error(f"Twilio heartbeat failed: {exc}", source="CheckTwilioHeartbeatService")
            if hasattr(current_app, "system_core"):
                current_app.system_core.death(
                    {
                        "message": f"Twilio heartbeat failure: {exc}",
                        "payload": {"provider": "twilio"},
                        "level": "HIGH",
                    }
                )
            result["error"] = str(exc)
        return result
